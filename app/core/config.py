import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
API_KEY_NAME = os.getenv("API_KEY_NAME", "x-api-key")

if not API_KEY:
    raise RuntimeError("API_KEY is not set in .env file")