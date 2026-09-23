import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

CHECK_INTERVAL_MINUTES = int(os.getenv("CHECK_INTERVAL_MINUTES", "20"))
MIN_MATCH_SCORE = int(os.getenv("MIN_MATCH_SCORE", "60"))

TARGET_ROLES = [
    "ai/ml engineer", "ai ml engineer", "ai engineer",
    "machine learning engineer", "ml engineer",
    "generative ai engineer", "genai engineer",
    "llm engineer", "rag engineer", "data scientist",
]

TARGET_LOCATIONS = [
    "remote", "work from home", "wfh", "rajkot",
    "ahmedabad", "gandhinagar", "gift city", "gujarat",
]

TARGET_SKILLS = [
    "python", "machine learning", "deep learning",
    "generative ai", "genai", "llm", "rag", "langchain",
    "langgraph", "fastapi", "aws", "docker", "sql",
    "tensorflow", "pytorch", "transformers",
    "vector database", "qdrant", "faiss", "pinecone",
]

EXCLUDED_TERMS = [
    "intern", "internship", "fresher", "student",
    "7+ years", "8+ years", "10+ years",
]
