import { useState } from "react";
import { startJob } from "./api";
import JobStatus from "./JobStatus";

export default function App() {
  const [jobs, setJobs] = useState([]);

  async function handleStart() {
    const { job_id } = await startJob();
    setJobs(prev => [...prev, job_id]);
  }

  return (
    <div style={{ padding: "20px" }}>
      <h1>SSE Multi - Job Demo</h1>

      <button onClick={handleStart}>Start Job</button>

      {jobs.map(jobId => (
        <JobStatus key={jobId} jobId={jobId} />
      ))}
    </div>
  );
}
