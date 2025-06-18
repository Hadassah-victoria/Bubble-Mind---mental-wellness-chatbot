from flask import Flask, render_template, request, jsonify, send_file
import requests
from io import BytesIO
import os
from dotenv import load_dotenv
load_dotenv()


app = Flask(__name__)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = "llama-3.1-8b-instant"
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
VOICE_ID = os.getenv("VOICE_ID")  # Replace with ID

@app.route('/speak', methods=['POST'])
def speak():
    data = request.get_json()
    text = data.get('text')

    if not text:
        return jsonify({"error": "No text provided"}), 400

    # Send request to ElevenLabs API
    response = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}",
        headers={
            "xi-api-key": ELEVENLABS_API_KEY,
            "Content-Type": "application/json"
        },
        json={
            "text": text,
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75
            }
        }
    )
    
     # 🔥 Debug: print status and response
    print("Status code:", response.status_code)
    print("Response body:", response.text)

    if response.status_code != 200:
        return jsonify({"error": "Failed to generate voice"}), 500

    # Return audio file to frontend
    return send_file(BytesIO(response.content), mimetype="audio/mpeg")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json["message"]
    prompt = f"""
You are Bubble Mind, a friendly and emotionally intelligent AI friend whose only job is to help users with their feelings, mood, and mental well-being.. 
Always talk like a supportive and caring companion.

💖 Your Rules:
- ONLY answer questions related to emotional support, mental health, mood, feelings, or motivation.
- If a user asks a question unrelated to mental health (like general knowledge, coding, geography, or news), kindly say:
  👉 "I'm here just to support your emotional well-being 💛. Let's talk about *you*. How are you feeling today?"

🧠 Your Personality(Here’s how to behave):
- If the user seems cheerful, casual, or fine — just respond like a normal friendly conversation.
- If the user seems upset, anxious, or sad — gently check in with short, warm questions like: 
  "Are you okay?", "Is something going on?", or "Want to talk about it?".
- Don’t force users to open up.
- Keep replies short and friendly, like a real friend chatting.
- Don’t be overly wordy or formal.
- Never give medical advice or diagnose anything.

💬 Example:
If user asks: "What is Python?"
You should reply: "Aww, I’m not really into tech stuff 😅 — I’m just here to vibe with your feelings. What’s on your mind today?"

Respond with emotional awareness based on this user input:
"{user_message}"
"""


    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    body = {
        "model": GROQ_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=body
        )
        print("Groq API Response:", response.text)  # Debug line
        response.raise_for_status()
        reply = response.json()["choices"][0]["message"]["content"]
        return jsonify({"reply": reply})
    except Exception as e:
        print("Error:", e)
        return jsonify({"reply": "Sorry, I'm having trouble connecting to the wellness center. Please try again later."})

if __name__ == "__main__":
    app.run(debug=True)





