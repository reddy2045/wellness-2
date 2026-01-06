import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

load_dotenv()

def create_connection():
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME')
        )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def init_db():
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        
        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(80) UNIQUE NOT NULL,
                email VARCHAR(120) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                profile_pic VARCHAR(255),
                weight DECIMAL(5,2),
                height DECIMAL(5,2),
                age INT,
                fitness_goal VARCHAR(100),
                medical_history TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_admin BOOLEAN DEFAULT FALSE
            )
        """)
        
        # Create wellness_logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS wellness_logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                log_date DATE NOT NULL,
                sleep_hours DECIMAL(4,2),
                water_intake_liters DECIMAL(4,2),
                calories_consumed INT,
                calories_burned INT,
                mood VARCHAR(50),
                notes TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        
        # Create workouts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS workouts (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                workout_date DATE NOT NULL,
                workout_type VARCHAR(100),
                duration_minutes INT,
                intensity VARCHAR(50),
                notes TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        
        # Create nutrition_logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS nutrition_logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                meal_date DATE NOT NULL,
                meal_type VARCHAR(50),
                food_item VARCHAR(200),
                calories INT,
                protein_g DECIMAL(5,2),
                carbs_g DECIMAL(5,2),
                fats_g DECIMAL(5,2),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        
        connection.commit()
        cursor.close()
        connection.close()
        print("Database initialized successfully!")

if __name__ == "__main__":
    init_db()