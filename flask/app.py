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
            font-family: 'Arial', sans-serif; 
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            background-color: #121212; /* Dark background */
        }
        #chat-container {
            width: 80%;
            max-width: 600px;
            margin: auto;
            border: 1px solid #333; /* Darker border for dark mode */
            background-color: #1e1e1e; /* Dark background for the chat container */
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.5);
            display: flex;
            flex-direction: column;
            height: 70vh;
            border-radius: 8px;
            overflow: hidden;
        }
        #chat {
            flex-grow: 1;
            padding: 10px; /* Reduced padding */
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 10px;
        }
        .message {
            padding: 8px 15px; /* Slightly reduced padding */
            border-radius: 20px;
            color: white; /* White text color for dark mode */
            max-width: 70%;
            word-wrap: break-word; /* Ensure text wraps in bubble */
        }
        .user {
            background-color: #0a84ff; /* Bright color for user messages */
            align-self: flex-end;
        }
        .bot {
            background-color: #333; /* Dark color for bot messages */
            align-self: flex-start;
        }
        #input-area {
            border-top: 1px solid #333;
            padding: 8px; /* Reduced padding in the input area */
            display: flex;
        }
        #user_input {
            flex-grow: 1;
            padding: 8px;
            border: 1px solid #555; /* Darker border for input field */
            border-radius: 20px;
            outline: none;
            background-color: #333; /* Dark input field */
            color: white; /* White input text */
        }
        button {
            padding: 8px 16px;
            border: none;
            background-color: #0a84ff; /* Matching button color with user messages */
            color: white;
            border-radius: 20px;
            cursor: pointer;
            margin-left: 10px; /* Add space between input and button */
        }
        button:hover {
            background-color: #0070d2;
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
                chat.scrollTop = chat.scrollHeight; // Scroll to bottom

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
                    chat.scrollTop = chat.scrollHeight; // Ensure new messages are seen
                });

                input.value = ''; // Clear input after sending
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
