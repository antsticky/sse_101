import { useEffect, useState } from "react";

async function startJob() {
  const res = await fetch("/start", { method: "POST" });
  const data = await res.json();
  return data.job_id;
}

export default function App() {
  const [messages, setMessages] = useState([]);

  useEffect(() => {
    const run = async () => {
      const jobId = await startJob();

      const evt = new EventSource(`/events?job_id=${jobId}`);

      evt.onmessage = (e) => {
        const [status, progress, message] = e.data.split("|");
        setMessages((prev) => [...prev, { status, progress, message }]);

        if (status === "finished" || status === "error") {
          evt.close();
        }
      };

      evt.onerror = () => {
        console.log("SSE connection lost");
      };
    };

    run();
  }, []);

  return (
    <div>
      <h1>SSE Demo</h1>
      <ul>
        {messages.map((m, i) => (
          <li key={i}>
            {m.status} – {m.progress}% – {m.message}
          </li>
        ))}
      </ul>
    </div>
  );
}
