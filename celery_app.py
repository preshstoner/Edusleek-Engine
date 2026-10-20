import os
import time
import requests
from celery import Celery
from requests.exceptions import RequestException
from dotenv import load_dotenv

# Initialize Celery using Redis as both the message broker and result backend
celery_app = Celery(
    "edusleek_tasks",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

@celery_app.task(name="compile_broadsheet_task")
def compile_broadsheet_task(tenant_id: str, term: str):
    """
    Worker Tier: Handles heavy database aggregation and PDF rendering in the background, completely isolated from the web server.
    """
    print(f"[{tenant_id}] Starting heavy broadsheet compilation for {term}...")

    # Simulate heavy compute / DB query delay (e.g., 5 seconds)
    time.sleep(5)

    # print(f"[{tenant_id}] Broadsheet complication complete for {term}!")

    return {
        "status": "success",
        "tenant_id": tenant_id,
        "term": term,
        "records_processed": 500,
        "download_url": f"/media/reports/{tenant_id}_{term}_broadsheet.pdf"
    }

def build_structured_academic_prompt(student_metrics: dict) -> str:
    """Constructs a deterministic prompt based on structured academic metrics."""
    name = student_metrics.get("student_name", "The student")
    avg = student_metrics.get("average_score", 0)
    strongest = student_metrics.get("strongest_subject", "General Studies")
    weakest = student_metrics.get("weakest_subject", "Areas for Improvement")
    attendance = student_metrics.get("attendance_percentage", 100)

    return (
        f"Write a professional, constructive and personalized academic end-of-term remark "
        f"for a student named {name}. "
        f"Metrics: Term Average: {avg}%, Strongest Subject: {strongest}, "
        f"Weakest Subject: {weakest}, Attendance: {attendance}%. "
        f"Keep it encouraging, concise (under 4 sentences), and actionable."
    )

def call_groq_completion_api(prompt: str) -> str:
    """Calls the Groq LLM API using standard OpenAI-compatible endpoints."""
    # Retrieve key directly from enviroment
    groq_api_key = os.getenv("GROQ_API_KEY")

    # Strictly fail fast if the enviroment variable isn't set
    if not groq_api_key:
        raise ValueError("GROQ_API_KEY enviroment variable is not set. Check your .env file.")

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {groq_api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "You are an expert school administrator writing student evaluation reports."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }

    response = requests.post(url, json=payload, headers=headers, timeout=10)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

    # Simulated response for local testing without a live Groq key right away:
    time.sleep(1)
    return f"Simulated AI Remark: Excellent progress demonstrated this term, especially in academics. Keep focusing on structed pratice to bridge gaps."


@celery_app.task(
    bind=True,
    autoretry_for=(RequestException,),
    retry_backoff=True,
    max_retires=3,
    name="generate_student_remark_async"
)
def generate_student_remark_async(self, student_metrics:dict) -> str:
    """
    Offloaded to Celery with exponential backoff to handle external API rate limits gracefully.
    """
    try:
        prompt = build_structured_academic_prompt(student_metrics)
        response = call_groq_completion_api(prompt)
        return response.strip()
    except Exception as exc:
        # Celery will auotmatically catch RequestException and retry with exponential backoff
        raise self.retry(exc=exc)

