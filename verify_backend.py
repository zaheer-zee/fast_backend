from fastapi.testclient import TestClient
from main import app
from models import Claim
import os

# Disable API keys for testing to rely on mocks/fallbacks
# API keys are loaded from .env via agents.py or environment
# os.environ["GROQ_API_KEY"] = ""  <-- Removed to allow real keys
# os.environ["NEWSDATA_API_KEY"] = "" <-- Removed to allow real keys

# Check for API Keys
print("--- API Key Check ---")
if os.getenv("GROQ_API_KEY"):
    print("✅ GROQ_API_KEY found.")
else:
    print("⚠️  GROQ_API_KEY missing. Scoring and Explanations will use fallbacks.")

if os.getenv("NEWSDATA_API_KEY"):
    print("✅ NEWSDATA_API_KEY found.")
else:
    print("⚠️  NEWSDATA_API_KEY missing. ScanAgent will use mock data.")
print("---------------------")

client = TestClient(app)

def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "CruxAI System Online"}
    print("Health check passed.")

def test_verify_claim():
    # Test verify endpoint
    response = client.post("/api/verify", json={"text": "Test claim"})
    assert response.status_code == 200
    data = response.json()
    assert "claim" in data
    assert "score" in data
    assert data["claim"]["text"] == "Test claim"
    # Since we have no keys, it should return default/fallback values
    assert data["score"]["verdict"] == "UNVERIFIED"
    print("Verify claim passed.")

def test_crisis_endpoint():
    # Inject a crisis claim manually
    from main import processed_claims
    processed_claims.append(Claim(
        text="Major earthquake reported",
        status="verified"
    ))
    
    response = client.get("/api/crisis")
    assert response.status_code == 200
    data = response.json()
    # Should detect crisis because "earthquake" is a keyword
    assert data["crisis_detected"] is True
    assert len(data["alerts"]) > 0
    assert data["alerts"][0]["title"] == "Potential Crisis Detected"
    print("Crisis endpoint passed.")

if __name__ == "__main__":
    try:
        test_health_check()
        test_verify_claim()
        test_crisis_endpoint()
        print("All tests passed!")
    except AssertionError as e:
        print(f"Test failed: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
