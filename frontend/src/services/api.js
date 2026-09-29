const API_BASE = '/api/v1';

export async function fetchWells() {
  const res = await fetch(`${API_BASE}/wells`);
  if (!res.ok) throw new Error('Failed to fetch wells');
  return res.json();
}

export async function fetchWellTrajectory(wellId) {
  const res = await fetch(`${API_BASE}/wells/${wellId}/trajectory`);
  if (!res.ok) throw new Error(`Failed to fetch trajectory for ${wellId}`);
  return res.json();
}

export async function fetchStratigraphy() {
  const res = await fetch(`${API_BASE}/stratigraphy`);
  if (!res.ok) throw new Error('Failed to fetch stratigraphy sequence');
  return res.json();
}

export async function fetchWellLogs(wellId) {
  const res = await fetch(`${API_BASE}/stratigraphy/logs/${wellId}`);
  if (!res.ok) throw new Error(`Failed to fetch logs for ${wellId}`);
  return res.json();
}

export async function sendAlertFeedback(alertId, action, comments = '') {
  const res = await fetch(`${API_BASE}/alerts/feedback`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ alert_id: alertId, user_action: action, comments })
  });
  return res.json();
}

export async function fetchReviewQueue() {
  const res = await fetch(`${API_BASE}/documents/review-queue`);
  if (!res.ok) throw new Error('Failed to fetch reviewer queue');
  return res.json();
}

export async function verifyDocumentRecord(eventId) {
  const res = await fetch(`${API_BASE}/documents/${eventId}/verify`, { method: 'POST' });
  if (!res.ok) throw new Error('Failed to verify document record');
  return res.json();
}

export async function runBacktest() {
  const res = await fetch(`${API_BASE}/backtest/run`);
  if (!res.ok) throw new Error('Failed to run backtest engine');
  return res.json();
}
