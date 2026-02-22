# 🩺 Health Diagnosis Agent

An intelligent AI-powered health diagnosis agent built with **Google's Agent Development Kit (ADK)**. It analyzes symptoms, medical history, and user input using multiple large language models (Gemini, xAI Grok, OpenAI, Anthropic) to provide preliminary health insights, possible conditions, and recommendations.

> ⚠️ **Disclaimer**: This project is for **educational and research purposes only**. It is **NOT** a substitute for professional medical advice, diagnosis, or treatment. Always consult a qualified healthcare provider.

---

## ✨ Features

- **Multi-LLM Reasoning**: Combines Google (Gemini) xAI (Grok), OpenAI (GPT), and Anthropic (Claude) for more balanced and accurate diagnoses
- **Conversational Memory**: Remembers user history and follows up naturally
- **Web Interface**: Simple, clean frontend (`index.html`) for easy interaction
- **Agentic Workflow**: Built with Google's ADK — supports tool calling, planning, and evaluation
- **Privacy Focused**: All API keys are loaded locally via `.env` (never committed)
- **Extensible**: Easy to add new tools (web search, medical databases, image analysis, etc.)

## 🛠 Tech Stack

- **Python** 3.11+
- **Google Agent Development Kit (ADK)**
- **LLMs**: Goggle Gemini, xAI Grok, OpenAI GPT-4o / o1, Anthropic Claude 3.5/Opus
- **Frontend**: HTML + JavaScript (simple static UI)
---

## 🚀 Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/TekFed/health_diagnosis_agent.git
cd health_diagnosis_agent
```

### 2. Create virtual environment (recommended)
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up API keys
```bash
cp agents/.env.example agents/.env
```

Edit `agents/.env` and add your keys:
```env
GEMINI_API_KEY=SK-...
XAI_API_KEY=sk-...
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-...
```

---

## 🎮 How to Run

### Option A: Web Interface (Recommended)
```bash
# Just open the file in your browser
# Double-click index.html or run:
python -m http.server 8000

# Then go to `http://localhost:8000`

OR

# for the web dev ui
adk web

#to run in terminal
adk run
```

### Option B: CLI Mode
```bash
python -m agents.main
```

---

## 📁 Project Structure

```
health_diagnosis_agent/
├── agents/                 # Core ADK agents and tools
│   ├── __init__.py
│   ├── main.py
│   ├── agents.py
│   ├── tools.py
│   ├── .env                # ← ignored
│   └── .env.example
├── .adk/                   # ADK local cache (ignored)
├── __pycache__/            # Python cache (ignored)
├── index.html              # Web frontend
├── .gitignore
├── LICENSE
├── README.md
└── requirements.txt
```

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Open issues for bugs or feature requests
- Submit pull requests
- Improve documentation or add new tools

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Google Agent Development Kit team
- Google, xAI, OpenAI, and Anthropic for their powerful models
- All open-source contributors

---

**Built with ❤️ and lots of ☕**

---
