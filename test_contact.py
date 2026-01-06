import requests
import json

# Test URL
url = "http://localhost:5000/contact"

# Test data
test_data = {
    'name': 'John Doe',
    'email': 'john@example.com',
    'phone': '9876543210',
    'subject': 'Test Inquiry',
    'message': 'This is a test message from the test script.'
}

try:
    response = requests.post(url, data=test_data)
    print(f"Status Code: {response.status_code}")
    print(f"Response URL: {response.url}")
    print(f"Response Text: {response.text[:500]}")
    
    if response.status_code == 200:
        print("Test passed! Form submitted successfully.")
    else:
        print(" Test failed!")
        
except Exception as e:
    print(f" Error: {e}")