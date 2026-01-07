const API_BASE_URL = 'http://localhost:5000/api';

export async function analyzeText(text: string) {
  const response = await fetch(`${API_BASE_URL}/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text, use_fuzzy: true }),
  });

  if (!response.ok) throw new Error('Failed to analyze text');

  const data = await response.json();
  const transformations = data.transformations || [];

  return {
    original_text: data.original,
    detected_obfuscation: data.analysis?.isObfuscated ?? false,
    obfuscation_percentage: (data.analysis?.confidence ?? 0) * 100,
    deciphered_text: data.deobfuscated,
    fuzzy_matches: transformations.map(t => ({
      original: t.original,
      match: t.corrected,
      score: 95
    })),
    character_count: data.original.length,
  };
}

export async function detectObfuscation(text: string) {
  // Just detect obfuscation patterns
  const response = await fetch(`${API_BASE_URL}/detect`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ text }),
  });

  if (!response.ok) {
    throw new Error('Detection failed');
  }

  return response.json();
}

export async function deobfuscateText(text: string, use_fuzzy: boolean = true) {
  // Just deobfuscate text
  const response = await fetch(`${API_BASE_URL}/deobfuscate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ text, use_fuzzy }),
  });

  if (!response.ok) {
    throw new Error('Deobfuscation failed');
  }

  return response.json();
}

export async function healthCheck() {
  // Check if API is available
  try {
    const response = await fetch(`${API_BASE_URL}/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ text: 'test' }),
    });
    
    return response.ok;
  } catch {
    return false;
  }
}