import shutil
import uuid
import os
import time
import asyncio
import logging
from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List, Any
from pydantic import BaseModel

# Import the service from our package
# Note: When running with uvicorn from root or backend, path resolution might vary.
# We assume running `uvicorn main:app --reload` from `backend/` directory.
from backend.ai_engine.service import analysis_service
from backend.database import db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("app.log")
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="ShuttleCoach AI API",
    description="Backend API for ShuttleCoach AI - Badminton Video Analysis",
    version="0.1.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

async def cleanup_old_files():
    """Delete files older than 24 hours."""
    logger.info("Starting cleanup of old files...")
    now = time.time()
    cutoff = now - (24 * 3600) # 24 hours ago
    
    count = 0
    for filename in os.listdir(UPLOAD_DIR):
        file_path = os.path.join(UPLOAD_DIR, filename)
        if os.path.isfile(file_path):
            file_mtime = os.path.getmtime(file_path)
            if file_mtime < cutoff:
                try:
                    os.remove(file_path)
                    count += 1
                    logger.info(f"Deleted old file: {filename}")
                except Exception as e:
                    logger.error(f"Error deleting file {filename}: {e}")
    logger.info(f"Cleanup finished. Deleted {count} files.")

@app.on_event("startup")
async def startup_event():
    # Run cleanup on startup
    await cleanup_old_files()

def process_analysis_task(task_id: str, file_path: str):
    """
    Background task to run the AI analysis.
    """
    try:
        logger.info(f"Starting analysis for task {task_id}")
        # MVP: We now let the AI engine automatically detect the action type.
        # So we pass action_type=None to let the detector work.
        result = analysis_service.analyze_video(file_path, action_type=None)
        
        db.update_task_result(task_id, result)
        logger.info(f"Analysis completed for task {task_id}")
    except Exception as e:
        logger.error(f"Analysis failed for task {task_id}: {e}")
        db.update_task_error(task_id, str(e))

@app.get("/")
async def root():
    return {"message": "Welcome to ShuttleCoach AI API"}

@app.post("/api/upload")
async def upload_video(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    # Generate unique ID
    task_id = str(uuid.uuid4())
    
    # Save file
    file_path = os.path.join(UPLOAD_DIR, f"{task_id}_{file.filename}")
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # Initialize status in DB
    db.create_task(task_id, file_path)
    
    # Trigger background task
    background_tasks.add_task(process_analysis_task, task_id, file_path)
    
    return {"task_id": task_id, "message": "Upload successful, analysis started."}

@app.get("/api/result/{task_id}")
async def get_result(task_id: str):
    task = db.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

class ChatRequest(BaseModel):
    task_id: str
    message: str
    history: List[Dict[str, str]]

@app.post("/api/chat")
async def chat_with_coach_endpoint(request: ChatRequest):
    # 1. Get analysis result from DB
    task = db.get_task(request.task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    analysis_result = task.get("result")
    if not analysis_result:
         # If no result yet, we can't chat about it.
         return {"reply": "分析尚未完成，请稍后再试。"}
    
    # 2. Call Gemini
    from backend.ai_engine.llm_client import gemini_coach
    response = gemini_coach.chat_with_coach(analysis_result, request.message, request.history)
    
    return {"reply": response}
