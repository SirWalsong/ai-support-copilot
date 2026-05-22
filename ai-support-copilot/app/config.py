import os
from dotenv import load_dotenv

load_dotenv()

MODEL_NAME = os.getenv("MODEL_NAME")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")