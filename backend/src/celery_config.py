# ==========================
# src/celery_config.py
# ==========================

from kombu import Queue
from src.config import config

# --------------------------
# Redis Settings
# --------------------------
# Redis will be used as:
#   - Message broker (queue system)
#   - Result backend (store task results)
broker_url = config.REDIS_URL
result_backend = config.REDIS_URL

# --------------------------
# Serialization
# --------------------------
# Tasks and results are always sent in JSON
task_serializer = 'json'
result_serializer = 'json'
accept_content = ['json']

# All time-based operations use UTC
timezone = 'UTC'
enable_utc = True

# --------------------------
# Task Routing (which task goes to which queue)
# --------------------------
task_routes = {
    'src.services.update_sol_price': {'queue': 'price_updates'},
    'src.services.check_all_monitored_wallets': {'queue': 'wallet_monitoring'},
    'src.services.check_wallet_transactions': {'queue': 'wallet_monitoring'},
}

# --------------------------
# Queue Definitions
# --------------------------
task_default_queue = 'default'
task_queues = (
    Queue('default', routing_key='default'),
    Queue('price_updates', routing_key='price_updates'),
    Queue('wallet_monitoring', routing_key='wallet_monitoring'),
)

# --------------------------
# Worker Behavior
# --------------------------
worker_prefetch_multiplier = 1     # Worker takes 1 task at a time (no overloading)
task_acks_late = True              # Mark task as done ONLY after it's finished
worker_max_tasks_per_child = 1000  # Restart worker after 1000 tasks (avoids memory leaks)

# --------------------------
# Retry Policy
# --------------------------
task_default_retry_delay = 60  # Retry failed task after 60s
task_max_retries = 3           # Max retries per task = 3

# --------------------------
# Beat (Scheduler) Settings
# --------------------------
# Stores periodic schedule in a file (persistent across restarts)
beat_scheduler = 'celery.beat.PersistentScheduler'
beat_schedule_filename = 'celerybeat-schedule'

# --------------------------
# Logging & Monitoring
# --------------------------
worker_hijack_root_logger = False  # Don't override Python's default logging
worker_log_color = False           # Disable colored logs
worker_send_task_events = True     # Send task lifecycle events (for monitoring)
task_send_sent_event = True        # Send event when task is dispatched


"""

# Start Redis (if using Docker)
docker run -d --name redis -p 6379:6379 redis:alpine

# Or install Redis locally
# Ubuntu: sudo apt-get install redis-server
# macOS: brew install redis

# Install required packages
pip install celery[redis] flower

# Start Celery worker (in one terminal)
celery -A src.services.celery_app worker --loglevel=info --queues=default,price_updates,wallet_monitoring

# Start Celery Beat scheduler (in another terminal)
celery -A src.services.celery_app beat --loglevel=info

# Optional: Start Flower monitoring UI (in third terminal)
celery -A src.services.celery_app flower --port=5555

# Production startup (single command)
celery -A src.services.celery_app worker --beat --loglevel=info --detach

# Check task status
celery -A src.services.celery_app inspect active

# Monitor with Flower
# Open browser to http://localhost:5555
"""
