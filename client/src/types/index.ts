export interface DetectionResult {
  isObfuscated: boolean
  confidence: number
  patterns: string[]
}

export interface AnalysisRequest {
  code: string
  language?: string
}

export interface FuzzyMatch {
  original: string
  match: string
  score: number
}

export interface FuzzyAnalysisResult {
  original_text: string
  detected_obfuscation: boolean
  obfuscation_percentage: number
  deciphered_text: string
  character_count: number
  fuzzy_matches: FuzzyMatch[]
  confidence: number
}
