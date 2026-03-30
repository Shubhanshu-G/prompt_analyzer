"""Configuration for multi-agent AI system"""

# Ollama settings
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_DEFAULT_MODEL = "llama3.1:8b"  # User's current primary model

# File upload settings
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB
ALLOWED_FILE_TYPES = [".txt", ".docx", ".pdf", ".png", ".jpg", ".jpeg", ".webp"]
IMAGE_FILE_TYPES = [".png", ".jpg", ".jpeg", ".webp"]
UPLOAD_FOLDER = "uploads"

# Vision Model settings
VISION_MODELS = ["llava", "bakllava", "llava:7b", "llava:13b", "llava:34b"]
DEFAULT_VISION_MODEL = "llava"

# UI Configuration
APP_TITLE = "Local Multi-Agent AI System"
APP_ICON = "🤖"

# Agent Configuration
DEFAULT_TEMPERATURE = 0.7
DEFAULT_TOP_P = 0.9

# Evaluator Configuration
EVALUATORS = {
    "prompt": {
        "name": "Prompt Quality Evaluator",
        "icon": "📝",
        "criteria": [
            {"name": "Clarity", "weight": 25, "description": "Is the prompt clear and unambiguous?"},
            {"name": "Specificity", "weight": 25, "description": "Does it have enough detail and specificity?"},
            {"name": "Context", "weight": 25, "description": "Is sufficient background/context provided?"},
            {"name": "Actionability", "weight": 25, "description": "Can the AI effectively act on this prompt?"},
        ]
    },
    "decision": {
        "name": "AI Decision Evaluator",
        "icon": "⚖️",
        "criteria": [
            {"name": "Logic Soundness", "weight": 30, "description": "Is the decision logically sound?"},
            {"name": "Evidence-Based", "weight": 25, "description": "Is it backed by facts/data?"},
            {"name": "Fairness", "weight": 25, "description": "Are potential biases considered?"},
            {"name": "Completeness", "weight": 20, "description": "Were all relevant options evaluated?"},
        ]
    }
}

# Grade mapping
GRADE_MAPPING = {
    (90, 100): "A - Excellent",
    (80, 89): "B - Good",
    (70, 79): "C - Fair",
    (60, 69): "D - Below Average",
    (0, 59): "F - Poor"
}
