import requests
import json

print("="*60)
print("TEST FORM SUBMISSION")
print("="*60)

# Test data matching your form
test_data = {
    'name': 'John Doe',
    'email': 'john@example.com',
    'phone': '9876543210',
    'subject': 'Program Inquiry',
    'message': 'I would like to know more about your weight loss program.',
    'source': 'website_contact',
    'page': 'home'
}

url = "http://localhost:5000/contact"

try:
    print(f" Sending POST request to: {url}")
    print(f" Data: {json.dumps(test_data, indent=2)}")
    
    response = requests.post(url, data=test_data)
    
    print(f"\n Response:")
    print(f"   Status Code: {response.status_code}")
    print(f"   Response URL: {response.url}")
    print(f"   Response Size: {len(response.content)} bytes")
    
    if response.status_code == 200:
        print(" Form submitted successfully!")
        print("\n Check your database with:")
        print("   mysql> SELECT * FROM wellness_coach.contact_messages;")
    else:
        print(f" Unexpected status code: {response.status_code}")
        print(f"   Response text: {response.text[:500]}")
        
except Exception as e:
    print(f" Error: {e}")