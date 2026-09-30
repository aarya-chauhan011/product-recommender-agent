# Product Recommender Agent

An AI shopping assistant that remembers user preferences across sessions
and recommends products from a catalog using an LLM (Groq).

## Features
- Extracts preferences (category, budget, brands, features) from chat
- Saves the user profile between sessions
- Filters and ranks products, then explains each recommendation

## Tech Stack
Python, Groq API, pandas

## Setup
1. Clone the repo
2. `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and add your GROQ_API_KEY
4. Run `python main.py`