const BASE_URL = import.meta.env.VITE_API_URL || '/api/v1';

async function fetchWithCatch(url, options) {
  try {
    const response = await fetch(url, options);
    if (!response.ok) {
      if (response.status === 404) return null;
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('API Error:', error);
    return null;
  }
}

export async function getInfluencers(filters = {}) {
  const params = new URLSearchParams();
  for (const [key, value] of Object.entries(filters)) {
    if (value !== undefined && value !== null && value !== '') {
      params.append(key, value);
    }
  }
  const res = await fetchWithCatch(`${BASE_URL}/influencers/?${params.toString()}`);
  return res || [];
}

export async function getInfluencer(id, brandId) {
  let url = `${BASE_URL}/influencers/${id}`;
  if (brandId) url += `?brand_id=${brandId}`;
  return fetchWithCatch(url);
}

export async function createInfluencer(payload) {
  return fetchWithCatch(`${BASE_URL}/influencers/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
}

export async function updateInfluencer(id, payload) {
  return fetchWithCatch(`${BASE_URL}/influencers/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
}

export async function getBrands(filters = {}) {
  const params = new URLSearchParams();
  for (const [key, value] of Object.entries(filters)) {
    if (value !== undefined && value !== null && value !== '') {
      params.append(key, value);
    }
  }
  const res = await fetchWithCatch(`${BASE_URL}/brands/?${params.toString()}`);
  return res || [];
}

export async function getBrand(id, influencerId) {
  let url = `${BASE_URL}/brands/${id}`;
  if (influencerId) url += `?influencer_id=${influencerId}`;
  return fetchWithCatch(url);
}

export async function createBrand(payload) {
  return fetchWithCatch(`${BASE_URL}/brands/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
}

export async function updateBrand(id, payload) {
  return fetchWithCatch(`${BASE_URL}/brands/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
}

export async function generateMatch(brandId, influencerId) {
  return fetchWithCatch(`${BASE_URL}/matches/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ brand_id: brandId, influencer_id: influencerId }),
  });
}

export async function getPastCollaborations(influencerId) {
  const res = await fetchWithCatch(`${BASE_URL}/past-collaborations/?influencer_id=${influencerId}`);
  return res || [];
}

export async function sendContact(payload) {
  return fetchWithCatch(`${BASE_URL}/contact/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
}

export async function getContactRequests(userId, direction) {
  let url = `${BASE_URL}/contact-requests/?user_id=${userId}`;
  if (direction) url += `&direction=${direction}`;
  const res = await fetchWithCatch(url);
  return res || [];
}

export async function updateContactRequest(requestId, status) {
  return fetchWithCatch(`${BASE_URL}/contact-requests/${requestId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ status }),
  });
}

export async function getStats() {
  const res = await fetchWithCatch(`${BASE_URL}/stats/`);
  return res || { creator_count: 0, brand_count: 0, avg_roi: 0 };
}
