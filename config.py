import os

from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not set in .env")

ACTOR_MODEL = "gemini/gemini-3.5-flash-lite"
CRITIC_MODEL = "gemini/gemini-3.6-flash"
