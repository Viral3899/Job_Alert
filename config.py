import os

from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN: str | None = os.getenv("TELEGRAM_BOT_TOKEN")
# Be tolerant of a common .env mistake: TELEGRAM_BOT_TOKEN=TELEGRAM_BOT_TOKEN=123...
if TELEGRAM_BOT_TOKEN:
    TELEGRAM_BOT_TOKEN = TELEGRAM_BOT_TOKEN.strip().strip("'")
    if TELEGRAM_BOT_TOKEN.startswith("TELEGRAM_BOT_TOKEN="):
        TELEGRAM_BOT_TOKEN = TELEGRAM_BOT_TOKEN.split("=", 1)[1].strip().strip("'")
TELEGRAM_CHAT_ID: str | None = os.getenv("TELEGRAM_CHAT_ID")
GROQ_API_KEY: str | None = os.getenv("GROQ_API_KEY")
GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

CHECK_INTERVAL_MINUTES: int = int(os.getenv("CHECK_INTERVAL_MINUTES", "15"))
JOB_LOOKBACK_HOURS: int = int(os.getenv("JOB_LOOKBACK_HOURS", "48"))
MIN_MATCH_SCORE: int = int(os.getenv("MIN_MATCH_SCORE", "60"))

# Search terms intentionally broader than only "AI/ML Engineer" so alerts from
# adjacent GenAI/LLM/RAG/Data Scientist roles are not missed.
TARGET_ROLES: list[str] = [
    "ai/ml engineer",
    "ai ml engineer",
    "ai engineer",
    "artificial intelligence engineer",
    "machine learning engineer",
    "ml engineer",
    "machine learning developer",
    "generative ai engineer",
    "genai engineer",
    "gen ai engineer",
    "llm engineer",
    "rag engineer",
    "rag developer",
    "agentic ai engineer",
    "ai agent engineer",
    "ai developer",
    "mlops engineer",
    "machine learning scientist",
    "data scientist",
    "applied scientist",
    "applied ai engineer",
    "software engineer ai",
    "software engineer ml",
    "nlp engineer",
    "computer vision engineer",
    "deep learning engineer",
]

TARGET_LOCATIONS: list[str] = [
    "remote",
    "remote india",
    "india remote",
    "work from home",
    "wfh",
    "rajkot",
    "ahmedabad",
    "gandhinagar",
    "gift city",
    "gujarat",
    "bengaluru",
    "bangalore",
    "hyderabad",
    "pune",
    "gurugram",
    "gurgaon",
    "noida",
    "delhi",
    "mumbai",
    "chennai",
    "indore",
]

TARGET_SKILLS: list[str] = [
    "python",
    "machine learning",
    "deep learning",
    "generative ai",
    "genai",
    "llm",
    "large language model",
    "rag",
    "retrieval augmented generation",
    "langchain",
    "langgraph",
    "llamaindex",
    "agentic ai",
    "ai agents",
    "fastapi",
    "flask",
    "aws",
    "azure",
    "gcp",
    "docker",
    "kubernetes",
    "sql",
    "tensorflow",
    "pytorch",
    "transformers",
    "hugging face",
    "sentence transformers",
    "vector database",
    "qdrant",
    "faiss",
    "pinecone",
    "pgvector",
    "milvus",
    "opensearch",
    "mlflow",
    "onnx",
    "ocr",
]

# Strong negatives. These reduce score but do not automatically discard a job.
EXCLUDED_TERMS: list[str] = [
    "intern",
    "internship",
    "fresher",
    "student",
    "trainee",
    "7+ years",
    "8+ years",
    "9+ years",
    "10+ years",
    "11+ years",
    "12+ years",
]

PLATFORMS: list[str] = [
    "LinkedIn",
    "Indeed",
    "Naukri",
    "Wellfound",
    "Cutshort",
    "Instahyre",
    "Hirist",
    "Foundit",
    "TimesJobs",
    "Shine",
    "Freshersworld",
]
