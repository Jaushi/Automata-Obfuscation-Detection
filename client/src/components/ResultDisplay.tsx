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
    <div className="max-w-5xl mx-auto bg-white rounded-2xl shadow-xl p-8">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">
        Analysis Results
      </h2>

      <div className="space-y-6">
        {/* Obfuscation Status */}
        <div className="flex items-center gap-3">
          <div
            className={`flex items-center gap-2 px-4 py-2 rounded-lg ${
              result.detected_obfuscation
                ? "bg-red-100 text-red-800"
                : "bg-green-100 text-green-800"
            }`}
          >
            <span className="font-semibold">
              {result.detected_obfuscation
                ? "Obfuscation Detected"
                : "No Obfuscation Detected"}
            </span>
          </div>

          {result.detected_obfuscation && (
            <span className="text-gray-600">
              {result.obfuscation_percentage.toFixed(1)}% obfuscated
            </span>
          )}
        </div>

        {/* Original Text */}
        <div>
          <label className="block text-sm font-semibold text-gray-600 mb-2">
            Original Text
          </label>
          <div className="p-4 bg-gray-50 rounded-lg border border-gray-200">
            <p className="text-lg text-gray-800 font-mono break-words">
              {result.original_text}
            </p>
          </div>
        </div>

        {/* Fuzzy Matches */}
        {result.fuzzy_matches && result.fuzzy_matches.length > 0 && (
          <div>
            <label className="block text-sm font-semibold text-gray-600 mb-2">
              Detected Obfuscations ({result.fuzzy_matches.length} found)
            </label>
            <div className="space-y-2">
              {result.fuzzy_matches.map((match, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between p-3 bg-purple-50 rounded-lg border border-purple-200"
                >
                  <div className="flex items-center gap-3">
                    <span className="px-3 py-1 bg-red-100 text-red-800 font-mono rounded">
                      {match.original}
                    </span>
                    <svg
                      className="w-5 h-5 text-gray-400"
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
                    <span className="px-3 py-1 bg-green-100 text-green-800 font-mono rounded">
                      {match.match}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Deciphered Text */}
        {result.deciphered_text && (
          <div>
            <label className="block text-sm font-semibold text-gray-600 mb-2">
              Deciphered Text
            </label>
            <div className="p-4 bg-indigo-50 rounded-lg border border-indigo-200">
              <p className="text-lg text-indigo-900 font-mono break-words">
                {result.deciphered_text}
              </p>
            </div>
          </div>
        )}

        {/* Statistics */}
        <div className="grid grid-cols-2 gap-4 pt-4 border-t">
          <div className="text-center p-4 bg-gray-50 rounded-lg">
            <div className="text-3xl font-bold text-indigo-600">
              {result.character_count}
            </div>
            <div className="text-sm text-gray-600 mt-1">Total Characters</div>
          </div>
          <div className="text-center p-4 bg-gray-50 rounded-lg">
            <div className="text-3xl font-bold text-purple-600">
              {result.obfuscation_percentage.toFixed(1)}%
            </div>
            <div className="text-sm text-gray-600 mt-1">Obfuscation Rate</div>
          </div>
        </div>
      </div>
    </div>
  );
}
