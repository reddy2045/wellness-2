import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Security
    SECRET_KEY = os.getenv("SECRET_KEY", "change-this-secret")

    # Railway MySQL
    MYSQL_HOST = os.getenv("MYSQLHOST")
    MYSQL_PORT = int(os.getenv("MYSQLPORT", 3306))
    MYSQL_USER = os.getenv("MYSQLUSER")
    MYSQL_PASSWORD = os.getenv("MYSQLPASSWORD")
    MYSQL_DB = os.getenv("MYSQLDATABASE")
    MYSQL_CURSORCLASS = "DictCursor"

    # Uploads
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")


