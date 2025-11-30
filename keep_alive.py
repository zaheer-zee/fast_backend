import time
import requests
import sys
from datetime import datetime

def keep_alive(url, interval=840):
    """
    Pings the specified URL every `interval` seconds (default 14 minutes).
    Render free tier spins down after 15 minutes of inactivity.
    """
    print(f"Starting keep-alive for {url}")
    print(f"Ping interval: {interval} seconds")
    
    while True:
        try:
            response = requests.get(url)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{timestamp}] Ping {url} - Status: {response.status_code}")
        except Exception as e:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{timestamp}] Error pinging {url}: {e}")
        
        time.sleep(interval)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python keep_alive.py <your-render-url>")
        print("Example: python keep_alive.py https://truth-weaver-backend.onrender.com")
        
        # Default fallback for convenience if user edits this file
        DEFAULT_URL = "https://truth-weaver-backend.onrender.com"
        print(f"\nNo URL provided. Using default: {DEFAULT_URL}")
        keep_alive(DEFAULT_URL)
    else:
        keep_alive(sys.argv[1])
