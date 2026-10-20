# EduSleek Engine

A production-grade, multi-tenant backend architecture designed for high-concurrency school management systems. Built to handle spiky traffic, offline school environments, dynamic grading rubrics, and asynchronous AI task processing without breaking a sweat.

---

## 🏗️ Architectural Highlights

1. **Dynamic JSONB Tenant Blueprint Engine (`engine.py`)**
   - Eliminates hardcoded relational columns by allowing each tenant school to define custom grading rubrics via structured JSON.
   - Utilizes Python's `Decimal` math to prevent floating-point rounding errors during weighted score aggregation.

2. **Async Task Pipeline (`celery_app.py` & `main_api.py`)**
   - Offloads heavy report rendering and database aggregation to background workers via Celery and Redis.
   - Protects the FastAPI/Gunicorn web tier from lockup, returning task IDs in under 150ms to prevent 502 Bad Gateway errors under peak load.

3. **Practical AI Integration (`celery_app.py`)**
   - Integrates the Groq LLM API directly into background workers with exponential backoff and automatic retries.
   - Generates contextual, individualized student report card remarks in seconds, cutting administrative bottlenecks by over 50%.

4. **Offline-First CBT Terminal (`cbt_client.html` & `main_api.py`)**
   - Designed for local campus deployments with unstable power and internet grids.
   - Pairs browser `localStorage` caching with periodic server background synchronization so students can resume exams from the exact second they left off if a terminal loses power.

5. **Disaster Recovery Backup Manager (`backup_manager.py`)**
   - Automates timestamped logical PostgreSQL database backups (`pg_dump`).
   - Enforces a rolling retention window to prune expired backups and preserve disk space.

---

## 📁 Project Structure

```text
edusleek-engine/
├── engine.py             # Core multi-tenant JSONB validation logic
├── demo.py               # Test script simulating multiple tenant grading rubrics
├── celery_app.py         # Celery broker configuration, broadsheet tasks, & Groq AI worker
├── main_api.py           # FastAPI web gateway (Async routing & CBT state sync)
├── cbt_client.html       # Offline-resilient Computer-Based Testing browser client
└── backup_manager.py     # Automated database backup and retention ring manager


🚀 Quick Start Guide
Prerequisites
Python 3.10+

Docker Desktop (for running Redis)

1. Clone & Install Dependencies
PowerShell
git clone https://github.com/preshstoner/Edusleek-Engine.git
cd edusleek-engine
pip install fastapi uvicorn celery redis requests python-dotenv

2. Start Redis via Docker
PowerShell
docker run -d -p 6379:6379 --name edusleek-redis redis:alpine

3. Run the Celery Background Worker
In your first terminal window:

PowerShell
python -m celery -A celery_app.celery_app worker --loglevel=info -P solo
4. Start the FastAPI Web Tier
In a second terminal window:

PowerShell
python -m uvicorn main_api:app --reload --port 8000
5. Test the Engine Demo Script
To test the multi-tenant grading blueprint engine locally:

PowerShell
python demo.py
💡 Environment Variables
Create a .env file in the root directory if you are using the live Groq AI integration:

Code snippet
GROQ_API_KEY=gsk_your_actual_groq_api_key_here
🛡️ License
Distributed under the MIT License. See LICENSE for more information.
