from flask import Flask, render_template, request, jsonify
import requests
import json

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat')
def chat():
    return render_template('chat.html')

@app.route('/get_response', methods=['POST'])
def get_response():
    data = request.json
    if not data or 'message' not in data:
        return jsonify({'response': 'Invalid request.', 'source': 'system'})
    
    user_message = data.get('message', '').strip()
    if not user_message:
        return jsonify({'response': 'Please enter a message.', 'source': 'system'})

    try:
        # 🔹 Send message to Ollama (running locally)
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "mistral", "prompt": user_message, "max_tokens": 300},
            stream=True
        )

        full_text = ""
        for line in response.iter_lines():
            if line:
                try:
                    chunk = json.loads(line.decode("utf-8"))
                    if "response" in chunk:
                        full_text += chunk["response"]
                except json.JSONDecodeError:
                    continue

        bot_reply = full_text.strip() if full_text else "Sorry, I couldn't generate a response."

    except Exception as e:
        print("Ollama error:", e)
        bot_reply = "I'm having trouble connecting to my language model. Please ensure Ollama is running."

    return jsonify({'response': bot_reply, 'source': 'ollama'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
