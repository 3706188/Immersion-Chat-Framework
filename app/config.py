import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    GEMINI_API_KEY : str = os.getenv("GEMINI_API_KEY", "")
    # 免費版建議使用 gemini-2.0-flash 或 gemini-1.5-flash
    MODEL_NAME: str = "gemini-2.5-flash" 

settings = Settings()