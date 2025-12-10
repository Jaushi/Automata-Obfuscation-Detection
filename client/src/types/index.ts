export interface DetectionResult {
  isObfuscated: boolean
  confidence: number
  patterns: string[]
}

export interface AnalysisRequest {
  code: string
  language?: string
}
