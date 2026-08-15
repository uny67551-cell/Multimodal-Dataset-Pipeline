const API = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000"; //set the API base URL to the value of the VITE_API_BASE environment variable, or to http://127.0.0.1:8000 if the environment variable is not set

async function request(path, options = {}) {
  const res = await fetch(`${API}${path}`, options);
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`${res.status} ${text}`);
  }
  const contentType = res.headers.get("content-type") || "";
  if (contentType.includes("application/json")) {
    return res.json();
  }
  return res;
}

export function getHealth() {
  return request("/api/health");
}

export function getReports() {
  return request("/api/reports");
}

export function getGallery() {
  return request("/api/gallery");
}

export function imageUrl(id) {
  return `${API}/api/images/${id}`;
}

export function listUploads() {
  return request("/api/uploads");
}

export function uploadFiles(fileList) {
  const body = new FormData();
  for (const file of fileList) {
    body.append("files", file);
  }
  return request("/api/uploads", { method: "POST", body });
}

export function runStage(name, jsonBody) {
  const options = { method: "POST" };
  if (jsonBody) {
    options.headers = { "Content-Type": "application/json" };
    options.body = JSON.stringify(jsonBody);
  }
  return request(`/api/pipeline/${name}`, options);
}