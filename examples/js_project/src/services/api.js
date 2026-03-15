import { getToken } from './auth.js';

const BASE_URL = 'https://api.example.com';

export async function fetchData(endpoint) {
  const token = getToken();
  const response = await fetch(`${BASE_URL}${endpoint}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  return response.json();
}

export async function postData(endpoint, data) {
  const token = getToken();
  const response = await fetch(`${BASE_URL}${endpoint}`, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });
  return response.json();
}
