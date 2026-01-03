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

  // Extract fuzzy matches from original and deobfuscated text
  const fuzzy_matches = [];
  const origWords = original.split(/\s+/);
  const deobWords = deobfuscated.split(/\s+/);
  
  for (let i = 0; i < Math.min(origWords.length, deobWords.length); i++) {
    if (origWords[i] !== deobWords[i]) {
      fuzzy_matches.push({
        original: origWords[i],
        match: deobWords[i],
        score: 95 // Default confidence score
      });
    }
  }

  // If no changes were made, it's not obfuscated
  const hasChanges = fuzzy_matches.length > 0;
  
  // Calculate percentage based on actual word changes
  const obfuscation_percentage = hasChanges 
    ? Math.min(100, (fuzzy_matches.length / origWords.length) * 100)
    : 0;

  return {
    original_text: original,
    detected_obfuscation: hasChanges,
    obfuscation_percentage: obfuscation_percentage,
    deciphered_text: deobfuscated,
    fuzzy_matches: fuzzy_matches,
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