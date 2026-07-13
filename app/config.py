import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# Default model: gemini-1.5-flash is fast and supports tool calling/chat
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

# Quick verification
if not GEMINI_API_KEY:
    # We do not crash on import, but we will raise an error when the client is initialized
    print("[WARNING]: GEMINI_API_KEY is not set in the environment or .env file.")
