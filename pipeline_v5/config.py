import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


class Config:
    # API keys come only from the environment or a local .env file (see ../.env.example).
    # Never write a real key in this file.
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "")

    # System Settings
    ACTIVE_BACKEND = os.getenv("STC_ACTIVE_BACKEND", "groq")
    BACKEND_PRIORITY = ['gemini', 'groq', 'openai', 'mistral']
    MAX_RETRIES = 3
    REQUEST_TIMEOUT = 60
    SEARCH_LIMIT = 5

    # Set STC_SIMULATE=1 to get placeholder text instead of real model output (for UI testing only).
    SIMULATE = os.getenv("STC_SIMULATE", "") == "1"

    # V5 Framework Engine
    V5_FRAMEWORK_ENGINE = """
- Mechanisms: Signalling-without-habit, perceived-vs-actual attribution gap, quick-commerce distortion, VC incentive misalignment, and moat decay.
- Temporal Curve: Day 0-7 (Excitement), 7-30 (Friction), 30-60 (Doubt), 60+ (Abandonment).
- Segmentation: Disciplined vs. Impulsive, Problem-driven vs. Aspirational.
"""
