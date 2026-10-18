import json
import os
from groq import Groq
import gradio as gr

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

# 2. Define the Human-Like Persona + Record Awareness
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

# 3. Define Tools for Personal Records
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

# 4. Agent Function for Gradio Web UI
def chat_with_agent(message, history):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    for human_msg, ai_msg in history:
        messages.append({"role": "user", "content": human_msg})
        messages.append({"role": "assistant", "content": ai_msg})
        
    messages.append({"role": "user", "content": message})

    for step in range(5):
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
            return msg.content

# 5. Launch Free Local Web UI
demo = gr.ChatInterface(
    fn=chat_with_agent, 
    title="AI Companion Pod (Local Vault)",
    description="Your private, free AI agent with local personal record keeping."
)

if __name__ == "__main__":
    demo.launch()