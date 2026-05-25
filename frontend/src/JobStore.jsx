import { createContext, useContext, useState } from "react";

const JobContext = createContext(null);

export function JobProvider({ children }) {
  const [jobs, setJobs] = useState({});
  return (
    <JobContext.Provider value={{ jobs, setJobs }}>
      {children}
    </JobContext.Provider>
  );
}

export function useJobs() {
  return useContext(JobContext);
}
