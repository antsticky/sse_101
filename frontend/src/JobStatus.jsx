import { useEffect, useState } from "react";

export default function JobStatus({ jobId }) {
  const [status, setStatus] = useState("queued");
  const [progress, setProgress] = useState(0);
  const [message, setMessage] = useState("Waiting...");
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    if (!jobId) return;

    const url = `http://localhost:8000/events?job_id=${jobId}`;
    const evtSource = new EventSource(url);

    evtSource.onopen = () => {
      setConnected(true);
    };

    evtSource.onmessage = (e) => {
      if (e.data === "heartbeat") return;

      const data = JSON.parse(e.data);

      setStatus(data.status);
      setProgress(Number(data.progress));
      setMessage(data.message);

      if (data.status === "finished" || data.status === "error") {
        evtSource.close();
        setConnected(false);
      }
    };

    evtSource.onerror = () => {
      setConnected(false);
    };

    return () => evtSource.close();
  }, [jobId]);

  return (
    <div style={{ marginTop: "20px" }}>
      <h2>Job ID: {jobId}</h2>
      <p>Status: {status}</p>
      <p>Message: {message}</p>
      <p>Progress: {progress}%</p>

      <div
        style={{
          width: "100%",
          height: "20px",
          background: "#ddd",
          marginTop: "10px",
        }}
      >
        <div
          style={{
            width: `${progress}%`,
            height: "100%",
            background: "green",
            transition: "width 0.3s",
          }}
        />
      </div>

      <p style={{ marginTop: "10px", color: connected ? "green" : "red" }}>
        SSE connection: {connected ? "connected" : "closed"}
      </p>
    </div>
  );
}
