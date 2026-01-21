const DEFAULT_BASE_URL = "https://backend-ktuk.onrender.com";
// const DEFAULT_BASE_URL = "http://localhost:5000";
export const API_BASE_URL =DEFAULT_BASE_URL;

async function parseJsonSafe(res) {
  const text = await res.text();
  try {
    return text ? JSON.parse(text) : null;
  } catch {
    return text;
  }
}

export async function postFormData(path, formData) {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    method: "POST",
    body: formData,
  });

  const data = await parseJsonSafe(res);
  if (!res.ok) {
    const msg =
      (data && data.message) || `Request failed (${res.status})`;
    throw new Error(msg);
  }
  return data;
}


