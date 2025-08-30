import os
from dotenv import load_dotenv

# Database configuration
DATABASE_NAME = os.getenv("DATABASE_NAME", "interview_bot")

# Collection names
SESSIONS_COLLECTION = "sessions"
USERS_COLLECTION = "users"

# Interview flow configuration
INTERVIEW_FLOW = {
    "greeting": {"count": 1, "phase": "greeting"},
    "easy": {"count": 7, "phase": "easy"},
    "moderate": {"count": 4, "phase": "moderate"}, 
    "scenario": {"count": 2, "phase": "scenario"},
    "hard": {"count": 3, "phase": "hard"},
    "expert": {"count": 2, "phase": "expert"}
}

TOTAL_QUESTIONS = sum(phase["count"] for phase in INTERVIEW_FLOW.values())

# API Configuration
OPENROUTER_API_URL =os.getenv("OPENROUTER_API_URL", "https://openrouter.ai/api/v1/chat/completions")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "openai/gpt-4o-mini")
DEFAULT_TEMPERATURE = os.getenv("DEFAULT_TEMPERATURE", 0.7)
DEFAULT_MAX_TOKENS = os.getenv("DEFAULT_MAX_TOKENS", 300)
