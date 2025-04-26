from flask import Flask, request, render_template_string, session
import datetime
import random
import math
import json
import os
import requests
from urllib.parse import quote

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this to a secure random key

class PydroidChatBot:
    def __init__(self):
        self.jokes = [
            "Why don't scientists trust atoms? They make up everything!",
            "Parallel lines have so much in common... it's a shame they'll never meet.",
            "I told my computer I needed a break... now it won't stop sending me vacation ads."
        ]
        self.fun_facts = [
            "Octopuses have three hearts and blue blood.",
            "Honey never spoils - edible after 3000 years!",
            "Venus has a day longer than its year."
        ]
        self.web_services = {
            'g': 'https://www.google.com/search?q=',
            'google': 'https://www.google.com/search?q=',
            'w': 'https://en.wikipedia.org/wiki/',
            'wikipedia': 'https://en.wikipedia.org/wiki/',
            'yt': 'https://www.youtube.com/results?search_query=',
            'youtube': 'https://www.youtube.com/results?search_query=',
            'ddg': 'https://duckduckgo.com/?q=',
            'duckduckgo': 'https://duckduckgo.com/?q='
        }

    def respond(self, user_input):
        user_input = user_input.lower().strip()

        if user_input in ['hello', 'hi']:
            return "Hello! How can I help you?"
        elif 'how are you' in user_input:
            return "I am fine, thanks for asking."
        elif 'what is your name' in user_input:
            return "My name is PydroidBot."
        elif 'who created you' in user_input:
            return "I was created by Vijay Chockalingam."
        elif 'time' in user_input:
            return datetime.datetime.now().strftime("%I:%M %p")
        elif 'date' in user_input:
            return datetime.datetime.now().strftime("%B %d, %Y")
        elif 'joke' in user_input:
            return random.choice(self.jokes)
        elif 'fact' in user_input:
            return random.choice(self.fun_facts)
        elif user_input.startswith('math '):
            expr = user_input[5:]
            try:
                return str(eval(expr))
            except:
                return "I can't solve that."
        elif user_input.startswith('search '):
            parts = user_input[7:].split(' ', 1)
            if len(parts) == 2:
                service, query = parts
                if service in self.web_services:
                    url = self.web_services[service] + quote(query)
                    return f'<a href="{url}" target="_blank">Click to search: {query}</a>'
                else:
                    return "Unknown service. Use google/wikipedia/youtube etc."
            else:
                return "Usage: search [service] [query]"
        elif user_input.startswith('ask '):
            prompt = user_input[4:]
            return self.ask_deepseek(prompt)
        elif user_input.startswith('weather '):
            location = user_input[8:]
            return self.get_weather(location)
        elif user_input in ['bye', 'exit']:
            return "Goodbye!"
        elif user_input == 'clear':
            return "CLEAR_HISTORY"  # Special keyword to clear history
        else:
            return "Sorry, I didn't understand that. Try 'help'."

    def get_weather(self, location):
        try:
            url = f"https://wttr.in/{location}?format=%C+%t"
            response = requests.get(url)
            return f"Weather in {location}: {response.text.strip()}"
        except:
            return "Weather service unavailable."

    def ask_deepseek(self, prompt):
        memory_file = "ask_memory.json"
        try:
            if os.path.exists(memory_file):
                with open(memory_file, "r") as f:
                    memory = json.load(f)
            else:
                memory = {}
        except:
            memory = {}

        if prompt in memory:
            return f"(From Memory) {memory[prompt]}"
        api_key ="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"  # Replace with your key
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "deepseek/deepseek-r1-zero:free",
            "messages": [{"role": "user", "content": prompt}]
        }

        try:
            response = requests.post(url, headers=headers, data=json.dumps(data))
            if response.status_code == 200:
                answer = response.json()['choices'][0]['message']['content']
                memory[prompt] = answer
                with open(memory_file, "w") as f:
                    json.dump(memory, f, indent=4)
                return answer
            else:
                return f"Error: {response.status_code}"
        except Exception as e:
            return f"Exception: {e}"

bot = PydroidChatBot()

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>PydroidChatBot</title>
    <style>
        body { 
            font-family: Arial; 
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        #chat-container {
            border: 1px solid #ddd;
            border-radius: 5px;
            height: 400px;
            overflow-y: auto;
            margin-bottom: 15px;
            padding: 10px;
            background: #f9f9f9;
        }
        .user-message {
            text-align: right;
            margin: 5px;
            padding: 8px 12px;
            background: #e3f2fd;
            border-radius: 10px;
            display: inline-block;
            max-width: 70%;
            word-wrap: break-word;
        }
        .bot-message {
            text-align: left;
            margin: 5px;
            padding: 8px 12px;
            background: #f1f1f1;
            border-radius: 10px;
            display: inline-block;
            max-width: 70%;
            word-wrap: break-word;
        }
        #input-form {
            display: flex;
            gap: 10px;
        }
        #message-input {
            flex-grow: 1;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
        }
        #submit-button {
            padding: 10px 20px;
            background: #4CAF50;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
        .clear-btn {
            background: #f44336;
            color: white;
            border: none;
            padding: 5px 10px;
            border-radius: 3px;
            cursor: pointer;
            margin-top: 10px;
        }
    </style>
</head>
<body>
    <h2>PydroidChatBot</h2>
    <div id="chat-container">
        {% for message in chat_history %}
            {% if message.sender == 'user' %}
                <div class="user-message"><b>You:</b> {{ message.text|safe }}</div><br>
            {% else %}
                <div class="bot-message"><b>Bot:</b> {{ message.text|safe }}</div><br>
            {% endif %}
        {% endfor %}
    </div>
    <form id="input-form" method="post">
        <input type="text" id="message-input" name="message" placeholder="Type your message..." required />
        <input type="submit" id="submit-button" value="Send" />
    </form>
    <form method="post">
        <input type="hidden" name="message" value="clear" />
        <button type="submit" class="clear-btn">Clear Chat</button>
    </form>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    # Initialize chat history in session if not exists
    if 'chat_history' not in session:
        session['chat_history'] = []
    
    if request.method == 'POST':
        user_input = request.form['message']
        
        if user_input == 'clear':
            session['chat_history'] = []
            return render_template_string(HTML_PAGE, chat_history=session['chat_history'])
        
        # Add user message to history
        session['chat_history'].append({'sender': 'user', 'text': user_input})
        
        # Get bot response
        bot_response = bot.respond(user_input)
        
        # Add bot response to history
        if bot_response != "CLEAR_HISTORY":
            session['chat_history'].append({'sender': 'bot', 'text': bot_response})
        else:
            session['chat_history'] = []
        
        # Save the modified session
        session.modified = True
    
    return render_template_string(HTML_PAGE, chat_history=session['chat_history'])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)