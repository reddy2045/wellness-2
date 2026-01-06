import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'secret-key')

    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.getenv('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'Reddy@123')
    MYSQL_DB = os.getenv('MYSQL_DB', 'wellness_coach')
    MYSQL_CURSORCLASS = 'DictCursor'

    # ✅ MUST BE HERE
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
