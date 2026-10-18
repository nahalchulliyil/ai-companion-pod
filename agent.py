import json
import os
from groq import Groq

# 1. Define the Human-Like Persona
SYSTEM_PROMPT = """
You are an intelligent, grounded, and candid AI companion.

Core Guidelines:
1. Speak naturally, concisely, and like a real human friend or collaborator.
2. NEVER use generic chatbot fluff or overly cheerful corporate greetings (e.g., "Sure thing!", "Let's get the conversation flowing!", "How can I assist you today?").
3. Match the user's energy, conversational tone, and level of depth.
4. Have opinions, use subtle humor or curiosity when appropriate, and ask natural, open-ended follow-up questions instead of listing generic choices.
5. Focus on mutual dialogue rather than sounding like a customer support bot.
"""

# Securely load API key from environment variables
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)

# 1. DEFINE TOOL FUNCTION
def get_stock_price(symbol: str) -> str:
    mock_db = {
        "AAPL": "$230.50", 
        "TSLA": "$210.00", 
        "NVDA": "$125.00", 
        "MSFT": "$420.00", 
        "GOOGL": "$175.00"
    }
    return mock_db.get(symbol.upper(), "Stock symbol not found in database.")

# 2. DEFINE TOOL SCHEMA FOR GROQ
tools_schema = [{
    "type": "function",
    "function": {
        "name": "get_stock_price",
        "description": "Fetch the live price for a stock ticker symbol.",
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {"type": "string", "description": "The stock ticker symbol (e.g. AAPL)"}
            },
            "required": ["symbol"]
        }
    }
}]

# 3. AGENT EXECUTION LOOP
def run_agent(user_prompt: str):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt}
    ]
    print(f"\n👤 User Prompt: '{user_prompt}'\n" + "-"*40)

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
            
            print(f"🤖 LLM requested tool: [{func_name}] with args: {args}")

            if func_name == "get_stock_price":
                result = get_stock_price(args.get("symbol"))
                print(f"⚙️ Tool Output returned: {result}\n")

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(result)
                })
        else:
            print(f"🤖 Final Agent Response:\n{msg.content}\n")
            break

if __name__ == "__main__":
    print("🤖 Agent is online! Type your questions below (type 'exit' to quit).\n" + "="*50)
    while True:
        user_input = input("\n👤 Ask something: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break
        run_agent(user_input)
