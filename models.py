from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import MySQLdb.cursors
import re
import json
import logging

logger = logging.getLogger(__name__)


def init_models(mysql):

    # =========================
    # USER MODEL
    # =========================
    class User(UserMixin):
        def __init__(self, id, username, email, user_type,
                     profile_image=None, created_at=None):
            self.id = id
            self.username = username
            self.email = email
            self.user_type = user_type
            self.profile_image = profile_image
            self.created_at = created_at

        def get_id(self):
            return str(self.id)

        # -------- Flask-Login loader --------
        @staticmethod
        def get(user_id):
            try:
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute("SELECT * FROM users WHERE id=%s", (user_id,))
                user = cursor.fetchone()
                if not user:
                    return None
                return User(**user)
            except Exception as e:
                logger.error(f"User.get error: {e}")
                return None

        # -------- Registration --------
        @staticmethod
        def create(username, email, password, user_type="user"):
            if not User.is_valid_email(email):
                return None, "Invalid email address"
            if not User.is_valid_username(username):
                return None, "Invalid username"
            if not User.is_valid_password(password):
                return None, "Password too short"

            try:
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute(
                    "SELECT id FROM users WHERE email=%s OR username=%s",
                    (email, username)
                )
                if cursor.fetchone():
                    return None, "User already exists"

                hashed = generate_password_hash(password)
                cursor.execute(
                    """INSERT INTO users (username, email, password, user_type)
                       VALUES (%s, %s, %s, %s)""",
                    (username, email, hashed, user_type)
                )
                mysql.connection.commit()

                cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
                user = cursor.fetchone()
                return User(**user), "Registration successful"

            except Exception as e:
                logger.error(f"User.create error: {e}")
                return None, "Registration failed"

        # -------- Login --------
        @staticmethod
        def authenticate(email, password):
            try:
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
                user = cursor.fetchone()

                if not user:
                    logger.info("Auth failed: user not found")
                    return None

                if not check_password_hash(user["password"], password):
                    logger.info("Auth failed: wrong password")
                    return None

                logger.info("Auth success")
                return User(**user)

            except Exception as e:
                logger.error(f"Auth error: {e}")
                return None

        # -------- Validators --------
        @staticmethod
        def is_valid_email(email):
            return re.match(r"^[^@]+@[^@]+\.[^@]+$", email)

        @staticmethod
        def is_valid_username(username):
            return re.match(r"^[a-zA-Z0-9_]{3,50}$", username)

        @staticmethod
        def is_valid_password(password):
            return len(password) >= 6

        # -------- Admin helpers --------
        @staticmethod
        def get_all():
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute(
                "SELECT id, username, email, user_type, created_at FROM users"
            )
            return cursor.fetchall()

        @staticmethod
        def get_count():
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT COUNT(*) AS count FROM users")
            return cursor.fetchone()["count"]


    # =========================
    # CONTACT MESSAGES
    # =========================
    class ContactMessage:
        @staticmethod
        def create(name, email, phone, message):
            cursor = mysql.connection.cursor()
            cursor.execute(
                "INSERT INTO contact_messages (name,email,phone,message) VALUES (%s,%s,%s,%s)",
                (name, email, phone, message)
            )
            mysql.connection.commit()
            return True

        @staticmethod
        def get_all():
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("SELECT * FROM contact_messages ORDER BY created_at DESC")
            return cursor.fetchall()

        @staticmethod
        def get_count():
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT COUNT(*) AS count FROM contact_messages")
            return cursor.fetchone()["count"]


    # =========================
    # PRODUCTS
    # =========================
    class Product:
        @staticmethod
        def get_all():
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute(
                "SELECT * FROM products WHERE available_offline=1 ORDER BY created_at DESC"
            )
            products = cursor.fetchall()
            for p in products:
                p["features"] = json.loads(p["features"] or "[]")
            return products

        @staticmethod
        def create(name, description, price, duration_days=30, features=None):
            cursor = mysql.connection.cursor()
            cursor.execute(
                """INSERT INTO products (name,description,price,duration_days,features)
                   VALUES (%s,%s,%s,%s,%s)""",
                (name, description, price, duration_days, json.dumps(features or []))
            )
            mysql.connection.commit()
            return True

        @staticmethod
        def delete(product_id):
            cursor = mysql.connection.cursor()
            cursor.execute("DELETE FROM products WHERE id=%s", (product_id,))
            mysql.connection.commit()
            return True

        @staticmethod
        def get_count():
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT COUNT(*) AS count FROM products")
            return cursor.fetchone()["count"]


    # =========================
    # USER PROFILE
    # =========================
    class UserProfile:
        @staticmethod
        def get(user_id):
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute(
                "SELECT * FROM user_profiles WHERE user_id=%s", (user_id,)
            )
            return cursor.fetchone()

        @staticmethod
        def save(user_id, data):
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute(
                "SELECT id FROM user_profiles WHERE user_id=%s", (user_id,)
            )
            exists = cursor.fetchone()

            if exists:
                cursor.execute(
                    """UPDATE user_profiles SET
                       full_name=%s, phone=%s, age=%s, gender=%s,
                       height=%s, weight=%s, goal=%s,
                       medical_conditions=%s, dietary_preferences=%s
                       WHERE user_id=%s""",
                    (*data.values(), user_id)
                )
            else:
                cursor.execute(
                    """INSERT INTO user_profiles
                       (user_id, full_name, phone, age, gender,
                        height, weight, goal, medical_conditions, dietary_preferences)
                       VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                    (user_id, *data.values())
                )

            mysql.connection.commit()
            return True


    return User, ContactMessage, Product, UserProfile
