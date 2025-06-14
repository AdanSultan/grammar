from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import asyncio
import time
from typing import Optional, Dict, Any
import os
from dotenv import load_dotenv

# Import our custom modules
from services.grammar_service import GrammarService
from services.humanization_service import HumanizationService
from services.detection_service import DetectionService
from services.plagiarism_service import PlagiarismService
from utils.text_processor import TextProcessor

# Load environment variables
load_dotenv("../api-keys/.env")

app = FastAPI(
    title="AI-to-Human Converter",
    description="Convert AI-generated text to undetectable human-like content",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
grammar_service = GrammarService()
humanization_service = HumanizationService()
detection_service = DetectionService()
plagiarism_service = PlagiarismService()
text_processor = TextProcessor()

class ConversionRequest(BaseModel):
    text: str
    tone: Optional[str] = "balanced"  # formal, casual, balanced
    preserve_meaning: Optional[bool] = True
    check_plagiarism: Optional[bool] = True
    check_ai_detection: Optional[bool] = True

class ConversionResponse(BaseModel):
    original_text: str
    converted_text: str
    grammar_corrections: int
    humanization_score: float
    ai_detection_score: float
    plagiarism_score: float
    processing_time: float
    confidence: float

@app.get("/")
async def root():
    return {"message": "AI-to-Human Converter API", "status": "active"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "services": {
        "grammar": "active",
        "humanization": "active", 
        "detection": "active",
        "plagiarism": "active"
    }}

@app.post("/api/convert", response_model=ConversionResponse)
async def convert_text(request: ConversionRequest):
    """
    Main conversion endpoint - converts AI text to human-like content
    """
    start_time = time.time()
    
    try:
        # Step 1: Grammar correction
        grammar_start = time.time()
        corrected_text, grammar_corrections = await grammar_service.correct_grammar(request.text)
        grammar_time = time.time() - grammar_start
        
        # Step 2: Humanization
        humanization_start = time.time()
        humanized_text, humanization_score = await humanization_service.humanize(
            corrected_text, 
            tone=request.tone,
            preserve_meaning=request.preserve_meaning
        )
        humanization_time = time.time() - humanization_start
        
        # Step 3: AI Detection Check (if requested)
        ai_detection_score = 0.0
        if request.check_ai_detection:
            detection_start = time.time()
            ai_detection_score = await detection_service.check_ai_detection(humanized_text)
            detection_time = time.time() - detection_start
        
        # Step 4: Plagiarism Check (if requested)
        plagiarism_score = 0.0
        if request.check_plagiarism:
            plagiarism_start = time.time()
            plagiarism_score = await plagiarism_service.check_plagiarism(humanized_text)
            plagiarism_time = time.time() - plagiarism_start
        
        # Calculate confidence score
        confidence = calculate_confidence(
            grammar_corrections,
            humanization_score,
            ai_detection_score,
            plagiarism_score
        )
        
        total_time = time.time() - start_time
        
        return ConversionResponse(
            original_text=request.text,
            converted_text=humanized_text,
            grammar_corrections=grammar_corrections,
            humanization_score=humanization_score,
            ai_detection_score=ai_detection_score,
            plagiarism_score=plagiarism_score,
            processing_time=total_time,
            confidence=confidence
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conversion failed: {str(e)}")

@app.post("/api/grammar")
async def correct_grammar_only(request: ConversionRequest):
    """Grammar correction only endpoint"""
    try:
        corrected_text, corrections = await grammar_service.correct_grammar(request.text)
        return {
            "original_text": request.text,
            "corrected_text": corrected_text,
            "corrections_made": corrections,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Grammar correction failed: {str(e)}")

@app.post("/api/humanize")
async def humanize_only(request: ConversionRequest):
    """Humanization only endpoint"""
    try:
        humanized_text, score = await humanization_service.humanize(
            request.text,
            tone=request.tone,
            preserve_meaning=request.preserve_meaning
        )
        return {
            "original_text": request.text,
            "humanized_text": humanized_text,
            "humanization_score": score,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Humanization failed: {str(e)}")

@app.post("/api/detect")
async def check_ai_detection(request: ConversionRequest):
    """AI detection check endpoint"""
    try:
        detection_score = await detection_service.check_ai_detection(request.text)
        return {
            "text": request.text,
            "ai_detection_score": detection_score,
            "is_ai_detected": detection_score > 0.5,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI detection check failed: {str(e)}")

@app.post("/api/plagiarism")
async def check_plagiarism(request: ConversionRequest):
    """Plagiarism check endpoint"""
    try:
        plagiarism_score = await plagiarism_service.check_plagiarism(request.text)
        return {
            "text": request.text,
            "plagiarism_score": plagiarism_score,
            "is_plagiarized": plagiarism_score > 0.3,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Plagiarism check failed: {str(e)}")

def calculate_confidence(grammar_corrections: int, humanization_score: float, 
                        ai_detection_score: float, plagiarism_score: float) -> float:
    """Calculate overall confidence score"""
    # Grammar weight: 20%
    grammar_confidence = max(0, 1 - (grammar_corrections * 0.1))
    
    # Humanization weight: 30%
    humanization_confidence = humanization_score
    
    # AI detection weight: 30% (lower is better)
    detection_confidence = 1 - ai_detection_score
    
    # Plagiarism weight: 20% (lower is better)
    plagiarism_confidence = 1 - plagiarism_score
    
    # Weighted average
    confidence = (
        grammar_confidence * 0.2 +
        humanization_confidence * 0.3 +
        detection_confidence * 0.3 +
        plagiarism_confidence * 0.2
    )
    
    return min(1.0, max(0.0, confidence))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 