# Product Recommender Agent

An AI shopping assistant that understands what a user wants from a normal chat, remembers their preferences across sessions, and recommends products from a catalog using an LLM (Groq).

## Features

- Chat in plain English, e.g. "I need jewellery under 25000"
- Extracts preferences (category, budget, liked/disliked brands, liked features) from the conversation
- Saves the user profile to disk, so preferences are remembered between sessions
- Filters the catalog by category, budget and disliked brands
- Ranks products by liked brands and liked features
- Explains each recommendation in natural language
- Two ways to use it: terminal chat or web UI (FastAPI)
- Automated tests with pytest

## Tech Stack

| Part | Technology |
|------|------------|
| Language | Python 3.12 |
| LLM | Groq API |
| Backend / API | FastAPI, Uvicorn |
| Frontend | HTML, CSS, JavaScript |
| Data | JSON catalog, pandas |
| Testing | pytest, httpx |

## Project Structure

```
product-recommender-agent/
├── backend/
│   ├── __init__.py
│   ├── api.py            # FastAPI endpoints
│   ├── functions.py      # Catalog, profile, filtering and scoring
│   └── orchestrator.py   # LLM calls and tool calling
├── dataset/
│   └── products.json     # Product catalog
├── frontend/
│   ├── templates/
│   │   └── index.html    # Chat page
│   └── static/
│       ├── style.css
│       └── script.js
├── tests/
│   ├── conftest.py       # Keeps tests away from the real profile.json
│   ├── test_api.py
│   └── test_functions.py
├── .env.example          # Template for environment variables
├── .gitignore
├── helper.py
├── main.py               # Terminal chat entry point
├── requirements.txt
└── README.md
```

## Setup

1. Clone the repo
```bash
   git clone https://github.com/aarya-chauhan011/product-recommender-agent.git
   cd product-recommender-agent
```
2. Create and activate a virtual environment
```bash
   python -m venv venv
   venv\Scripts\activate        # Windows
   source venv/bin/activate     # Mac / Linux
```
3. Install dependencies
```bash
   pip install -r requirements.txt
```
4. Copy `.env.example` to `.env` and add your Groq API key
```
   GROQ_API_KEY=your_key_here
```

## Usage

### Option 1: Terminal chat

```bash
python main.py
```

Type `reset` to clear saved preferences and `quit` to exit.

### Option 2: Web UI

```bash
uvicorn backend.api:app --reload
```

Open http://127.0.0.1:8000 in your browser.
Interactive API docs are available at http://127.0.0.1:8000/docs.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Serves the chat web page |
| POST | `/chat` | Send a message, get the assistant's reply and the updated profile |
| GET | `/profile` | Get the saved user profile |
| POST | `/reset` | Clear saved preferences and chat history |

Example request:

```json
POST /chat
{"message": "I need jewellery under 25000"}
```

Example response:

```json
{
  "reply": "Here are my top picks...",
  "profile": {"category": "Jewellery", "max_budget": 25000, "liked_brands": [], "disliked_brands": [], "liked_features": []}
}
```

## How It Works

1. The user sends a message.
2. The orchestrator asks the LLM to extract preferences and updates the saved profile.
3. `find_products()` filters the catalog (category, budget, disliked brands) and ranks the results (liked brands, liked features).
4. The LLM explains the top recommendations to the user.

## Running Tests

```bash
python -m pytest -v
```

Tests do not call the Groq API and do not modify your real `profile.json`.

## Notes

- `.env` and `profile.json` are in `.gitignore` and are never pushed to GitHub.
- The current version keeps one shared conversation, so it is meant for a single user.