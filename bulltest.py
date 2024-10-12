from fastapi import FastAPI, BackgroundTasks
from bullmq import Queue, Worker, Job
from redis import Redis
import asyncio
import signal
import uuid


redis_connection = Redis(host='localhost', port=6379, db=0)
app = FastAPI()

# Replace these with your Redis connection details
# REDIS_CONNECTION = "rediss://<user>:<password>@<host>:<port>"
queue = Queue("myQueue")
# In-memory job statuses for demonstration purposes
job_statuses = {}


async def process(job):
    # Simulate some processing (e.g., perform an async operation)
    await asyncio.sleep(2)  # Simulating a task taking some time
    job_statuses[job.id] = "completed"  # Mark the job as completed


@app.on_event("startup")
async def startup_event():
    # Create the worker
    worker = Worker("myQueue", process)

    # Handle shutdown signals
    shutdown_event = asyncio.Event()

    def signal_handler(signal, frame):
        print("Signal received, shutting down.")
        shutdown_event.set()

    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    # Run the worker until shutdown
    await shutdown_event.wait()
    print("Cleaning up worker...")
    await worker.close()
    print("Worker shut down successfully.")


@app.post("/jobs/")
async def create_job(background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())  # Create a unique job ID
    job_statuses[job_id] = "pending"  # Initialize job status
    await queue.add("myJob", {"job_id": job_id})  # Add job to the queue
    return {"job_id": job_id, "status": "Job added to the queue."}


@app.get("/jobs/{job_id}/status")
async def get_job_status(job_id: str):
    status = job_statuses.get(job_id, "Job not found.")
    return {"job_id": job_id, "status": status}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
