from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import requests
import json

app = Flask(__name__)
app.secret_key = "supersecretkey"

users = {}  # Temporary storage (replace with database later)

SYSTEM_PROMPT = """
You are FamilyCare — an expert AI assistant specializing in family planning,
reproductive health, and contraceptive methods.

Your job is to answer user questions clearly, kindly, and accurately.

Rules:
•⁠  ⁠Focus only on family planning, contraception, sexual and reproductive health.
•⁠  ⁠If a question is off-topic, politely say it’s outside your scope.
•⁠  ⁠Use short, friendly sentences.


Example:
User: What is an IUD?
Answer: An intrauterine device (IUD) is a small, T-shaped contraceptive inserted into the uterus to prevent pregnancy.
"""


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat')
def chat():
    return render_template('chat.html', username=session.get('user'))

# @app.route('/get_response', methods=['POST'])
# def get_response():
#     data = request.json
#     if not data or 'message' not in data:
#         return jsonify({'response': 'Invalid request.', 'source': 'system'})
    
#     user_message = data.get('message', '').strip()
#     language = data.get('language', 'english')
#     if not user_message:
#         return jsonify({'response': 'Please enter a message.', 'source': 'system'})
    
#     try:
#         language_instruction = "IMPORTANT: Respond in " + {"Nepali" if language == 'nepali' else 'English'} +" ."
#         full_prompt = f"{SYSTEM_PROMPT}\n\n{language_instruction}\n\nUser: {user_message}\nAssistant:"

#         response = requests.post(
#             "https://localhost:11434/api/generate",
#             json={"model": "mistral", "prompt": full_prompt, "max_tokens":300},
#         )

#         full_text = ""
#         for line in response.iter_lines():
#             if line:
#                 try:
#                     chunk = json.loads(line.decode("utf-8"))
#                     if "response" in chunk:
#                         full_text += chunk["response"]
#                 except json.JSONDecodeError:
#                     continue

#         bot_reply = full_text.strip() if full_text else "Sorry. I couldn't generate a response."

#     except Exception as e:
#         print("Ollama error:", e)
#         bot_reply = "I'm having trouble connecting to my language model. Please ensure ollama is running."

#     return jsonify({"response": bot_reply, 'source': 'ollama'})

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users:
            return render_template('signup.html', error="Username already exists!")

        users[username] = password
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if users.get(username) == password:
            session['user'] = username
            return redirect(url_for('chat'))
        else:
            return render_template('login.html', error="Invalid username or password.")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

@app.route('/get_response', methods=['POST'])
def get_response():
    data = request.json
    if not data or 'message' not in data:
        return jsonify({'response': 'Invalid request.'})

    user_message = data.get('message', '').strip()
    if not user_message:
        return jsonify({'response': 'Please enter a message.'})

    try:
        full_prompt = f"{SYSTEM_PROMPT}\n\nUser: {user_message}\nAssistant:"
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "mistral", "prompt": full_prompt, "max_tokens": 300},
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

    return jsonify({'response': bot_reply})

if __name__ == '__main__':
    app.run(debug=True)
