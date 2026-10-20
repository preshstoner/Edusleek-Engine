from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from celery.result import AsyncResult
from celery_app import celery_app, compile_broadsheet_task

# In-memory store for demo purposes (in production, use Redis or PostgresSQL)
CBT_STATE_STORE: Dict[str, Dict[str, Any]] = {}

class ExamStatePayload(BaseModel):
    student_id: str
    exam_id: str
    current_question_index: int
    saved_answers: Dict[str, Any]
    remaining_seconds: int

app = FastAPI(title="EduSleek Asynchronous Gateway")

@app.post("/api/compile-broadsheet")
def trigger_broadsheet_compilation(tenant_id: str, term: str):
    """
    Web Tier: Enqueues the task into Redis and returns immediatly (<150ms).
    Prevents Gunicorn/Uvicorn worker lockup.
    """
    # Push job to Redis queue without waiting for completion
    task = compile_broadsheet_task.delay(tenant_id, term)

    return {
        "message": "Broadsheet compilation queued successfully.",
        "task_id": task.id,
        "poll_status_url": f"/api/task-status/{task.id}"
    }


@app.post("/api/cbt/sync-state")
def sync_exam_state(payload: ExamStatePayload):
    """
    Receives periodic background syncs from the student's browser tp prevent state against power cuts or browser crashes.
    """
    key = f"{payload.exam_id}:{payload.student_id}"
    CBT_STATE_STORE[key] = {
        "current_question_index": payload.current_question_index,
        "saved_answers": payload.saved_answers,
        "remaining_seconds": payload.remaining_seconds,
        "last_synced_at": "server_timestamp_active" 
    }
    return {"status": "synced", "student_id": payload.student_id}

@app.get("/api/cbt/restore-state/{exam_id}/{student_id}")
def restore_exam_state(exam_id: str, student_id: str):
    """
    Allows a student logging in from a backup terminal to resume from the exact question and second they left off.
    """
    key = f"{exam_id}:{student_id}"
    state = CBT_STATE_STORE.get(key)

    if not state:
        # If no server backup exists, return default starting state
        return{
            "resumed": False,
            "current_question_index": 0,
            "saved_answers": {},
            "remaining_seconds": 3600 # e.g., 60-mintues default exam
        }

    return {
        "resumed": True,
        **state
    }

@app.get("/api/task-status/{task_id}")
def get_task_status(task_id: str):
    """
    Status Endpoint: Polled lightweight endpoint (perfect for HTMX or frontend JS)
    to check background worker progress without tying up web workers.
    """
    task_result = AsyncResult(task_id, app=celery_app)

    response = {
        "task_id": task_id,
        "status": task_result.status, # PENDING, STARTED, SUCCESS, FAILURE
        "ready": task_result.ready(),
    }

    if task_result.ready():
        if task_result.successful():
            response["result"] = task_result.result
        else:
            response["error"] = str(task_result.result)

    return response

@app.post("/api/generate-remark")
def trigger_ai_remark_generation(student_metrics: dict):
    """
    Enqueues the AI report card remark generation task into Celery/redis.
    """
    from celery_app import generate_student_remark_async

    task = generate_student_remark_async.delay(student_metrics)

    return {
        "message": "AI remark generation queued successfully.",
        "task_id": task.id,
        "poll_status_url": f"/api/task-status/{task.id}"
    }
