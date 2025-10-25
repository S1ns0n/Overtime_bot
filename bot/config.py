import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BOT_TOKEN = os.environ.get('BOT_TOKEN')
    API_URL = os.environ.get('API_URL')