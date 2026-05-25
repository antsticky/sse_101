import asyncio
import time
import redis.asyncio as redis
from fastapi import FastAPI

app = FastAPI()

REDIS_HOST = "redis"
r = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)


@app.on_event("startup")
async def startup():
    asyncio.create_task(worker_loop())


async def worker_loop():
    while True:
        job = await r.brpop("job_queue")
        job_id = job[1]

        asyncio.create_task(run_job(job_id))


async def run_job(job_id: str):
    steps = [
        ("running", 10, "Loading data"),
        ("running", 40, "Processing data"),
        ("running", 70, "Finalizing"),
        ("finished", 100, "Job completed"),
    ]

    for status, progress, message in steps:
        await r.hset(job_id, mapping={
            "status": status,
            "progress": progress,
            "message": message,
            "updated_at": time.time(),
        })
        await asyncio.sleep(3)
