interface FuzzyMatch {
  original: string;
  match: string;
  score: number;
}

interface ResultDisplayProps {
  result: {
    original_text: string;
    detected_obfuscation: boolean;
    obfuscation_percentage: number;
    deciphered_text?: string;
    character_count: number;
    fuzzy_matches?: FuzzyMatch[];
    confidence?: number;
  };
}

export default function ResultDisplay({ result }: ResultDisplayProps) {
  return (
    <div className="bg-white rounded-lg p-6 border border-gray-200">
      <h2 className="text-lg font-semibold text-gray-900 mb-6">
        Analysis Results
      </h2>

      <p className="disclaimer-text mb-4 text-xs text-gray-500">
        {" "}
        Confidence scores reflect the strength of detected obfuscation patterns
        not semantic correctness or translation accuracy.{" "}
      </p>

      {/* Statistics */}
      <div className="grid grid-cols-2 gap-4 mb-6 pb-6 border-b border-gray-200">
        <div className="text-center p-4">
          <div className="text-2xl font-semibold text-gray-900">
            {result.character_count}
          </div>
          <div className="text-xs text-gray-500 mt-1">Total Characters</div>
        </div>
        <div className="text-center p-4">
          <div className="text-2xl font-semibold text-primary">
            {result.obfuscation_percentage.toFixed(1)}%
          </div>
          <div className="text-xs text-gray-500 mt-1">Obfuscation Rate</div>
        </div>
      </div>

      <div className="space-y-6">
        {/* Obfuscation Status */}
        <div className="flex items-center gap-3">
          <div
            className={`flex items-center gap-2 px-3 py-1.5 rounded ${
              result.detected_obfuscation
                ? "bg-red-50 text-red-700 border border-red-100"
                : "bg-green-50 text-green-700 border border-green-100"
            }`}
          >
            <span className="font-medium text-sm">
              {result.detected_obfuscation
                ? "Obfuscation Detected"
                : "No Obfuscation Detected"}
            </span>
          </div>

          {result.detected_obfuscation && (
            <span className="text-sm text-gray-600">
              {result.obfuscation_percentage.toFixed(1)}% obfuscated
            </span>
          )}
        </div>

        {/* Original Text */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Original Text
          </label>
          <div className="p-3 bg-gray-50 rounded border border-gray-200">
            <pre className="text-sm text-gray-900 break-words whitespace-pre-wrap font-sans">
              {result.original_text}
            </pre>
          </div>
        </div>

        {/* Deciphered Text */}
        {result.deciphered_text && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Deciphered Text
            </label>
            <div className="p-3 bg-gray-50 rounded border border-gray-200">
              <pre className="text-sm text-gray-900 break-words whitespace-pre-wrap font-sans">
                {result.deciphered_text}
              </pre>
            </div>
          </div>
        )}

        {/* Fuzzy Matches */}
        {result.fuzzy_matches && result.fuzzy_matches.length > 0 && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Detected Obfuscations ({result.fuzzy_matches.length} found)
            </label>
            <div className="space-y-2">
              {result.fuzzy_matches.map((match, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between p-3 bg-gray-50 rounded border border-gray-200"
                >
                  <div className="flex items-center gap-3">
                    <span className="px-2.5 py-1 bg-red-50 text-red-700 text-sm rounded border border-red-100">
                      {match.original}
                    </span>
                    <svg
                      className="w-4 h-4 text-gray-400"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M13 7l5 5m0 0l-5 5m5-5H6"
                      />
                    </svg>
                    <span
                      className="px-2.5 py-1 text-sm rounded border text-primary"
                      style={{
                        backgroundColor: "rgba(147, 51, 234, 0.1)",
                        borderColor: "rgba(147, 51, 234, 0.3)",
                      }}
                    >
                      {match.match}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
