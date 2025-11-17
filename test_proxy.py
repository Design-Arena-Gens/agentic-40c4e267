#!/usr/bin/env python3
"""
Quick proxy test to verify it works
"""
from curl_cffi import requests as curl_requests

PROXY_CONFIG = {
    "username": "c147d949a38ca89c4c3a__cr.au,gb,us",
    "password": "b7351118825adfbd",
    "server": "gw.dataimpulse.com",
    "port": "823"
}

PROXY_URL = f"http://{PROXY_CONFIG['username']}:{PROXY_CONFIG['password']}@{PROXY_CONFIG['server']}:{PROXY_CONFIG['port']}"

print("Testing proxy connection...")
print(f"Proxy: {PROXY_CONFIG['server']}:{PROXY_CONFIG['port']}")

try:
    # Test with a simple endpoint
    response = curl_requests.get(
        'https://api.ipify.org?format=json',
        proxies={'http': PROXY_URL, 'https': PROXY_URL},
        impersonate='chrome120',
        timeout=30
    )
    print(f"\n✓ Proxy works!")
    print(f"Response: {response.text}")
    print(f"Status: {response.status_code}")
except Exception as e:
    print(f"\n✗ Proxy test failed: {e}")

# Test the target site without proxy first
print("\n" + "="*60)
print("Testing target site WITHOUT proxy...")
try:
    response = curl_requests.get(
        'https://www.realestate.com.au/',
        impersonate='chrome120',
        timeout=30
    )
    print(f"Status: {response.status_code}")
    print(f"Content length: {len(response.text)}")
    if "429" in str(response.status_code):
        print("Rate limited without proxy")
except Exception as e:
    print(f"Error: {e}")

# Test target with proxy
print("\n" + "="*60)
print("Testing target site WITH proxy...")
try:
    response = curl_requests.get(
        'https://www.realestate.com.au/',
        proxies={'http': PROXY_URL, 'https': PROXY_URL},
        impersonate='chrome120',
        timeout=30
    )
    print(f"Status: {response.status_code}")
    print(f"Content length: {len(response.text)}")
    if response.status_code == 429:
        print("⚠️  Rate limited WITH proxy - Kasada detected us")
        print("This confirms we need a full browser with JS execution")
except Exception as e:
    print(f"Error: {e}")
