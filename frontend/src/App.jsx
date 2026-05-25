import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import { JobProvider } from "./JobStore";
import JobList from "./JobList";
import JobDetail from "./JobDetail";

export default function App() {
  return (
    <JobProvider>
      <BrowserRouter>
        <nav style={{ padding: 10 }}>
          <Link to="/">Home</Link>
        </nav>

        <Routes>
          <Route path="/" element={<JobList />} />
          <Route path="/job/:jobId" element={<JobDetail />} />
        </Routes>
      </BrowserRouter>
    </JobProvider>
  );
}
