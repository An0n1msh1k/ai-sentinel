import os

from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not set in .env")

#ACTOR_MODEL = "ollama/qwen2.5-coder:1.5b"
#CRITIC_MODEL = "ollama/qwen2.5-coder:1.5b"

ACTOR_MODEL = "gemini/gemini-3.5-flash-lite"
CRITIC_MODEL = "gemini/gemini-3.6-flash"
# MODEL="groq/llama-3.3-70b-versatile"

# ollama/qwen2.5-coder:1.5b моя локальна лошадка
# groq/llama-3.1-8b-instant	Ідеальний Актор. Дуже швидка (до 300 токенів/сек), чудово пише код і чорнові конфіги.	~500 000+ токенів/день (у 5 разів більше за 70B)
# openai/gpt-oss-20b replacement for deprecation
# groq/mixtral-8x7b-32768	Альтернатива для логіки та аналітики, велике вікно контексту.	~500 000+ токенів/день
# groq/gemma2-9b-it	Модель від Google (Gemma 2 9B), але працює на швидкому залізі Groq.	~500 000+ токенів/день
# groq/llama-3.3-70b-versatile	Ідеальний Критик. Найрозумніша модель для глибокого аудиту та пошуку вразливостей.
# openai/gpt-oss-120b or qwen/qwen3.6-27b