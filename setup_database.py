import MySQLdb
from werkzeug.security import generate_password_hash
import sys

def setup_database():
    try:
        print("=" * 60)
        print("WELLNESS COACH DATABASE SETUP")
        print("=" * 60)
        
        # Step 1: Connect to MySQL
        print("Step 1: Connecting to MySQL...")
        connection = MySQLdb.connect(
            host="localhost",
            user="root",
            password="Reddy@123"
        )
        cursor = connection.cursor()
        
        # Step 2: Create database (using wellness_coach)
        print("Step 2: Creating database...")
        cursor.execute("DROP DATABASE IF EXISTS wellness_coach")
        cursor.execute("CREATE DATABASE IF NOT EXISTS wellness_coach")
        cursor.execute("USE wellness_coach")
        
        # Step 3: Create tables with proper structure
        print("Step 3: Creating tables...")
        
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(100) NOT NULL UNIQUE,
                email VARCHAR(100) NOT NULL UNIQUE,
                name VARCHAR(100) NOT NULL,
                password VARCHAR(255) NOT NULL,
                user_type VARCHAR(10) DEFAULT 'user',
                profile_image VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✓ Created 'users' table")
        
        # Products table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(200) NOT NULL,
                description TEXT,
                price DECIMAL(10,2) NOT NULL,
                duration VARCHAR(50),
                features TEXT,
                available_offline BOOLEAN DEFAULT TRUE,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✓ Created 'products' table")
        
        # Contact messages table - CORRECTED for Flask app
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS contact_messages (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) NOT NULL,
                phone VARCHAR(20),
                subject VARCHAR(200),
                message TEXT NOT NULL,
                status ENUM('new', 'read') DEFAULT 'new',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("Created 'contact_messages' table")
        
        # Reviews table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reviews (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                username VARCHAR(100),
                rating INT NOT NULL,
                review_text TEXT NOT NULL,
                is_approved BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
            )
        """)
        print("✓ Created 'reviews' table")
        
        # Success stories table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS success_stories (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                title VARCHAR(200) NOT NULL,
                description TEXT NOT NULL,
                before_image VARCHAR(255),
                after_image VARCHAR(255),
                weight_lost DECIMAL(5,2),
                time_period VARCHAR(50),
                is_approved BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
            )
        """)
        print("✓ Created 'success_stories' table")
        
        # Site settings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS site_settings (
                id INT AUTO_INCREMENT PRIMARY KEY,
                setting_key VARCHAR(50) UNIQUE NOT NULL,
                setting_value TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """)
        print("✓ Created 'site_settings' table")
        
        # Step 4: Insert admin user
        print("Step 4: Creating admin user...")
        admin_password = "admin@7671"
        hashed_password = generate_password_hash(admin_password)
        
        cursor.execute("""
            INSERT INTO users (username, email, name, password, user_type) 
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE 
            name=VALUES(name), password=VALUES(password), user_type=VALUES(user_type)
        """, ('admin', 'admin@wellness.com', 'Wellness Admin', hashed_password, 'admin'))
        print("✓ Created admin user")
        
        # Step 5: Insert sample data
        print("Step 5: Inserting sample data...")
        
        # Sample products
        sample_products = [
            ('Weight Loss Program', 'Complete 12-week weight loss transformation with personalized diet and exercise plans', 2999.00, '12 Weeks', 'Personalized meal plans, Weekly check-ins, Exercise routine, Progress tracking'),
            ('Muscle Building Program', 'Healthy muscle building and strength training program', 3499.00, '16 Weeks', 'Custom workout plan, Nutrition guide, Supplement advice, Progress photos'),
            ('Yoga & Meditation', 'Stress relief and flexibility improvement program', 1999.00, '8 Weeks', 'Daily yoga sessions, Meditation guides, Breathing exercises, Stress management'),
            ('Nutrition Counseling', 'Personalized nutrition and diet planning', 1499.00, '4 Weeks', 'Diet analysis, Meal planning, Grocery lists, Recipe suggestions'),
            ('Fitness for Beginners', 'Get started with fitness the right way', 2499.00, '6 Weeks', 'Basic exercises, Form correction, Safety tips, Gradual progression'),
            ('Advanced Bodybuilding', 'Take your physique to the next level', 4999.00, '20 Weeks', 'Advanced techniques, Competition prep, Peak week strategy, Posing guidance')
        ]
        
        for product in sample_products:
            cursor.execute("""
                INSERT INTO products (name, description, price, duration, features)
                VALUES (%s, %s, %s, %s, %s)
            """, product)
        print("✓ Added 6 sample products")
        
        # Sample contact messages
        sample_messages = [
            ('John Doe', 'john@example.com', '9876543210', 'Weight Loss Program Inquiry', 'Hello, I would like to know more about your weight loss program. What does it include?', 'new'),
            ('Jane Smith', 'jane@example.com', '8765432109', 'Feedback', 'Great service! The yoga program really helped with my flexibility.', 'read'),
            ('Raj Patel', 'raj@example.com', '7654321098', 'Diet Plan Question', 'Do you provide vegetarian meal plans? I am interested in the nutrition counseling.', 'new'),
            ('Priya Sharma', 'priya@example.com', '6543210987', 'Discount Query', 'Are there any discounts available for students?', 'new'),
            ('Mike Johnson', 'mike@example.com', '9876123450', 'Personal Training', 'Do you offer one-on-one personal training sessions?', 'read'),
            ('Sara Williams', 'sara@example.com', '8765094321', 'Success Story', 'I lost 15kg with your program! Thank you so much.', 'read')
        ]
        
        for msg in sample_messages:
            cursor.execute("""
                INSERT INTO contact_messages (name, email, phone, subject, message, status)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, msg)
        print("✓ Added 6 sample contact messages")
        
        # Sample reviews
        sample_reviews = [
            (1, 'John Doe', 5, 'Amazing program! Lost 10kg in 3 months. Highly recommended!', True),
            (2, 'Jane Smith', 4, 'Great yoga sessions. Helped reduce my back pain significantly.', True),
            (None, 'Anonymous', 5, 'Best fitness coach ever! Transformed my life completely.', True),
            (None, 'Robert Brown', 4, 'Good nutrition advice. Meal plans were easy to follow.', False),
            (None, 'Lisa Taylor', 5, 'The muscle building program gave me great results!', True)
        ]
        
        for review in sample_reviews:
            cursor.execute("""
                INSERT INTO reviews (user_id, username, rating, review_text, is_approved)
                VALUES (%s, %s, %s, %s, %s)
            """, review)
        print("✓ Added 5 sample reviews")
        
        # Sample success stories
        sample_stories = [
            (1, 'From 100kg to 75kg in 6 Months!', 'I was struggling with weight issues for years. With the weight loss program, I transformed completely. The diet plan was easy to follow and the exercises were effective.', 'before1.jpg', 'after1.jpg', 25.0, '6 Months', True),
            (None, 'Gained 10kg of Muscle Mass', 'As a hard gainer, I never thought I could build muscle. This program changed everything! Proper nutrition and training made the difference.', 'before2.jpg', 'after2.jpg', -10.0, '8 Months', True),
            (None, 'Yoga Changed My Life', 'Chronic back pain was affecting my daily life. After the yoga program, I feel like a new person. Flexibility improved and pain reduced by 90%.', 'before3.jpg', 'after3.jpg', 0, '3 Months', False)
        ]
        
        for story in sample_stories:
            cursor.execute("""
                INSERT INTO success_stories (user_id, title, description, before_image, after_image, weight_lost, time_period, is_approved)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, story)
        print("✓ Added 3 sample success stories")
        
        # Sample site settings
        sample_settings = [
            ('site_name', 'Wellness Coach'),
            ('site_email', 'contact@wellnesscoach.com'),
            ('site_phone', '+91 9876543210'),
            ('site_address', '123 Fitness Street, Health City'),
            ('footer_text', '© 2024 Wellness Coach. All rights reserved.'),
            ('facebook_url', 'https://facebook.com/wellnesscoach'),
            ('instagram_url', 'https://instagram.com/wellnesscoach'),
            ('twitter_url', 'https://twitter.com/wellnesscoach')
        ]
        
        for setting in sample_settings:
            cursor.execute("""
                INSERT INTO site_settings (setting_key, setting_value)
                VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE setting_value=VALUES(setting_value)
            """, setting)
        print("✓ Added site settings")
        
        connection.commit()
        cursor.close()
        connection.close()
        
        print("\n" + "=" * 60)
        print(" DATABASE SETUP COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("✓ Database: wellness_coach")
        print("✓ Tables created: users, products, contact_messages, reviews, success_stories, site_settings")
        print("\n Admin Login Credentials:")
        print("   Email: admin@wellness.com")
        print("   Password: admin@7671")
        print("\n Sample Data Added:")
        print("   • 6 Products")
        print("   • 6 Contact Messages (3 new, 3 read)")
        print("   • 5 Reviews (4 approved, 1 pending)")
        print("   • 3 Success Stories (2 approved, 1 pending)")
        print("=" * 60)
        print("\n Next Steps:")
        print("1. Update Flask app configuration:")
        print("   app.config['MYSQL_DB'] = 'wellness_coach'")
        print("2. Run: python app.py")
        print("3. Open: http://localhost:5000")
        print("4. Admin Panel: http://localhost:5000/admin")
        print("=" * 60)
        
        return True
        
    except MySQLdb.Error as e:
        print(f"\n MySQL Error: {e}")
        print("\n Troubleshooting:")
        print("1. Make sure MySQL server is running")
        print("2. Check MySQL credentials (user: root, password: Reddy@123)")
        print("3. Verify MySQL installation")
        print("4. Try connecting manually: mysql -u root -p")
        return False
    except Exception as e:
        print(f"\n Error: {e}")
        return False

if __name__ == "__main__":
    success = setup_database()
    if success:
        sys.exit(0)
    else:
        sys.exit(1)