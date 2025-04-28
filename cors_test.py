#!/usr/bin/env python3
"""
Simple script to test CORS configuration
Run this file directly to test CORS headers
"""
import requests
import json
import sys

def test_cors(url, origin):
    """Test CORS configuration for a URL"""
    # Test OPTIONS request (preflight)
    headers = {
        'Origin': origin,
        'Access-Control-Request-Method': 'POST',
        'Access-Control-Request-Headers': 'Content-Type, Authorization'
    }
    
    print(f"Testing OPTIONS request to {url} with origin {origin}...")
    try:
        response = requests.options(url, headers=headers, timeout=10)
        print(f"Status: {response.status_code}")
        print("Headers:")
        for key, value in response.headers.items():
            if key.lower().startswith('access-control'):
                print(f"  {key}: {value}")
        
        # Check for required headers
        if 'Access-Control-Allow-Origin' in response.headers:
            if response.headers['Access-Control-Allow-Origin'] == origin:
                print("✅ Access-Control-Allow-Origin header is correct")
            else:
                print(f"❌ Access-Control-Allow-Origin header is incorrect: {response.headers['Access-Control-Allow-Origin']}")
        else:
            print("❌ Access-Control-Allow-Origin header is missing")
            
        if 'Access-Control-Allow-Credentials' in response.headers:
            if response.headers['Access-Control-Allow-Credentials'].lower() == 'true':
                print("✅ Access-Control-Allow-Credentials header is correct")
            else:
                print(f"❌ Access-Control-Allow-Credentials header is incorrect: {response.headers['Access-Control-Allow-Credentials']}")
        else:
            print("❌ Access-Control-Allow-Credentials header is missing")
            
    except Exception as e:
        print(f"Error testing OPTIONS request: {e}")
    
    print("\n")
    
    # Test GET request
    headers = {
        'Origin': origin
    }
    
    print(f"Testing GET request to {url}/api/cors-test with origin {origin}...")
    try:
        response = requests.get(f"{url}/api/cors-test", headers=headers, timeout=10)
        print(f"Status: {response.status_code}")
        print("Headers:")
        for key, value in response.headers.items():
            if key.lower().startswith('access-control'):
                print(f"  {key}: {value}")
        
        print("Response body:")
        try:
            print(json.dumps(response.json(), indent=2))
        except:
            print(response.text[:200] + "..." if len(response.text) > 200 else response.text)
            
    except Exception as e:
        print(f"Error testing GET request: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python cors_test.py <api_url> <origin>")
        print("Example: python cors_test.py https://api.loyhaofisi.uz http://localhost:3000")
        sys.exit(1)
        
    api_url = sys.argv[1]
    origin = sys.argv[2]
    
    test_cors(api_url, origin)
