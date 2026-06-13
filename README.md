# 🤖 ResearchBot — Autonomous AI Research Agent

Give ResearchBot any topic. It autonomously searches the web, reads pages, and writes a full research report — no human input needed after the initial prompt.

## 🧠 What Makes This an "Agent"?

Unlike a normal chatbot, ResearchBot:
- **Decides on its own** what to search for
- **Reads real web pages** to gather current information
- **Plans multiple steps** to build a complete picture
- **Knows when to stop** once it has enough information

This is powered by **Gemini Function Calling** — the core technology behind all modern AI agents.

## ⚙️ Agent Loop

```
User gives topic
     ↓
Gemini decides: "I should search for X"
     ↓
web_search("X") executes → results returned to Gemini
     ↓
Gemini decides: "I should read this URL for more detail"
     ↓
read_webpage(url) executes → content returned to Gemini
     ↓
Gemini decides: "I have enough info"
     ↓
Writes structured research report
```

## 🛠️ Tech Stack

| Component | Tool |
|---|---|
| LLM + Function Calling | Google Gemini 1.5 Flash |
| Web Search | DuckDuckGo (no API key needed) |
| Web Scraping | requests + BeautifulSoup4 |
| Backend | FastAPI |
| Frontend | HTML + CSS + Vanilla JS |

## 🚀 Running Locally

```bash
# Clone
git clone https://github.com/YOUR_USERNAME/researchbot.git
cd researchbot

# Virtual environment
python -m venv venv
source venv/bin/activate    # Windows: venv\Scripts\activate

# Install
pip install -r requirements.txt

# Add your Gemini API key
cp .env.example .env
# Edit .env and paste your key from aistudio.google.com

# Run
uvicorn app.main:app --reload
# Open http://localhost:8000
```

## 📁 Structure

```
researchbot/
├── app/
│   ├── main.py              # FastAPI entry point
│   ├── config.py            # Settings
│   ├── schemas.py           # Data models
│   ├── core/
│   │   ├── tools.py         # web_search + read_webpage functions
│   │   └── agent.py         # The agent loop (function calling)
│   └── routes/
│       └── research.py      # POST /api/research
├── frontend/
│   └── index.html           # Terminal-style UI
└── requirements.txt
```

## 📝 Resume Bullets

```
ResearchBot — Autonomous AI Research Agent    Python, Gemini API, FastAPI, BeautifulSoup
• Built an autonomous AI agent using Gemini 1.5 Flash function calling that independently
  plans, searches, and synthesises multi-source research reports without human guidance.
• Implemented tool-use architecture with web_search (DuckDuckGo) and read_webpage
  (BeautifulSoup) tools, enabling the agent to retrieve and process live web content.
• Designed a self-terminating agent loop with iteration limits and structured report
  generation covering executive summary, key findings, and cited sources.
• Deployed as a FastAPI service with a real-time execution log UI showing each agent step.
```
