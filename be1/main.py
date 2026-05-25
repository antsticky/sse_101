import asyncio
import time
import uuid
import json
import redis.asyncio as redis
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS FIX
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # vagy: ["http://localhost:5173"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

REDIS_HOST = "redis"
r = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)


@app.post("/start")
async def start_job():
    job_id = str(uuid.uuid4())

    await r.hset(job_id, mapping={
        "status": "queued",
        "progress": 0,
        "message": "Job queued",
        "updated_at": time.time(),
    })

    await r.lpush("job_queue", job_id)

    return {"job_id": job_id}


async def sse_stream(job_id: str):
    last_state = None

    while True:
        state = await r.hgetall(job_id)

        if not state:
            yield "event: error\ndata: Job not found\n\n"
            return

        if state != last_state:
            yield f"data: {json.dumps(state)}\n\n"
            last_state = state

        # 🔥 If job is done → send close event and exit generator
        if state.get("status") in ("finished", "error"):
            yield "event: close\ndata: stream_end\n\n"
            return   # <--- IMPORTANT

        # heartbeat
        yield "data: heartbeat\n\n"
        await asyncio.sleep(1)



@app.get("/events")
async def events(job_id: str):
    exists = await r.exists(job_id)
    if not exists:
        raise HTTPException(status_code=404, detail="Job not found")

    return StreamingResponse(sse_stream(job_id), media_type="text/event-stream")
