import { useEffect } from "react";
import { useParams } from "react-router-dom";
import { useJobs } from "./JobStore";

export default function JobDetail() {
  const { jobId } = useParams();
  const { jobs, setJobs } = useJobs();
  const job = jobs[jobId];

  useEffect(() => {
    if (!job) return;

    const evt = new EventSource(`/events?job_id=${jobId}`);

    evt.onmessage = (e) => {
      const [status, progress, message] = e.data.split("|");

      setJobs((prev) => ({
        ...prev,
        [jobId]: {
          ...prev[jobId],
          status,
          progress: Number(progress),
          messages: [...prev[jobId].messages, { status, progress, message }],
        },
      }));

      if (status === "finished" || status === "error") {
        evt.close();
      }
    };

    evt.onerror = () => {
      console.log("SSE reconnecting…");
    };

    return () => evt.close();
  }, [jobId]);

  if (!job) return <p>Job not found</p>;

  return (
    <div style={{ padding: 20 }}>
      <h2>Job {jobId}</h2>

      <div
        style={{
          height: 20,
          width: "100%",
          background: "#eee",
          borderRadius: 4,
          overflow: "hidden",
          marginBottom: 10,
        }}
      >
        <div
          style={{
            height: "100%",
            width: `${job.progress}%`,
            background:
              job.status === "finished"
                ? "green"
                : job.status === "error"
                ? "red"
                : "#007bff",
            transition: "width 0.3s",
          }}
        />
      </div>

      <ul>
        {job.messages.map((m, i) => (
          <li key={i}>
            {m.status} – {m.progress}% – {m.message}
          </li>
        ))}
      </ul>
    </div>
  );
}
