import asyncio
import time
import redis.asyncio as redis
from fastapi import FastAPI

app = FastAPI()

REDIS_HOST = "redis"
r = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)


@app.on_event("startup")
async def startup():
    # Resume unfinished jobs BEFORE starting queue consumption
    await resume_incomplete_jobs()

    # Start normal worker loop
    asyncio.create_task(worker_loop())


async def resume_incomplete_jobs():
    print("[worker] Checking for incomplete jobs...")

    # Only fetch keys that look like job IDs (UUIDs contain hyphens)
    keys = await r.keys("*-*")

    for job_id in keys:
        state = await r.hgetall(job_id)
        if not state:
            continue

        if state.get("status") == "running":
            print(f"[worker] Resuming job {job_id} from progress={state.get('progress')}")
            asyncio.create_task(run_job(job_id, resume=True))


async def worker_loop():
    while True:
        job = await r.brpop("job_queue")
        job_id = job[1]

        print(f"[worker] Picked new job {job_id}")
        asyncio.create_task(run_job(job_id))


async def run_job(job_id: str, resume=False):
    steps = [
        ("running", 10, "Loading data"),
        ("running", 40, "Processing data"),
        ("running", 70, "Finalizing"),
        ("finished", 100, "Job completed"),
    ]

    # Load current state
    state = await r.hgetall(job_id)
    current_progress = int(state.get("progress", 0))

    # Find where to resume
    start_index = 0
    for i, (_, progress, _) in enumerate(steps):
        if progress > current_progress:
            start_index = i
            break

    print(f"[worker] Job {job_id} starting at step index {start_index}")

    # Run remaining steps
    for status, progress, message in steps[start_index:]:
        await r.hset(job_id, mapping={
            "status": status,
            "progress": progress,
            "message": message,
            "updated_at": time.time(),
        })
        await asyncio.sleep(3)

    print(f"[worker] Job {job_id} finished")
