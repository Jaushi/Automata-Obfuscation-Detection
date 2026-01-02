const API_BASE_URL = 'http://localhost:5000/api';

export async function analyzeText(text: string) {
  // Full pipeline: detect obfuscation + deobfuscate text
  const response = await fetch(`${API_BASE_URL}/analyze`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ text, use_fuzzy: true }),
  });

  if (!response.ok) {
    throw new Error('Failed to analyze text');
  }

  const data = await response.json();

  // Map backend response to frontend AnalysisResult shape
  const original = data.original ?? text;
  const deobfuscated = data.deobfuscated ?? text;

  // Calculate obfuscation percentage
  const origTokens = original.split(/\s+/).filter(Boolean);
  const deobfTokens = deobfuscated.split(/\s+/).filter(Boolean);
  const maxLen = Math.max(origTokens.length, deobfTokens.length, 1);
  let diffCount = 0;
  
  for (let i = 0; i < maxLen; i++) {
    if (origTokens[i] !== deobfTokens[i]) diffCount++;
  }

  const obfuscation_percentage = data.detection?.confidence 
    ? Math.min(100, (data.detection.confidence * 100))
    : Math.min(100, (diffCount / maxLen) * 100);

  return {
    original_text: original,
    detected_obfuscation: data.detection?.isObfuscated ?? (original !== deobfuscated),
    obfuscation_percentage,
    deciphered_text: deobfuscated,
    language_distribution: {
      tagalog: 0.5,
      english: 0.5,
    },
    character_count: original.length,
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