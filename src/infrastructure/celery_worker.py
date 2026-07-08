import os
import subprocess

from celery import Celery

from src.infrastructure.config_loader import default_loader, load_config

# Fetch configuration and initialize Celery app
cfg = load_config()
redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

app = Celery("ai_knowledge_tasks", broker=redis_url, backend=redis_url)

app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)


@app.task(bind=True, name="sync_context_task")
def sync_context_task(self):
    """
    Background task to synchronize the context using sync_context.py
    """
    repo_root = default_loader.get_repo_root()
    script_path = os.path.join(repo_root, "scripts", "sync_context.py")

    # Run the sync process
    try:
        import sys

        result = subprocess.run(
            [sys.executable, script_path],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=True,
        )
        return {"status": "success", "output": result.stdout}
    except subprocess.CalledProcessError as e:
        return {"status": "error", "output": e.stderr}
