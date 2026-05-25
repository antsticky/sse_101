# README

## Summary
This project demonstrates a fault‑tolerant, scalable, multi‑stage asynchronous job processing system using Server‑Sent Events (SSE).  
The architecture separates responsibilities across a frontend, a stateless gateway backend (BE1), a worker backend (BE2), and Redis as the central job state store.  
Long‑running tasks are executed by BE2, while BE1 streams real‑time progress updates to the frontend.  
The system supports parallel job execution, automatic reconnection, and graceful degradation when components fail.

---

## Alternatives

### Async Polling
- The frontend periodically requests job status from the backend.
- Simple but inefficient at scale.
- Introduces latency and unnecessary backend load.
- Not suitable for real‑time updates.

### Server‑Sent Events (SSE)
- One‑way, real‑time streaming from server to client over HTTP.
- Lightweight, reconnect‑capable, and easy to proxy.
- Ideal for progress updates, logs, and status notifications.
- Chosen for this project because job progress is naturally push‑oriented.

### WebSockets
- Full‑duplex communication.
- More complex and resource‑intensive.
- Useful when the client must also push frequent updates.
- Overkill for simple job progress streaming.

### Push Callback (Webhook‑style)
- Worker calls back a URL when job state changes.
- Requires public endpoints and complex retry logic.
- Not suitable for browser‑based clients without additional infrastructure.

---

## Architecture

### Frontend (FE)
- Starts jobs via BE1.
- Opens an SSE connection to receive real‑time updates.
- Supports multiple concurrent jobs.

### BE1 (Gateway / Orchestrator)
- Stateless API layer.
- Accepts job creation requests.
- Pushes job IDs into Redis queues.
- Streams job state from Redis to the frontend via SSE.
- Does not execute jobs.

### BE2 (Worker)
- Consumes job IDs from a Redis queue.
- Executes long‑running tasks asynchronously.
- Writes job progress and final results back to Redis.
- Multiple BE2 instances can run in parallel.

### Redis
- Centralized job state store.
- Stores job metadata (status, progress, message, timestamps).
- Provides a queue (`job_queue`) for BE2 workers.
- Enables full decoupling between BE1 and BE2.

---

## Communication Flow

### 1. Job Creation
- FE → BE1: POST /start
- BE1 → Redis: HSET job initial state
- BE1 → Redis: LPUSH job_queue job_id
- BE1 → FE: return job_id

### 2. Job Execution
- BE2 → Redis: BRPOP job_queue
- BE2 → run job steps
- BE2 → Redis: update job state (status, progress, message)

### 3. Real‑Time Updates
- FE → BE1: GET /events?job_id=...
- BE1 → Redis: HGETALL job state
- BE1 → FE: SSE data events

### 4. Completion
- BE2 → Redis: status = finished
- BE1 → FE: SSE close event
- FE: closes EventSource


---

## Error Tolerant Behavior

### BE1 Outage
- SSE connection drops.
- Browser automatically reconnects.
- BE1 is stateless, so restart does not affect job state.
- Redis ensures no data loss.

### BE2 Outage
- Job progress stops updating.
- SSE connection remains open (BE1 is still alive).
- When BE2 restarts, it resumes processing remaining jobs.
- No reconnect is triggered because the stream endpoint (BE1) is unaffected.

### Redis Outage
- BE1 cannot read job state → SSE may send error events.
- BE2 cannot write job state → jobs may fail or pause.
- When Redis returns, the system recovers automatically.

---

## Role of BE1

### Orchestrator
- Accepts job creation requests.
- Initializes job state in Redis.
- Pushes job IDs into the worker queue.

### SSE Stream Provider
- Reads job state from Redis.
- Streams updates to the frontend.
- Sends heartbeat messages.
- Closes the stream when the job finishes.

### Stateless API Layer
- Holds no job state in memory.
- Can be restarted at any time without losing data.
- Scales horizontally without coordination.

### Fault Isolation
- BE1 failures do not affect job execution.
- BE2 failures do not break SSE streams.
- Redis acts as the single source of truth for all job state.
