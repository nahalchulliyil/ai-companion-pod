import json
import os
from groq import Groq
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

# 1. Local Database File for Personal Records
RECORDS_FILE = "records.json"

def load_records():
    if os.path.exists(RECORDS_FILE):
        with open(RECORDS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_records_to_disk(records):
    with open(RECORDS_FILE, "w") as f:
        json.dump(records, f, indent=4)

# 2. Define Persona & Groq Client
SYSTEM_PROMPT = """
You are an intelligent, grounded, and candid AI companion with access to the user's local personal records.
Core Guidelines:
1. Speak naturally, concisely, and like a real human friend or collaborator.
2. NEVER use generic chatbot fluff or overly cheerful corporate greetings.
3. If the user asks you to remember or save a record, use the 'save_record' tool.
4. If they ask about past notes, use the 'get_record' tool.
"""

# Securely load API key from environment variables
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)

def save_record(title: str, content: str) -> str:
    records = load_records()
    records[title.lower()] = content
    save_records_to_disk(records)
    return f"Successfully saved record: '{title}'"

def get_record(title: str) -> str:
    records = load_records()
    return records.get(title.lower(), "No record found with that title.")

tools_schema = [
    {
        "type": "function",
        "function": {
            "name": "save_record",
            "description": "Save a personal note, record, or piece of information to local storage.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "The title or key of the record."},
                    "content": {"type": "string", "description": "The details or content to save."}
                },
                "required": ["title", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_record",
            "description": "Retrieve a saved personal record by its title.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "The title of the record to look up."}
                },
                "required": ["title"]
            }
        }
    }
]

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>AI Companion Pod (Local Vault)</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 20px; display: flex; flex-direction: column; align-items: center; height: 100vh; box-sizing: border-box; }
        h1 { margin-bottom: 5px; font-size: 1.5rem; color: #38bdf8; }
        p { margin-top: 0; color: #94a3b8; font-size: 0.9rem; }
        #chat-container { width: 100%; max-width: 700px; background: #1e293b; border-radius: 12px; display: flex; flex-direction: column; height: 75vh; box-shadow: 0 4px 20px rgba(0,0,0,0.5); overflow: hidden; border: 1px solid #334155; }
        #chat-box { flex: 1; padding: 20px; overflow-y: auto; display: flex; flex-direction: column; gap: 12px; }
        .message { padding: 12px 16px; border-radius: 8px; max-width: 80%; line-height: 1.4; word-break: break-word; }
        .user { background: #0284c7; color: white; align-self: flex-end; border-bottom-right-radius: 2px; }
        .assistant { background: #334155; color: #f1f5f9; align-self: flex-start; border-bottom-left-radius: 2px; }
        #input-area { display: flex; padding: 15px; background: #0f172a; border-top: 1px solid #334155; gap: 10px; }
        input { flex: 1; padding: 12px; border-radius: 6px; border: 1px solid #475569; background: #1e293b; color: white; font-size: 1rem; outline: none; }
        input:focus { border-color: #38bdf8; }
        button { padding: 12px 20px; background: #0284c7; color: white; border: none; border-radius: 6px; font-weight: bold; cursor: pointer; transition: background 0.2s; }
        button:hover { background: #0369a1; }
    </style>
</head>
<body>
    <h1>AI Companion Pod (Local Vault)</h1>
    <p>Private, local AI agent storing your notes securely in <code>records.json</code>.</p>
    <div id="chat-container">
        <div id="chat-box">
            <div class="message assistant">Hello. I am ready. What would you like to save or discuss today?</div>
        </div>
        <div id="input-area">
            <input type="text" id="user-input" placeholder="Type a message or note..." autofocus>
            <button onclick="sendMessage()">Send</button>
        </div>
    </div>

    <script>
        const chatBox = document.getElementById('chat-box');
        const userInput = document.getElementById('user-input');
        let history = [];

        userInput.addEventListener('keypress', function (e) {
            if (e.key === 'Enter') sendMessage();
        });

        async function sendMessage() {
            const text = userInput.value.trim();
            if (!text) return;

            appendMessage(text, 'user');
            userInput.value = '';
            chatBox.scrollTop = chatBox.scrollHeight;

            const loadingId = 'loading-' + Date.now();
            appendMessage('Thinking...', 'assistant', loadingId);

            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: text, history: history })
                });
                const data = await response.json();
                
                document.getElementById(loadingId).remove();
                appendMessage(data.reply, 'assistant');
                history = data.history;
            } catch (err) {
                document.getElementById(loadingId).innerText = 'Error connecting to local server.';
            }
            chatBox.scrollTop = chatBox.scrollHeight;
        }

        function appendMessage(text, sender, id = null) {
            const div = document.createElement('div');
            div.className = 'message ' + sender;
            if (id) div.id = id;
            div.innerText = text;
            chatBox.appendChild(div);
            chatBox.scrollTop = chatBox.scrollHeight;
        }
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message", "")
    history = data.get("history", [])

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for human_msg, ai_msg in history:
        messages.append({"role": "user", "content": human_msg})
        messages.append({"role": "assistant", "content": ai_msg})
    messages.append({"role": "user", "content": user_message})

    agent_reply = ""
    for _ in range(5):
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=messages,
            tools=tools_schema,
            tool_choice="auto"
        )
        msg = response.choices[0].message
        
        messages.append({
            "role": "assistant",
            "content": msg.content,
            "tool_calls": msg.tool_calls
        })

        if msg.tool_calls:
            tool_call = msg.tool_calls[0]
            func_name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)
            
            tool_result = ""
            if func_name == "save_record":
                tool_result = save_record(args.get("title"), args.get("content"))
            elif func_name == "get_record":
                tool_result = get_record(args.get("title"))
                
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(tool_result)
            })
        else:
            agent_reply = msg.content
            break  # Exit the loop early once the text response is ready

    # Append the newest transaction back to chat history records
    history.append([user_message, agent_reply])
    return jsonify({"reply": agent_reply, "history": history})

if __name__ == "__main__":
    app.run(debug=True)
