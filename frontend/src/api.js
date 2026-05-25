export async function startJob() {
  const res = await fetch("http://localhost:8000/start", {
    method: "POST",
  });
  return res.json();
}
