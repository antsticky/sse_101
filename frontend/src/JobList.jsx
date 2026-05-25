import { Link } from "react-router-dom";
import { useJobs } from "./JobStore";

async function startJob() {
  const res = await fetch("/start", { method: "POST" });
  const data = await res.json();
  return data.job_id;
}

export default function JobList() {
  const { jobs, setJobs } = useJobs();

  const startNewJob = async () => {
    const jobId = await startJob();

    setJobs((prev) => ({
      ...prev,
      [jobId]: { status: "queued", progress: 0, messages: [] },
    }));
  };

  return (
    <div style={{ padding: 20 }}>
      <h1>Jobs</h1>

      <button onClick={startNewJob}>Start Job</button>

      <ul>
        {Object.keys(jobs).map((jobId) => (
          <li key={jobId}>
            <Link to={`/job/${jobId}`}>Job {jobId}</Link>
          </li>
        ))}
      </ul>
    </div>
  );
}
