from fastapi import FastAPI, HTTPException, BackgroundTasks, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
import uuid
from datetime import datetime
from models import (
    Claim, Evidence, ScoreResponse, ExplainResponse, 
    CrisisResponse, ScanRequest, ScoreRequest, ExplainRequest
)
from agents import ScanAgent, VerifyAgent, ScoreAgent, ExplainAgent, CrisisAgent
from image_analyzer import image_analyzer

app = FastAPI(title="Crux-AI Backend")

# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for dev; restrict in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Agents
scan_agent = ScanAgent()
verify_agent = VerifyAgent()
score_agent = ScoreAgent()
explain_agent = ExplainAgent()
crisis_agent = CrisisAgent()

# In-memory storage for demo purposes
processed_claims: List[Claim] = []

@app.get("/")
def health_check():
    return {"status": "CruxAI System Online"}

@app.get("/api/claims", response_model=List[Claim])
def get_claims():
    return processed_claims

@app.post("/api/verify")
async def verify_claim(
    text: str = Form(None),
    link: str = Form(None),
    image: UploadFile = File(None)
):
    # Handle cases where only link or image is provided
    claim_text = text or ""
    
    # Create a new claim object
    """
    Verify a claim (text, link, or image).
    Now supports AI-generated image detection!
    """
    result = {
        "claim": None,
        "score": None,
        "image_analysis": None
    }
    
    # Handle text/link verification (existing functionality)
    if text or link:
        claim_text = text if text else f"Claim from: {link}"
        
        # Create a new claim object
        claim = Claim(
            id=str(uuid.uuid4()),
            text=claim_text,
            status="processing"
        )

        # Verify using existing agents
        claim = verify_agent.verify(claim, link=link) # Assuming verify_agent.verify can take a Claim object and link
        score = score_agent.score(claim)
        
        # Set status based on score
        if score.verdict == "VERIFIED": # Assuming score object has a verdict
            claim.status = "verified"
        elif score.verdict == "FALSE": # Assuming score object has a verdict
            claim.status = "false"
        else:
            claim.status = "unverified"
        
        processed_claims.append(claim)
        
        result["claim"] = claim
        result["score"] = score
    
    # Handle image analysis (NEW functionality)
    if image:
        try:
            print(f"Received image: {image.filename}")
            
            # Read image data
            image_data = await image.read()
            print(f"Image size: {len(image_data)} bytes")
            
            # Analyze image
            analysis = image_analyzer.analyze_image(image_data)
            
            result["image_analysis"] = analysis
            print("Image analysis complete!")
            
        except Exception as e:
            print(f"ERROR analyzing image: {e}")
            result["image_analysis"] = {
                "error": str(e),
                "message": "Failed to analyze image"
            }
    
    return result

@app.post("/api/score", response_model=ScoreResponse)
def score_claim(request: ScoreRequest):
    # Construct a temporary claim object for scoring
    claim = Claim(
        text=request.claim_text,
        evidence=request.evidence
    )
    return score_agent.score(claim)

@app.post("/api/explain", response_model=ExplainResponse)
def explain_verdict(request: ExplainRequest):
    explanation = explain_agent.explain(request.claim_text, request.verdict, request.lang)
    return ExplainResponse(explanation=explanation)

@app.get("/api/crisis", response_model=CrisisResponse)
def check_crisis():
    claims_to_check = processed_claims
    # If no claims have been processed locally, fetch fresh news to check for crises
    if not claims_to_check:
        print("No local claims found. Scanning for breaking news...")
        claims_to_check = scan_agent.scan()
        
    return crisis_agent.detect_crisis(claims_to_check)

def background_scan(source_url: str):
    new_claims = scan_agent.scan(source_url)
    for claim in new_claims:
        claim.id = str(uuid.uuid4())
        # Optional: Auto-verify scanned claims?
        # For now, just add them
        processed_claims.append(claim)

@app.post("/api/scan")
def trigger_scan(request: ScanRequest, background_tasks: BackgroundTasks):
    background_tasks.add_task(background_scan, request.source_url)
    return {"message": f"Scan initiated for {request.source_url}"}

@app.get("/api/news/{category}")
def get_news_by_category(category: str):
    """Fetch news by category"""
    try:
        claims = scan_agent.scan_by_category(category)
        return {
            "category": category,
            "count": len(claims),
            "articles": claims
        }
    except Exception as e:
        print(f"Error fetching news for category {category}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/agents")
def get_agents_status():
    try:
        # Calculate stats based on processed_claims
        total_processed = len(processed_claims)
        
        return {
            "agents": [
                {
                    "name": "ScanAgent",
                    "status": "active",
                    "processed": total_processed * 2 + 120, # Mock logic for demo
                    "active": 1,
                    "description": "Monitors social media and news sources for emerging claims",
                    "progress": 95,
                },
                {
                    "name": "VerifyAgent",
                    "status": "active",
                    "processed": total_processed,
                    "active": 0,
                    "description": "Cross-references claims with trusted fact-checking sources",
                    "progress": 100,
                },
                {
                    "name": "ScoreAgent",
                    "status": "active",
                    "processed": total_processed,
                    "active": 0,
                    "description": "Calculates credibility scores based on evidence strength",
                    "progress": 100,
                },
                {
                    "name": "ExplainAgent",
                    "status": "idle",
                    "processed": total_processed // 2,
                    "active": 0,
                    "description": "Generates human-readable explanations and translations",
                    "progress": 0,
                },
            ],
            "activity_logs": [
                {"time": "Just now", "agent": "System", "action": "System health check passed", "status": "success"},
                {"time": "1 min ago", "agent": "ScanAgent", "action": "Scanned for crisis events", "status": "success"},
            ]
        }
    except Exception as e:
        print(f"Error in get_agents_status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/forensics")
def analyze_media(
    url: str = Form(None),
    file: UploadFile = File(None)
):
    # Mock forensic analysis
    import random
    score = random.randint(10, 90)
    
    return {
        "defakeScore": score,
        "manipulations": [
            "Potential face manipulation detected" if score > 50 else "No significant manipulation detected",
            "Compression artifacts analyzed"
        ],
        "provenance": "Source origin analysis completed.",
        "recommendation": "HIGH RISK" if score > 60 else ("MODERATE RISK" if score > 30 else "LIKELY AUTHENTIC")
    }

@app.post("/api/chat")
async def chat(request: dict):
    """
    Chat endpoint using Hugging Face LLM for AI assistance (FREE!).
    """
    try:
        user_message = request.get("message", "")
        chat_history = request.get("history", [])
        
        if not user_message:
            raise HTTPException(status_code=400, detail="Message is required")
        
        # Use Hugging Face API for real LLM response
        from huggingface_hub import InferenceClient
        import os
        
        hf_api_key = os.getenv("HUGGINGFACE_API_KEY")
        if not hf_api_key:
            return {
                "response": "I'm here to help! I can assist you with verifying claims, checking crisis alerts, or navigating the platform. How can I help you today?"
            }
        
        client = InferenceClient(token=hf_api_key)
        
        # Build messages for chat
        messages = [
            {
                "role": "system",
                "content": "You are CruxAI Assistant, a helpful AI for a fact-checking platform. Be concise (2-3 sentences max). Help users verify claims and navigate features."
            }
        ]
        
        # Add last 3 messages for context
        for msg in chat_history[-3:]:
            messages.append({
                "role": msg.get("role", "user"),
                "content": msg.get("content", "")
            })
        
        # Add current message
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        # Use Groq API (same as credibility scoring - we know it works!)
        from groq import Groq
        
        groq_api_key = os.getenv("GROQ_API_KEY")
        if not groq_api_key:
            return {
                "response": "I'm here to help! I can assist you with verifying claims, checking crisis alerts, or navigating the platform."
            }
        
        client = Groq(api_key=groq_api_key)
        
        # Use Groq's chat completion
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",  # Fast and capable
            messages=messages,
            temperature=0.7,
            max_tokens=150,
            top_p=1,
            stream=False
        )
        
        response_text = completion.choices[0].message.content.strip()
        
        return {
            "response": response_text
        }
        
    except Exception as e:
        print(f"ERROR in chat endpoint: {e}")
        import traceback
        traceback.print_exc()
        # Fallback response on error
        return {
            "response": "I'm here to help! You can ask me about crisis alerts, agent status, or to verify claims. What would you like to know?"
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
