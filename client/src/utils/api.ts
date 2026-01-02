const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

export async function analyzeText(text: string) {
  const response = await fetch(`${API_BASE_URL}/translate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ text }),
  });

  if (!response.ok) {
    throw new Error('Failed to analyze text');
  }

  const data = await response.json();

  // Map backend /translate response to frontend AnalysisResult shape
  const original = data.original ?? text;
  const translated = data.translated ?? '';

  const origTokens = original.split(/\s+/).filter(Boolean);
  const transTokens = translated.split(/\s+/).filter(Boolean);
  const maxLen = Math.max(origTokens.length, transTokens.length, 1);
  let diffCount = 0;
  for (let i = 0; i < maxLen; i++) {
    if (origTokens[i] !== transTokens[i]) diffCount++;
  }

  const obfuscation_percentage = Math.min(100, (diffCount / maxLen) * 100);

  return {
    original_text: original,
    detected_obfuscation: original !== translated,
    obfuscation_percentage,
    deciphered_text: translated,
    language_distribution: {
      tagalog: 0.5,
      english: 0.5,
    },
    character_count: original.length,
  };
}

export async function healthCheck() {
  const response = await fetch(`${API_BASE_URL}/health`);
  
  if (!response.ok) {
    throw new Error('API health check failed');
  }
  
  return response.json();
}

export async function detectWithFuzzy(text: string, threshold: number = 75) {
  const response = await fetch(`${API_BASE_URL}/detect/fuzzy`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ text, threshold }),
  });
  
  if (!response.ok) {
    throw new Error('Fuzzy detection failed');
  }
  
  return response.json();
}
