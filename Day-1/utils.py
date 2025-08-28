"""
Utility helpers for the ai-education project.

Provides:
- GEMINI API detection and safe configure
- safe_generate(prompt) wrapper that returns (success, text)
- mock_response(prompt) for offline mode
- JSON load/save helpers
- small logger helper
"""

import os
import json
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# try to import google generative ai (optional)
try:
    import google.generativeai as genai
except Exception:
    genai = None

# Setup basic logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("ai-education-utils")

# Data directory for runtime files
DATA_DIR = Path(os.getenv("AI_EDU_DATA_DIR", "."))  # default: project root
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Files used by project
SCORES_FILE = DATA_DIR / "scores.json"
QUIZ_FILE = DATA_DIR / "quiz_questions.json"

def get_api_key():
    """Return GEMINI API key from environment variable."""
    return os.getenv("GEMINI_API_KEY", "").strip()

def is_gemini_available():
    """True if google.generativeai package present and key configured."""
    return (genai is not None) and bool(get_api_key())

def configure_gemini():
    """Configure genai if possible. Raises RuntimeError on missing package or key."""
    if genai is None:
        raise RuntimeError("google-generativeai package not installed. Install: pip install google-generativeai")
    key = get_api_key()
    if not key:
        raise RuntimeError("GEMINI_API_KEY not set. Add it in .env file.")
    genai.configure(api_key=key)
    return genai

def get_model(model_name="gemini-1.5-flash"):
    """Returns a generative model instance (if gemini available), else None."""
    if not is_gemini_available():
        return None
    configure_gemini()
    return genai.GenerativeModel(model_name)

def safe_generate(prompt: str, model_name="gemini-1.5-flash"):
    """Try to generate text from Gemini safely. Returns (True, text) or (False, error)."""
    try:
        model = get_model(model_name)
        if model is None:
            return False, "(offline) gemini not available"
        resp = model.generate_content(prompt)
        txt = getattr(resp, "text", str(resp))
        return True, txt
    except Exception as e:
        logger.exception("safe_generate failed")
        return False, f"Gemini call failed: {e}"

def mock_response(prompt: str):
    """Small deterministic mock reply for offline testing."""
    p = prompt or ""
    if "summarize" in p.lower():
        return "This is a short mock summary. (Set GEMINI_API_KEY to use real model.)"
    if "question" in p.lower() or "mcq" in p.lower() or "generate" in p.lower():
        return ("Question: What is the capital of India?\n"
                "Options:\nA) Mumbai\nB) New Delhi\nC) Chennai\nD) Kolkata\nAnswer: B")
    if len(p) < 40:
        return f"(mock) I received: {p[:120]}"
    return "(mock) This is an offline fallback. Install google-generativeai and set GEMINI_API_KEY for real replies."

# JSON helpers
def load_json_safe(path: Path):
    try:
        with path.open("r", encoding="utf-8") as fh:
            return json.load(fh)
    except FileNotFoundError:
        return None
    except Exception as e:
        logger.warning("Failed to load JSON %s: %s", path, e)
        return None

def save_json_safe(obj, path: Path):
    try:
        with path.open("w", encoding="utf-8") as fh:
            json.dump(obj, fh, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        logger.exception("Failed to save JSON %s: %s", path, e)
        return False

# small convenience wrappers
def load_scores():
    data = load_json_safe(SCORES_FILE)
    return data if isinstance(data, dict) else {}

def save_scores(data):
    return save_json_safe(data, SCORES_FILE)

def load_quiz_questions():
    data = load_json_safe(QUIZ_FILE)
    if isinstance(data, list) and data:
        return data
    return None

def ensure_files_exist():
    if not SCORES_FILE.exists():
        save_json_safe({}, SCORES_FILE)
    if not QUIZ_FILE.exists():
        save_json_safe([], QUIZ_FILE)

# prepare data dir on import
ensure_files_exist()
