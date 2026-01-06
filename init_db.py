import pymysql
from werkzeug.security import generate_password_hash
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_tables():
    """Create database tables"""
    connection = None
    cursor = None
    
    try:
        # Connect to MySQL
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='Reddy@123',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        cursor = connection.cursor()
        
        # Create database if not exists
        cursor.execute("CREATE DATABASE IF NOT EXISTS wellness_coach CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        cursor.execute("USE wellness_coach")
        
        # Drop tables if they exist (in correct order)
        cursor.execute("DROP TABLE IF EXISTS success_stories")
        cursor.execute("DROP TABLE IF EXISTS reviews")
        cursor.execute("DROP TABLE IF EXISTS contact_messages")
        cursor.execute("DROP TABLE IF EXISTS products")
        cursor.execute("DROP TABLE IF EXISTS users")
        
        # Create users table
        cursor.execute('''
            CREATE TABLE users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(100) NOT NULL UNIQUE,
                email VARCHAR(100) NOT NULL UNIQUE,
                name VARCHAR(100) NOT NULL,
                password VARCHAR(255) NOT NULL,
                user_type ENUM('user', 'admin') DEFAULT 'user',
                profile_image VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''')
        
        # Create products table
        cursor.execute('''
            CREATE TABLE products (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(200) NOT NULL,
                description TEXT,
                price DECIMAL(10,2) NOT NULL DEFAULT 0.00,
                duration VARCHAR(50),
                features JSON,
                available_offline BOOLEAN DEFAULT TRUE,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''')
        
        # Create reviews table
        cursor.execute('''
            CREATE TABLE reviews (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                username VARCHAR(100),
                rating INT NOT NULL,
                review_text TEXT NOT NULL,
                status ENUM('pending', 'approved', 'rejected') DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL ON UPDATE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''')
        
        # Create success_stories table
        cursor.execute('''
            CREATE TABLE success_stories (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                title VARCHAR(200) NOT NULL,
                description TEXT NOT NULL,
                before_image VARCHAR(255),
                after_image VARCHAR(255),
                weight_lost DECIMAL(5,2),
                time_period VARCHAR(50),
                status ENUM('pending', 'approved', 'rejected') DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE ON UPDATE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''')
        
        # Create contact_messages table
        cursor.execute('''
            CREATE TABLE contact_messages (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) NOT NULL,
                phone VARCHAR(20),
                subject VARCHAR(200),
                message TEXT NOT NULL,
                status ENUM('new', 'read', 'replied') DEFAULT 'new',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''')
        
        # Insert admin user
        admin_password = generate_password_hash('admin@7671')
        cursor.execute('''
            INSERT INTO users (username, email, name, password, user_type) 
            VALUES (%s, %s, %s, %s, %s)
        ''', ('admin', 'admin@wellness.com', 'Wellness Admin', admin_password, 'admin'))
        
        # Insert sample users
        sample_users = [
            ('anjali', 'anjali@example.com', 'Anjali Sharma', generate_password_hash('password123'), 'user'),
            ('rajesh', 'rajesh@example.com', 'Rajesh Kumar', generate_password_hash('password123'), 'user'),
            ('priya', 'priya@example.com', 'Priya Reddy', generate_password_hash('password123'), 'user'),
            ('suresh', 'suresh@example.com', 'Suresh Verma', generate_password_hash('password123'), 'user'),
            ('meena', 'meena@example.com', 'Meena Patel', generate_password_hash('password123'), 'user')
        ]
        
        cursor.executemany('''
            INSERT INTO users (username, email, name, password, user_type) 
            VALUES (%s, %s, %s, %s, %s)
        ''', sample_users)
        
        # Get user IDs
        cursor.execute('SELECT id, name FROM users WHERE user_type = "user"')
        users = cursor.fetchall()
        
        # Insert sample products
        sample_products = [
            ('Weight Loss Program', 'Complete 12-week weight loss transformation with personalized diet and exercise plans', 2999.00, '12 Weeks', '["Personalized meal plans", "Weekly check-ins", "Progress tracking", "Exercise routines", "WhatsApp support"]'),
            ('Weight Gain Program', 'Healthy weight gain program focused on building muscle mass and proper nutrition', 3499.00, '8 Weeks', '["Calorie-dense meal plans", "Strength training", "Supplement guidance", "Progress monitoring"]'),
            ('Personalized Nutrition Plan', 'Customized nutrition plan based on your body type, lifestyle, and goals', 1999.00, '4 Weeks', '["Detailed diet charts", "Grocery shopping lists", "Recipe suggestions", "Nutrition education"]'),
            ('Fitness Coaching', 'One-on-one fitness coaching sessions with expert guidance', 2499.00, '1 Month', '["Custom workout plans", "Form correction", "Video sessions", "Weekly assessments"]'),
            ('Heart Health Program', 'Cardiovascular wellness program for better heart health', 2799.00, '6 Weeks', '["BP monitoring", "Heart-healthy recipes", "Cardio exercises", "Stress management"]'),
            ('Mental Wellness', 'Stress management and mindfulness techniques program', 2299.00, '8 Weeks', '["Meditation guides", "Sleep improvement", "Anxiety management", "Mindfulness training"]'),
            ('Diabetes Management', 'Specialized program for diabetes control and management', 3299.00, '12 Weeks', '["Sugar monitoring", "Diabetic diet plans", "Exercise guidance", "Lifestyle changes"]'),
            ('Post Pregnancy Weight Loss', 'Safe weight loss program for new mothers', 3799.00, '16 Weeks', '["Postpartum exercises", "Breastfeeding-friendly diet", "Core strengthening", "Gentle workouts"]')
        ]
        
        cursor.executemany('''
            INSERT INTO products (name, description, price, duration, features) 
            VALUES (%s, %s, %s, %s, %s)
        ''', sample_products)
        
        # Insert sample reviews
        if users:
            sample_reviews = [
                (users[0]['id'], users[0]['name'], 5, 'I lost 12 kg in just 3 months! The personalized diet plan was easy to follow and I never felt deprived. Highly recommended!'),
                (users[1]['id'] if len(users) > 1 else 1, users[1]['name'] if len(users) > 1 else 'Rajesh Kumar', 5, 'As a diabetic, I was struggling to manage my weight. This program helped me control my sugar levels and lose 8 kg. Thank you!'),
                (users[2]['id'] if len(users) > 2 else 1, users[2]['name'] if len(users) > 2 else 'Priya Reddy', 4, 'The weight gain program helped me put on healthy weight. I feel more confident and energetic now. Great guidance!'),
                (users[3]['id'] if len(users) > 3 else 1, users[3]['name'] if len(users) > 3 else 'Suresh Verma', 5, 'Best investment in my health. The coach is very supportive and the plans are practical. Lost 15kg in 4 months!'),
                (users[4]['id'] if len(users) > 4 else 1, users[4]['name'] if len(users) > 4 else 'Meena Patel', 5, 'Post-pregnancy weight loss was challenging, but this program made it easy and safe. Lost 10kg while breastfeeding!')
            ]
            
            cursor.executemany('''
                INSERT INTO reviews (user_id, username, rating, review_text, status) 
                VALUES (%s, %s, %s, %s, "approved")
            ''', sample_reviews)
        
        # Insert sample success stories
        if users:
            sample_stories = [
                (users[0]['id'], 'My Weight Loss Journey', 'Lost 15kg in 3 months with proper diet and exercise. Feeling healthier than ever!', 15.0, '3 Months'),
                (users[1]['id'] if len(users) > 1 else 1, 'Diabetes Under Control', 'Reduced HbA1c from 8.5 to 6.2 with customized diet plan. No more medications!', 8.5, '4 Months'),
                (users[2]['id'] if len(users) > 2 else 1, 'Healthy Weight Gain', 'Gained 5kg of muscle mass with proper nutrition and strength training. Feeling strong!', -5.0, '2 Months')
            ]
            
            cursor.executemany('''
                INSERT INTO success_stories (user_id, title, description, weight_lost, time_period, status) 
                VALUES (%s, %s, %s, %s, %s, "approved")
            ''', sample_stories)
        
        connection.commit()
        logger.info("Database created and populated successfully!")
        
    except Exception as e:
        logger.error(f"Error creating database: {e}")
        if connection:
            connection.rollback()
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

if __name__ == "__main__":
    create_tables()