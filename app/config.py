import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found. Please add it to your .env file.")

MAX_AGENT_ITERATIONS = 8   # Safety limit — agent stops after 8 tool calls
MAX_WEBPAGE_CHARS = 3000   # How much text to read from each webpage
