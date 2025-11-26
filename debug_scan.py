from agents import ScanAgent
import os

# Mock API key if needed or rely on fallback
# os.environ["NEWSDATA_API_KEY"] = "test"

agent = ScanAgent()
print("--- Starting Scan ---")
claims = agent.scan()
print(f"--- Scan Complete. Found {len(claims)} claims ---")
for c in claims:
    print(f"Claim: {c.text}")
    print(f"Status: {c.status}")
