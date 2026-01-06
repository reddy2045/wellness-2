# test_mysql.py
import mysql.connector

print("="*60)
print("MySQL CONNECTION TEST")
print("="*60)

try:
    # Try to connect
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Reddy@123",
        database="wellness_coach"
    )
    
    print("Connected to MySQL!")
    
    cursor = conn.cursor(dictionary=True)
    
    # Check current data
    cursor.execute("SELECT * FROM contact_messages")
    messages = cursor.fetchall()
    
    print(f"\n Found {len(messages)} messages in contact_messages table:")
    print("-"*60)
    for msg in messages:
        print(f"ID: {msg['id']}, Name: {msg['name']}, Email: {msg['email']}, Status: {msg['status']}")
    print("-"*60)
    
    # Try to insert a test record
    print("\n Attempting to insert test record...")
    insert_sql = """
        INSERT INTO contact_messages 
        (name, email, phone, subject, message, status) 
        VALUES (%s, %s, %s, %s, %s, 'new')
    """
    
    test_data = ('Python Test', 'python@test.com', '9876543210', 
                'Python Connection Test', 'Testing direct connection')
    
    cursor.execute(insert_sql, test_data)
    conn.commit()
    
    print(" Test record inserted successfully!")
    
    # Check new count
    cursor.execute("SELECT * FROM contact_messages ORDER BY id DESC LIMIT 3")
    new_messages = cursor.fetchall()
    
    print("\n Latest 3 messages:")
    for msg in new_messages:
        print(f"ID: {msg['id']}, Name: {msg['name']}, Email: {msg['email']}")
    
    cursor.close()
    conn.close()
    
    print("\n" + "="*60)
    print(" CONNECTION TEST SUCCESSFUL!")
    print("="*60)
    
except mysql.connector.Error as err:
    print(f" MySQL Error: {err}")
    print("\nTroubleshooting steps:")
    print("1. Check if MySQL is running: sudo service mysql status")
    print("2. Check password (using: Reddy@123)")
    print("3. Check if database 'wellness_coach' exists")
    print("4. Check if table 'contact_messages' exists in that database")
    
except Exception as e:
    print(f" General Error: {e}")