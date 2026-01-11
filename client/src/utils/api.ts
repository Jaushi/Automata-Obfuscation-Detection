const API_BASE_URL = 'http://localhost:5000/api';

/**
 * Response types matching actual API responses
 */
export interface AnalysisResponse {
  success: boolean;
  original: string;
  deobfuscated: string;
  is_obfuscated: boolean;
  confidence: number;
  obfuscation_types: string[];
  fuzzy_matches: Array<{ original: string; match: string; score: number }>;
  transformations?: Array<{ original: string; corrected: string }>;
  status: string;
  error?: string;
}

export interface AnalysisResult {
  original_text: string;
  detected_obfuscation: boolean;
  status: string;
  obfuscation_percentage: number;
  deciphered_text: string;
  fuzzy_matches: Array<{ original: string; match: string; score: number }>;
  character_count: number;
}

/**
 * Full analysis: detect + deobfuscate
 * 
 * Formats API response into user-friendly result
 */
export async function analyzeText(text: string): Promise<AnalysisResult> {
  const response = await fetch(`${API_BASE_URL}/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text, use_fuzzy: true }),
  });

  if (!response.ok) {
    throw new Error('Failed to analyze text');
  }

  const data: AnalysisResponse = await response.json();
  
  // Use fuzzy_matches from API, or build from transformations if needed
  let fuzzy_matches = data.fuzzy_matches || [];
  
  if (fuzzy_matches.length === 0 && data.transformations) {
    fuzzy_matches = data.transformations.map(t => ({
      original: t.original,
      match: t.corrected,
      score: 95,
    }));
  }

  return {
    original_text: data.original,
    detected_obfuscation: data.is_obfuscated,
    status: data.status || 'unknown',
    obfuscation_percentage: data.confidence * 100,
    deciphered_text: data.deobfuscated,
    fuzzy_matches,
    character_count: data.original.length,
  };
}

export async function detectObfuscation(text: string) {
  const response = await fetch(`${API_BASE_URL}/detect`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text }),
  });

  if (!response.ok) {
    throw new Error('Detection failed');
  }

  return response.json();
}

/**
 * Deobfuscate text only
 * 
 * Skips detection, goes straight to deobfuscation
 */
export async function deobfuscateText(
  text: string,
  use_fuzzy: boolean = true
) {
  const response = await fetch(`${API_BASE_URL}/deobfuscate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text, use_fuzzy }),
  });

  if (!response.ok) {
    throw new Error('Deobfuscation failed');
  }

  return response.json();
}

/**
 * Health check - verify API is available
 */
export async function healthCheck(): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE_URL}/health`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
    });

    return response.ok;
  } catch {
    return false;
  }
}