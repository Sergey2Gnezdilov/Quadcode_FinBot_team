from flask import Flask, request, render_template_string
from trade_agent import GPTAssistant  # Make sure to update the import path if necessary

app = Flask(__name__)
assistant = GPTAssistant()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>📈 FinBot</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            background-color: #f4f4f9;
        }
        #chat-container {
            width: 80%;
            max-width: 600px;
            margin: auto;
            border: 1px solid #ccc;
            background-color: #fff;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            display: flex;
            flex-direction: column;
            height: 70vh;
            border-radius: 8px;
            overflow: hidden;
        }
        #chat {
            flex-grow: 1;
            padding: 20px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 10px;
        }
        .message {
            padding: 10px 20px;
            border-radius: 20px;
            color: white;
            max-width: 70%;
        }
        .user {
            background-color: #007bff;
            align-self: flex-end;
        }
        .bot {
            background-color: #333;
            align-self: flex-start;
        }
        #input-area {
            border-top: 1px solid #ccc;
            padding: 10px;
            display: flex;
        }
        #user_input {
            flex-grow: 1;
            padding: 10px;
            border: 1px solid #ccc;
            border-radius: 20px;
            outline: none;
        }
        button {
            padding: 10px 20px;
            border: none;
            background-color: #007bff;
            color: white;
            border-radius: 20px;
            cursor: pointer;
        }
        button:hover {
            background-color: #0056b3;
        }
    </style>
</head>
<body>
    <div id="chat-container">
        <div id="chat"></div>
        <div id="input-area">
            <input type="text" id="user_input" placeholder="Type your message here..." onkeypress="if(event.keyCode == 13) { sendMessage(); }">
            <button onclick="sendMessage()">Send</button>
        </div>
    </div>

    <script>
        function sendMessage() {
            var input = document.getElementById('user_input');
            var chat = document.getElementById('chat');
            if(input.value.trim() !== '') {
                var userDiv = document.createElement('div');
                userDiv.textContent = input.value;
                userDiv.className = 'message user';
                chat.appendChild(userDiv);
                chat.scrollTop = chat.scrollHeight;

                fetch('/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({user_input: input.value})
                })
                .then(response => response.json())
                .then(data => {
                    var botDiv = document.createElement('div');
                    botDiv.textContent = data.response;
                    botDiv.className = 'message bot';
                    chat.appendChild(botDiv);
                    chat.scrollTop = chat.scrollHeight; // Scroll to latest message
                });

                input.value = ''; // Clear input box after sending
            }
        }
    </script>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        user_input = request.json['user_input']
        response = assistant.conversation(user_input)
        return {'response': response}
    return render_template_string(HTML_TEMPLATE, response=None)

if __name__ == '__main__':
    app.run(debug=True)
