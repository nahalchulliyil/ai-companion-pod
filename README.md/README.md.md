# AI Companion Pod (Local Memory Vault)

An intelligent, 100% private, locally hosted AI companion web app featuring persistent memory via local file storage. Built with Python, Flask, and the Groq API, this application uses LLM tool-calling capabilities to save, manage, and retrieve personal notes without reliance on third-party cloud databases or subscription fees.

---

## 🌟 Key Features

* **Persistent Local Memory**: Automatically writes user records and notes to a local `records.json` file for long-term retention.
* **Function Calling / Tool Execution**: Leverages custom JSON function schemas (`save_record` and `get_record`) so the LLM dynamically interacts with the local storage.
* **100% Private & Free**: All personal records remain on your local device.
* **Lightweight Web Interface**: Styled single-page chat interface served via a local Flask backend.
* **High-Performance Reasoning**: Powered by the fast inference infrastructure of the Groq API.

---

## 🛠️ Architecture & Tech Stack

* **Backend**: Python 3, Flask
* **AI Engine & Function Calling**: Groq API (`openai/gpt-oss-20b`)
* **Database**: Local JSON File Storage (`records.json`)
* **Frontend**: HTML5, CSS3, JavaScript (Fetch API)

```
[ User Browser UI ] 
        │
        ▼ (HTTP Requests)
[ Flask Web Server (app.py) ]
        │
        ├──► Groq API (Inference & Tool Decisions)
        │
        └──► Local File System (records.json)
```

---

## 🚀 Quick Start Guide

### Prerequisites
* Python 3.10+ installed on your system.
* A free [Groq API Key](https://console.groq.com/).

### Installation & Setup

1. **Clone or Download the Repository**
   ```bash
   git clone https://github.com/your-username/ai-companion-pod.git
   cd ai-companion-pod
   ```

2. **Install Required Packages**
   ```bash
   pip install flask groq
   ```

3. **Configure API Key**
   Ensure your Groq API key is defined in `app.py`:
   ```python
   GROQ_API_KEY = "your-groq-api-key-here"
   ```

4. **Run the Application**
   ```bash
   python app.py
   ```

5. **Access the Interface**
   Open your browser and navigate to:
   `http://127.0.0.1:7860`

---

## 💡 Usage Examples

* **Saving Information**:
  * *User*: "Remember that my Wi-Fi password is `SecurePass123`."
  * *Agent*: Executes `save_record(title='wifi password', content='SecurePass123')`.

* **Retrieving Information**:
  * *User*: "What is my Wi-Fi password?"
  * *Agent*: Executes `get_record(title='wifi password')` and returns the details.

---

## 📂 File Structure

```text
ai_agent/
│
├── app.py          # Main Flask web server, agent orchestration, & UI template
└── records.json    # Local JSON storage for persistent records (auto-generated)
```

---

## 🛣️ Future Enhancements

- [ ] Support for vector embeddings (ChromaDB) for semantic retrieval instead of key-value lookup.
- [ ] Multi-user session management.
- [ ] UI panel to view, edit, and delete saved notes manually.