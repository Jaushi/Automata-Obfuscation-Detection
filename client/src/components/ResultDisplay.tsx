interface ResultDisplayProps {
  result: {
    original_text: string;
    detected_obfuscation: boolean;
    obfuscation_percentage: number;
    deciphered_text?: string;
    character_count: number;
  };
}

export default function ResultDisplay({ result }: ResultDisplayProps) {
  return (
    <div className="max-w-5xl mx-auto bg-white rounded-2xl shadow-xl p-8">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">Analysis Results</h2>
      
      <div className="space-y-6">
        {/* Obfuscation Status */}
        <div className="flex items-center gap-3">
          <div className={`flex items-center gap-2 px-4 py-2 rounded-lg ${
            result.detected_obfuscation 
              ? 'bg-red-100 text-red-800' 
              : 'bg-green-100 text-green-800'
          }`}>
            {result.detected_obfuscation ? (
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
            ) : (
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
            )}
            <span className="font-semibold">
              {result.detected_obfuscation ? 'Obfuscation Detected' : 'No Obfuscation Detected'}
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
          <label className="block text-sm font-semibold text-gray-600 mb-2">Original Text</label>
          <div className="p-4 bg-gray-50 rounded-lg border border-gray-200">
            <p className="text-lg text-gray-800 font-mono break-words">{result.original_text}</p>
          </div>
        </div>

        {/* Deciphered Text */}
        {result.detected_obfuscation && result.deciphered_text && (
          <div>
            <label className="block text-sm font-semibold text-gray-600 mb-2">Deciphered Text</label>
            <div className="p-4 bg-indigo-50 rounded-lg border border-indigo-200">
              <p className="text-lg text-indigo-900 font-mono break-words">{result.deciphered_text}</p>
            </div>
          </div>
        )}

        {/* Statistics */}
        <div className="grid grid-cols-2 gap-4 pt-4 border-t">
          <div className="text-center p-4 bg-gray-50 rounded-lg">
            <div className="text-3xl font-bold text-indigo-600">{result.character_count}</div>
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
