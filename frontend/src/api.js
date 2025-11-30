const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

async function handleResponse(response) {
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || 'Request failed');
  }
  if (response.status === 204) {
    return null;
  }
  return response.json();
}

export async function fetchShows(status) {
  const query = status && status !== 'all' ? `?status=${status}` : '';
  const res = await fetch(`${API_URL}/shows${query}`);
  return handleResponse(res);
}

export async function fetchShow(id) {
  const res = await fetch(`${API_URL}/shows/${id}`);
  return handleResponse(res);
}

export async function sendEmail(payload) {
  const res = await fetch(`${API_URL}/emails/send`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  return handleResponse(res);
}
