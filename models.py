from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import json
import logging

# Set up logging
logger = logging.getLogger(__name__)

def init_models(app, mysql):
    class User(UserMixin):
        def __init__(self, id, username, email, user_type, profile_image=None, created_at=None):
            self.id = id
            self.username = username
            self.email = email
            self.user_type = user_type
            self.profile_image = profile_image
            self.created_at = created_at
            self.is_authenticated = True
            self.is_active = True
            self.is_anonymous = False

        def get_id(self):
            return str(self.id)

        @staticmethod
        def get(user_id, mysql):
            try:
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
                user = cursor.fetchone()
                if user:
                    return User(
                        id=user['id'],
                        username=user['username'],
                        email=user['email'],
                        user_type=user['user_type'],
                        profile_image=user['profile_image'],
                        created_at=user['created_at']
                    )
                return None
            except Exception as e:
                logger.error(f"Error getting user {user_id}: {e}")
                return None

        @staticmethod
        def create(username, email, password, user_type='user', mysql=None):
            try:
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                
                # Check if user already exists by email or username
                cursor.execute('SELECT * FROM users WHERE email = %s OR username = %s', (email, username))
                account = cursor.fetchone()
                
                if account:
                    return None, "Account with this email or username already exists!"
                elif not User.is_valid_email(email):
                    return None, "Invalid email address!"
                elif not User.is_valid_username(username):
                    return None, "Username must contain only letters, numbers, and underscores!"
                elif not User.is_valid_password(password):
                    return None, "Password must be at least 6 characters long!"
                else:
                    hashed_password = generate_password_hash(password)
                    cursor.execute(
                        'INSERT INTO users (username, email, password, user_type) VALUES (%s, %s, %s, %s)',
                        (username, email, hashed_password, user_type)
                    )
                    mysql.connection.commit()
                    
                    # Get the newly created user
                    cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
                    new_user = cursor.fetchone()
                    user_obj = User(
                        id=new_user['id'],
                        username=new_user['username'],
                        email=new_user['email'],
                        user_type=new_user['user_type']
                    )
                    return user_obj, "Registration successful!"
            except Exception as e:
                logger.error(f"Error creating user {email}: {e}")
                return None, "An error occurred during registration. Please try again."

        @staticmethod
        def authenticate(email, password, mysql):
            try:
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
                user = cursor.fetchone()
                
                if user and check_password_hash(user['password'], password):
                    return User(
                        id=user['id'],
                        username=user['username'],
                        email=user['email'],
                        user_type=user['user_type'],
                        profile_image=user['profile_image'],
                        created_at=user['created_at']
                    )
                return None
            except Exception as e:
                logger.error(f"Error authenticating user {email}: {e}")
                return None

        @staticmethod
        def update_profile(user_id, username, email, mysql):
            try:
                cursor = mysql.connection.cursor()
                cursor.execute(
                    'UPDATE users SET username = %s, email = %s WHERE id = %s',
                    (username, email, user_id)
                )
                mysql.connection.commit()
                return True
            except Exception as e:
                logger.error(f"Error updating profile for user {user_id}: {e}")
                return False

        @staticmethod
        def update_profile_image(user_id, filename, mysql):
            try:
                cursor = mysql.connection.cursor()
                cursor.execute(
                    'UPDATE users SET profile_image = %s WHERE id = %s',
                    (filename, user_id)
                )
                mysql.connection.commit()
                return True
            except Exception as e:
                logger.error(f"Error updating profile image for user {user_id}: {e}")
                return False

        @staticmethod
        def is_valid_email(email):
            pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            return re.match(pattern, email) is not None

        @staticmethod
        def is_valid_username(username):
            pattern = r'^[a-zA-Z0-9_]{3,50}$'
            return re.match(pattern, username) is not None

        @staticmethod
        def is_valid_password(password):
            return len(password) >= 6

        @staticmethod
        def get_all(mysql):
            try:
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute('SELECT id, username, email, user_type, created_at FROM users ORDER BY created_at DESC')
                return cursor.fetchall()
            except Exception as e:
                logger.error(f"Error getting all users: {e}")
                return []

        @staticmethod
        def get_count(mysql):
            try:
                cursor = mysql.connection.cursor()
                cursor.execute('SELECT COUNT(*) as count FROM users')
                result = cursor.fetchone()
                return result['count'] if result else 0
            except Exception as e:
                logger.error(f"Error getting user count: {e}")
                return 0

    class ContactMessage:
        @staticmethod
        def create(name, email, phone, message, mysql):
            try:
                cursor = mysql.connection.cursor()
                cursor.execute(
                    'INSERT INTO contact_messages (name, email, phone, message) VALUES (%s, %s, %s, %s)',
                    (name, email, phone, message)
                )
                mysql.connection.commit()
                return True
            except Exception as e:
                logger.error(f"Error creating contact message from {email}: {e}")
                return False

        @staticmethod
        def get_all(mysql):
            try:
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute('SELECT * FROM contact_messages ORDER BY created_at DESC')
                return cursor.fetchall()
            except Exception as e:
                logger.error(f"Error getting all contact messages: {e}")
                return []

        @staticmethod
        def get_by_id(message_id, mysql):
            try:
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute('SELECT * FROM contact_messages WHERE id = %s', (message_id,))
                return cursor.fetchone()
            except Exception as e:
                logger.error(f"Error getting contact message {message_id}: {e}")
                return None

        @staticmethod
        def update_status(message_id, status, mysql):
            try:
                cursor = mysql.connection.cursor()
                cursor.execute(
                    'UPDATE contact_messages SET status = %s WHERE id = %s',
                    (status, message_id)
                )
                mysql.connection.commit()
                return True
            except Exception as e:
                logger.error(f"Error updating message status {message_id}: {e}")
                return False

        @staticmethod
        def delete(message_id, mysql):
            try:
                cursor = mysql.connection.cursor()
                cursor.execute('DELETE FROM contact_messages WHERE id = %s', (message_id,))
                mysql.connection.commit()
                return True
            except Exception as e:
                logger.error(f"Error deleting contact message {message_id}: {e}")
                return False

        @staticmethod
        def get_count(mysql):
            try:
                cursor = mysql.connection.cursor()
                cursor.execute('SELECT COUNT(*) as count FROM contact_messages')
                result = cursor.fetchone()
                return result['count'] if result else 0
            except Exception as e:
                logger.error(f"Error getting contact messages count: {e}")
                return 0

    class Product:
        @staticmethod
        def get_all(mysql):
            try:
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute('SELECT * FROM products WHERE available_offline = TRUE ORDER BY created_at DESC')
                products = cursor.fetchall()
                # Parse JSON features
                for product in products:
                    if product.get('features'):
                        try:
                            product['features'] = json.loads(product['features'])
                        except (json.JSONDecodeError, TypeError):
                            product['features'] = []
                    else:
                        product['features'] = []
                return products
            except Exception as e:
                logger.error(f"Error getting all products: {e}")
                return []

        @staticmethod
        def create(name, description, price, available_offline=True, duration_days=30, features=None, mysql=None):
            try:
                cursor = mysql.connection.cursor()
                features_json = json.dumps(features) if features else '[]'
                cursor.execute(
                    'INSERT INTO products (name, description, price, available_offline, duration_days, features) VALUES (%s, %s, %s, %s, %s, %s)',
                    (name, description, price, available_offline, duration_days, features_json)
                )
                mysql.connection.commit()
                return True
            except Exception as e:
                logger.error(f"Error creating product {name}: {e}")
                return False

        @staticmethod
        def get_by_id(product_id, mysql):
            try:
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute('SELECT * FROM products WHERE id = %s', (product_id,))
                product = cursor.fetchone()
                if product and product.get('features'):
                    try:
                        product['features'] = json.loads(product['features'])
                    except (json.JSONDecodeError, TypeError):
                        product['features'] = []
                return product
            except Exception as e:
                logger.error(f"Error getting product {product_id}: {e}")
                return None

        @staticmethod
        def update(product_id, name, description, price, available_offline, mysql):
            try:
                cursor = mysql.connection.cursor()
                cursor.execute(
                    'UPDATE products SET name = %s, description = %s, price = %s, available_offline = %s WHERE id = %s',
                    (name, description, price, available_offline, product_id)
                )
                mysql.connection.commit()
                return True
            except Exception as e:
                logger.error(f"Error updating product {product_id}: {e}")
                return False

        @staticmethod
        def delete(product_id, mysql):
            try:
                cursor = mysql.connection.cursor()
                cursor.execute('DELETE FROM products WHERE id = %s', (product_id,))
                mysql.connection.commit()
                return True
            except Exception as e:
                logger.error(f"Error deleting product {product_id}: {e}")
                return False

        @staticmethod
        def get_count(mysql):
            try:
                cursor = mysql.connection.cursor()
                cursor.execute('SELECT COUNT(*) as count FROM products')
                result = cursor.fetchone()
                return result['count'] if result else 0
            except Exception as e:
                logger.error(f"Error getting products count: {e}")
                return 0

        @staticmethod
        def search(query, mysql):
            try:
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                search_pattern = f"%{query}%"
                cursor.execute(
                    'SELECT * FROM products WHERE (name LIKE %s OR description LIKE %s) AND available_offline = TRUE',
                    (search_pattern, search_pattern)
                )
                products = cursor.fetchall()
                for product in products:
                    if product.get('features'):
                        try:
                            product['features'] = json.loads(product['features'])
                        except (json.JSONDecodeError, TypeError):
                            product['features'] = []
                return products
            except Exception as e:
                logger.error(f"Error searching products with query {query}: {e}")
                return []

    class UserProfile:
        @staticmethod
        def create_or_update(user_id, full_name=None, phone=None, age=None, gender=None, 
                           height=None, weight=None, goal=None, medical_conditions=None, 
                           dietary_preferences=None, mysql=None):
            try:
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute('SELECT id FROM user_profiles WHERE user_id = %s', (user_id,))
                existing_profile = cursor.fetchone()
                
                if existing_profile:
                    cursor.execute('''UPDATE user_profiles SET 
                                    full_name = COALESCE(%s, full_name),
                                    phone = COALESCE(%s, phone),
                                    age = COALESCE(%s, age),
                                    gender = COALESCE(%s, gender),
                                    height = COALESCE(%s, height),
                                    weight = COALESCE(%s, weight),
                                    goal = COALESCE(%s, goal),
                                    medical_conditions = COALESCE(%s, medical_conditions),
                                    dietary_preferences = COALESCE(%s, dietary_preferences)
                                    WHERE user_id = %s''',
                                (full_name, phone, age, gender, height, weight, goal, 
                                 medical_conditions, dietary_preferences, user_id))
                else:
                    cursor.execute('''INSERT INTO user_profiles 
                                    (user_id, full_name, phone, age, gender, height, weight, goal, medical_conditions, dietary_preferences) 
                                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''',
                                (user_id, full_name, phone, age, gender, height, weight, goal, 
                                 medical_conditions, dietary_preferences))
                mysql.connection.commit()
                return True
            except Exception as e:
                logger.error(f"Error creating/updating user profile for user {user_id}: {e}")
                return False

        @staticmethod
        def get_by_user_id(user_id, mysql):
            try:
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute('SELECT * FROM user_profiles WHERE user_id = %s', (user_id,))
                return cursor.fetchone()
            except Exception as e:
                logger.error(f"Error getting user profile for user {user_id}: {e}")
                return None

        @staticmethod
        def delete(user_id, mysql):
            try:
                cursor = mysql.connection.cursor()
                cursor.execute('DELETE FROM user_profiles WHERE user_id = %s', (user_id,))
                mysql.connection.commit()
                return True
            except Exception as e:
                logger.error(f"Error deleting user profile for user {user_id}: {e}")
                return False

    return User, ContactMessage, Product, UserProfile