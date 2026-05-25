from typing import TypedDict, Dict, Optional
import time
import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
import uuid


class JobState(TypedDict):
    status: str
    progress: int
    message: str
    updated_at: float


app = FastAPI()

job_states: Dict[str, JobState] = {}


async def long_job(job_id: str) -> None:
    try:
        steps: list[tuple[str, int, str]] = [
            ("started", 0, "Job started"),
            ("running", 25, "Loading data"),
            ("running", 50, "Processing data"),
            ("running", 75, "Finalizing"),
            ("finished", 100, "Job completed"),
        ]

        for status, progress, message in steps:
            job_states[job_id] = JobState(
                status=status,
                progress=progress,
                message=message,
                updated_at=time.time(),
            )
            await asyncio.sleep(5)

    except Exception as e:
        job_states[job_id] = JobState(
            status="error",
            progress=0,
            message=f"Error: {e}",
            updated_at=time.time(),
        )


@app.post("/start")
async def start_job() -> dict[str, str]:
    job_id = str(uuid.uuid4())
    job_states[job_id] = JobState(
        status="queued",
        progress=0,
        message="Job queued",
        updated_at=time.time(),
    )
    asyncio.create_task(long_job(job_id))
    return {"job_id": job_id}


async def sse_stream(job_id: str):
    last_state: Optional[JobState] = None

    if job_id not in job_states:
        yield "event: error\ndata: Job not found\n\n"
        return

    while True:
        state = job_states.get(job_id)

        if state is None:
            # job was removed or never existed
            yield "event: error\ndata: Job state missing\n\n"
            break

        if state != last_state:
            payload = (
                f"data: {state['status']}|"
                f"{state['progress']}|"
                f"{state['message']}\n\n"
            )
            yield payload
            last_state = state

        if state["status"] in ("finished", "error"):
            break

        await asyncio.sleep(0.3)


@app.get("/events")
async def events(job_id: str):
    if job_id not in job_states:
        raise HTTPException(status_code=404, detail="Job not found")

    return StreamingResponse(sse_stream(job_id), media_type="text/event-stream")
