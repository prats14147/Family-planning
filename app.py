from flask import Flask, render_template, request, jsonify
import json
import requests
from difflib import get_close_matches

app = Flask(__name__)

with open('chatbot_data.json', 'r', encoding='utf-8') as file:
    chatbot_data = json.load(file)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat')
def chat():
    return render_template('chat.html')

@app.route('/get_response', methods=['POST'])
def get_response():
    data = request.json
    user_message = data.get('message', '').lower().strip()
    language = data.get('language', 'english').lower()
    
    if not user_message:
        return jsonify({'response': 'Please enter a message.', 'source': 'system'})
    
    if language not in ['english', 'nepali']:
        language = 'english'
    
    response = None
    source = 'static'
    
    if any(keyword in user_message for keyword in ['latest', 'recent', 'update', 'new', 'current']):
        live_data = fetch_live_health_data(user_message, language)
        if live_data:
            response = live_data
            source = 'live'
    
    if not response:
        language_data = chatbot_data.get(language, {})
        
        if user_message in language_data:
            response = language_data[user_message]
        else:
            matches = get_close_matches(user_message, language_data.keys(), n=1, cutoff=0.6)
            if matches:
                response = language_data[matches[0]]
    
    if not response:
        if language == 'english':
            response = "I'm sorry, I don't have information about that. Could you please rephrase your question or ask about family planning methods, benefits, safety, or services?"
        else:
            response = "माफ गर्नुहोस्, मसँग यस बारे जानकारी छैन। कृपया आफ्नो प्रश्न अर्को तरिकाले सोध्नुहोस् वा परिवार नियोजन विधि, फाइदा, सुरक्षा, वा सेवाहरूको बारेमा सोध्नुहोस्।"
    
    return jsonify({'response': response, 'source': source})

def fetch_live_health_data(query, language):
    try:
        api_url = "https://api.api-ninjas.com/v1/healthnews"
        headers = {'X-Api-Key': 'demo'}
        
        response = requests.get(api_url, headers=headers, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            
            if data and isinstance(data, list) and len(data) > 0:
                article = data[0]
                title = article.get('title', 'No title')
                description = article.get('description', 'No description available')
                
                if language == 'english':
                    return f"Latest Health Information: {title}. {description} (From live data source)"
                else:
                    return f"नवीनतम स्वास्थ्य जानकारी: {title}. {description} (प्रत्यक्ष डेटा स्रोतबाट)"
    except Exception as e:
        print(f"API Error: {e}")
    
    return None

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
