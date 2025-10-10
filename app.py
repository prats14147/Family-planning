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
    if not data:
        return jsonify({'response': 'Invalid request.', 'source': 'system'})
    
    user_message = data.get('message', '').lower().strip()
    language = data.get('language', 'english').lower()
    
    if not user_message:
        return jsonify({'response': 'Please enter a message.', 'source': 'system'})
    
    if language not in ['english', 'nepali']:
        language = 'english'
    
    response = None
    source = 'static'
    
    english_keywords = ['latest', 'recent', 'update', 'new', 'current']
    nepali_keywords = ['नवीनतम', 'हालै', 'ताजा', 'नयाँ', 'हालको']
    
    if any(keyword in user_message for keyword in english_keywords + nepali_keywords):
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
        api_url = "https://health.gov/myhealthfinder/api/v3/topicsearch.json?lang=en"
        
        response = requests.get(api_url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            
            if data and 'Result' in data and 'Resources' in data['Result']:
                resources = data['Result']['Resources'].get('Resource', [])
                if resources and len(resources) > 0:
                    resource = resources[0]
                    title = resource.get('Title', 'Health Information')
                    
                    if language == 'english':
                        return f"Latest Health Information: {title}. For the most current family planning information, visit WHO (www.who.int) or your local health department. (From live data source)"
                    else:
                        return f"नवीनतम स्वास्थ्य जानकारी: {title}. नवीनतम परिवार नियोजन जानकारीको लागि WHO (www.who.int) वा आफ्नो स्थानीय स्वास्थ्य विभाग भ्रमण गर्नुहोस्। (प्रत्यक्ष डेटा स्रोतबाट)"
    except Exception as e:
        print(f"API Error: {e}")
    
    if language == 'english':
        return "For the latest family planning information and updates, please visit the World Health Organization (WHO) at www.who.int or contact your local health department. (Recommended resources)"
    else:
        return "नवीनतम परिवार नियोजन जानकारी र अद्यावधिकका लागि, कृपया विश्व स्वास्थ्य संगठन (WHO) www.who.int मा जानुहोस् वा आफ्नो स्थानीय स्वास्थ्य विभागलाई सम्पर्क गर्नुहोस्। (सिफारिस गरिएका स्रोतहरू)"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
