from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime

class Evidence(BaseModel):
    source: str
    content: str
    url: str

class ScoreResponse(BaseModel):
    final_score: int = Field(..., ge=0, le=100)
    source_reliability: int = Field(..., ge=0, le=100)
    evidence_strength: int = Field(..., ge=0, le=100)
    consistency: int = Field(..., ge=0, le=100)
    verdict: Literal["VERIFIED", "FALSE", "MIXED", "UNVERIFIED"]

class Claim(BaseModel):
    id: Optional[str] = None
    text: str
    source: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    status: Literal["unverified", "verified", "processing"] = "unverified"
    evidence: List[Evidence] = []
    score: Optional[ScoreResponse] = None

class CrisisAlert(BaseModel):
    id: str
    title: str
    severity: Literal["CRITICAL", "HIGH", "MEDIUM", "LOW"]
    region: Optional[str] = None
    verified: bool
    keywords: List[str]
    description: Optional[str] = None

class CrisisResponse(BaseModel):
    crisis_detected: bool
    alerts: List[CrisisAlert]
    recommended_actions: List[str]

class ExplainRequest(BaseModel):
    claim_text: str
    verdict: str
    lang: str = "en"

class ExplainResponse(BaseModel):
    explanation: str

class ScanRequest(BaseModel):
    source_url: str

class VerifyRequest(BaseModel):
    text: str

class ScoreRequest(BaseModel):
    claim_id: Optional[str] = None
    claim_text: str
    evidence: List[Evidence]
