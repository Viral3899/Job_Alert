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
    "llm engineer", "rag engineer", "data scientist","data analyst", "bussiness intteligence analyst", "data engineer", "data analytics engineer",
]

TARGET_LOCATIONS = [
    "remote", "work from home", "wfh", "rajkot",
     "gujarat",
]

TARGET_SKILLS = [

    # =========================
    # Programming
    # =========================
    "python",
    "java",
    "c++",
    "javascript",
    "typescript",
    "golang",
    "scala",
    "r",
    "bash",

    # =========================
    # Machine Learning / AI
    # =========================
    "machine learning",
    "ml",
    "artificial intelligence",
    "ai",
    "deep learning",
    "neural networks",
    "ann",
    "cnn",
    "rnn",
    "lstm",
    "gru",
    "reinforcement learning",
    "supervised learning",
    "unsupervised learning",
    "semi-supervised learning",
    "transfer learning",
    "ensemble learning",
    "feature engineering",
    "model training",
    "model evaluation",
    "predictive modeling",

    # =========================
    # Generative AI / LLM
    # =========================
    "generative ai",
    "genai",
    "gen ai",
    "generative artificial intelligence",
    "large language model",
    "large language models",
    "llm",
    "llms",
    "foundation models",
    "language models",
    "multimodal ai",
    "multimodal",
    "ai agents",
    "agentic ai",
    "agentic systems",
    "autonomous agents",
    "multi-agent",
    "multi agent systems",
    "llm agents",
    "ai agent",
    "agent framework",

    # =========================
    # LLM Frameworks
    # =========================
    "langchain",
    "langgraph",
    "llamaindex",
    "llama index",
    "haystack",
    "semantic kernel",
    "autogen",
    "crewai",
    "dspy",

    # =========================
    # RAG / Knowledge Systems
    # =========================
    "rag",
    "retrieval augmented generation",
    "retrieval-augmented generation",
    "advanced rag",
    "agentic rag",
    "graph rag",
    "knowledge graph",
    "knowledge graphs",
    "semantic search",
    "hybrid search",
    "vector search",
    "document intelligence",
    "document ai",
    "question answering",
    "qa systems",
    "enterprise search",

    # =========================
    # LLM Techniques
    # =========================
    "prompt engineering",
    "prompt engineering",
    "prompt optimization",
    "context engineering",
    "fine tuning",
    "fine-tuning",
    "instruction tuning",
    "parameter efficient fine tuning",
    "peft",
    "lora",
    "qlora",
    "rlhf",
    "rag evaluation",
    "llm evaluation",
    "llmops",
    "model evaluation",
    "guardrails",
    "ai safety",
    "structured output",
    "function calling",
    "tool calling",

    # =========================
    # LLM Providers / Models
    # =========================
    "openai",
    "chatgpt",
    "gpt",
    "gpt-4",
    "gpt-5",
    "azure openai",
    "gemini",
    "google gemini",
    "anthropic",
    "claude",
    "llama",
    "meta llama",
    "mistral",
    "mixtral",
    "qwen",
    "deepseek",
    "hugging face",
    "huggingface",
    "cohere",

    # =========================
    # NLP
    # =========================
    "natural language processing",
    "nlp",
    "natural language understanding",
    "nlu",
    "text classification",
    "text generation",
    "text summarization",
    "sentiment analysis",
    "named entity recognition",
    "ner",
    "information extraction",
    "speech recognition",
    "speech to text",
    "text to speech",
    "tts",
    "embeddings",
    "sentence transformers",

    # =========================
    # Computer Vision
    # =========================
    "computer vision",
    "cv",
    "image processing",
    "object detection",
    "image classification",
    "image segmentation",
    "ocr",
    "optical character recognition",
    "opencv",
    "yolo",
    "yolov8",
    "yolov9",
    "yolov10",
    "yolov11",
    "stable diffusion",
    "image generation",
    "vision language model",
    "vlm",
    "multimodal llm",

    # =========================
    # ML Frameworks
    # =========================
    "scikit-learn",
    "sklearn",
    "tensorflow",
    "keras",
    "pytorch",
    "torch",
    "jax",
    "xgboost",
    "lightgbm",
    "catboost",
    "onnx",
    "onnxruntime",

    # =========================
    # Vector Databases
    # =========================
    "vector database",
    "vector databases",
    "vector db",
    "qdrant",
    "faiss",
    "pinecone",
    "weaviate",
    "milvus",
    "chroma",
    "chromadb",
    "pgvector",
    "redis vector",
    "opensearch",
    "elasticsearch",

    # =========================
    # Databases
    # =========================
    "sql",
    "mysql",
    "postgresql",
    "postgres",
    "mariadb",
    "mongodb",
    "redis",
    "dynamodb",
    "oracle",
    "nosql",

    # =========================
    # APIs / Backend
    # =========================
    "fastapi",
    "flask",
    "django",
    "rest api",
    "restful api",
    "api development",
    "microservices",
    "backend development",
    "websocket",
    "grpc",

    # =========================
    # Cloud / AWS
    # =========================
    "aws",
    "amazon web services",
    "ec2",
    "s3",
    "rds",
    "lambda",
    "ecs",
    "eks",
    "ecr",
    "cloudwatch",
    "sagemaker",
    "bedrock",
    "aws bedrock",
    "azure",
    "azure ai",
    "azure ml",
    "gcp",
    "google cloud",
    "vertex ai",

    # =========================
    # DevOps / MLOps
    # =========================
    "docker",
    "kubernetes",
    "k8s",
    "jenkins",
    "github actions",
    "ci/cd",
    "cicd",
    "terraform",
    "mlops",
    "mlflow",
    "dvc",
    "model deployment",
    "model serving",
    "model monitoring",
    "experiment tracking",
    "feature store",
    "kubeflow",
    "airflow",
    "apache airflow",

    # =========================
    # Data Engineering
    # =========================
    "data engineering",
    "data pipeline",
    "etl",
    "elt",
    "data processing",
    "pandas",
    "numpy",
    "spark",
    "pyspark",
    "apache spark",
    "kafka",
    "apache kafka",
    "databricks",
    "snowflake",
    "dbt",

    # =========================
    # Analytics / Visualization
    # =========================
    "data science",
    "data scientist",
    "data analyst",
    "business intelligence",
    "power bi",
    "tableau",
    "advanced excel",
    "matplotlib",
    "seaborn",
    "plotly",

    # =========================
    # AI Application Development
    # =========================
    "ai application",
    "ai applications",
    "ai product",
    "ai platform",
    "ai solutions",
    "ai engineering",
    "machine learning engineer",
    "ml engineer",
    "ai engineer",
    "ai/ml engineer",
    "mlops engineer",
    "generative ai engineer",
    "genai engineer",
    "llm engineer",
    "ai developer",
    "machine learning developer",
    "applied scientist",
    "research engineer",

    # =========================
    # Chatbots / Conversational AI
    # =========================
    "chatbot",
    "chatbots",
    "conversational ai",
    "conversational artificial intelligence",
    "virtual assistant",
    "ai assistant",
    "voice ai",
    "voice assistant",
    "customer support ai",

    # =========================
    # Production / Architecture
    # =========================
    "production ai",
    "production ml",
    "ml systems",
    "ai systems",
    "distributed systems",
    "scalable ai",
    "scalable machine learning",
    "model serving",
    "inference",
    "real-time inference",
    "real time ai",
    "ai architecture",
    "ml architecture",
    "solution architecture",
]

EXCLUDED_TERMS = [
    "intern", "internship", "fresher", "student",
    "7+ years", "8+ years", "10+ years",
]
