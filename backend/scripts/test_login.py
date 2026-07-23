"""Quick script to test login API"""
import json
import urllib.request

def test():
    url = "http://localhost:8000/api/v1/auth/login"
    
    # Test customer login
    payload = json.dumps({"identifier": "customer@gmail.com", "password": "customer123"}).encode()
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as r:
            data = json.loads(r.read())
            print(f"[customer] Status: {r.status}")
            print(f"  Token: {data['access_token'][:50]}...")
            print(f"  User: {data['user']['full_name']} - Role: {[r['code'] for r in data['user']['roles']]}")
    except urllib.error.HTTPError as e:
        print(f"[customer] Status: {e.code}")
        print(f"  Error: {e.read().decode()}")
    
    # Test admin login
    payload2 = json.dumps({"identifier": "admin@cineai.vn", "password": "admin123"}).encode()
    req2 = urllib.request.Request(url, data=payload2, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req2) as r:
            data = json.loads(r.read())
            print(f"[admin] Status: {r.status}")
            print(f"  Token: {data['access_token'][:50]}...")
            print(f"  User: {data['user']['full_name']} - Role: {[r['code'] for r in data['user']['roles']]}")
    except urllib.error.HTTPError as e:
        print(f"[admin] Status: {e.code}")
        print(f"  Error: {e.read().decode()}")

test()

