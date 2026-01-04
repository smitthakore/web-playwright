'''
Docstring for agent-backend.src.config
'''

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq")
    MODEL_NAME = os.getenv("MODEL_NAME", "llama-3.1-70b-versatile")
    MAX_TOKENS = 4096
    TEMPERATURE = 0.7
    PLANNER_PROMPT = "planner_v02"
    CODEGEN_PROMPT = "codegen_v02"

    @classmethod
    def validate(cls):
        if not cls.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY not set in environment")
        if not cls.GROQ_API_KEY.startswith("gsk_"):
            raise ValueError("Invalid GROQ_API_KEY format")
        print(f"✅ Config loaded - Provider: {cls.LLM_PROVIDER}, Model: {cls.MODEL_NAME}")

# Validate on import
Config.validate()