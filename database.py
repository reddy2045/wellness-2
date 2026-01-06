from flask_mysqldb import MySQL
import MySQLdb.cursors

mysql = MySQL()

def init_db(app):
    app.config['MYSQL_HOST'] = app.config['MYSQL_HOST']
    app.config['MYSQL_USER'] = app.config['MYSQL_USER']
    app.config['MYSQL_PASSWORD'] = app.config['MYSQL_PASSWORD']
    app.config['MYSQL_DB'] = app.config['MYSQL_DB']
    app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
    
    mysql.init_app(app)
    
    # Create table if not exists
    with app.app_context():
        cursor = mysql.connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS contact_messages (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(150) NOT NULL,
                phone VARCHAR(15) NOT NULL,
                subject VARCHAR(200) NOT NULL,
                message TEXT NOT NULL,
                status ENUM('new', 'read', 'replied') DEFAULT 'new',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ip_address VARCHAR(45),
                user_agent TEXT,
                INDEX idx_email (email),
                INDEX idx_status (status),
                INDEX idx_created_at (created_at)
            )
        ''')
        mysql.connection.commit()
        cursor.close()