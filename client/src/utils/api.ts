const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

export async function analyzeText(text: string) {
  const response = await fetch(`${API_BASE_URL}/detect`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ text }),
  });

  if (!response.ok) {
    throw new Error('Failed to analyze text');
  }

  return response.json();
}

export async function healthCheck() {
  const response = await fetch(`${API_BASE_URL}/health`);
  
  if (!response.ok) {
    throw new Error('API health check failed');
  }
  
  return response.json();
}
