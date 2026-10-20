import os
import subprocess
import datetime
from pathlib import Path

# Configuration
BACKUP_DIR = Path("./backups")
RETENTION_DAYS = 30 # Keep backup for 30 days
DB_NAME = os.getenv("DB_NAME", "edusleek_prod")
DB_USER = os.getenv("DB_USER", "postgres")
DB_HOST = os.getenv("DB_HOST", "localhost")

def create_logical_backup():
    """
    Simulates or executes a PostgreSQL logical pg_dump backup with a precise timestamp for granular tenant restoration.
    """
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_file = BACKUP_DIR / f"edusleek_backup_{timestamp}.sql"

    print(f"[{datetime.datetime.now()}] Starting database backup for {DB_NAME}...")

    # Command to run pg_dump (uncomment in production with real DB credentials)
    #cmd = f"pg_dump -h {DB_HOST} -U {DB_USER} -F c -b -v -f {backup_file} {DB_NAME}"

    # Simulation for local workspace testing:
    backup_file.write_text(f"-- EduSleek Logical Backup Simulation\n-- Timestamp: {timestamp}\n")

    print(f"[{datetime.datetime.now()}] Backup successfully saved to {backup_file}")
    cleanup_old_backups()

def cleanup_old_backups():
    """
    Enforces the rolling rentention ring by deleting backups older than RETENTION_DAYS.
    """

    now = datetime.datetime.now()
    deleted_count = 0

    for file_path in BACKUP_DIR.glob("edusleek_backup_*.sql"):
        # Check file age based on creation time
        file_age_days = (now - datetime.datetime.fromtimestamp(file_path.stat().st_mtime)).days

        if file_age_days > RETENTION_DAYS:
            file_path.unlink()
            deleted_count += 1
            print(f"Pruned expired backup: {file_path.name} (Age: {file_age_days} days)")

    print(f"Retention Check complete. Pruned {deleted_count} old backup(s). ")

if __name__ == "__main__":
    create_logical_backup()