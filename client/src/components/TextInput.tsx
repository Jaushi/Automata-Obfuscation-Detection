interface TextInputProps {
  value: string;
  onChange: (value: string) => void;
  onAnalyze: () => void;
  onClear: () => void;
  isAnalyzing: boolean;
}

export default function TextInput({ value, onChange, onAnalyze, onClear, isAnalyzing }: TextInputProps) {
  const charCount = value.length;

  return (
    <div>
      <label className="block text-xl font-semibold text-gray-700 mb-3">
        Enter Taglish Obfuscated Text
      </label>
      
      <div className="relative">
        <textarea
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder="Type or paste your text here... (e.g., 'h3ll0 w0r1d', 'k4m5t4 n4 p0')"
          className="w-full h-48 p-4 text-lg border-2 border-gray-300 rounded-lg focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 outline-none transition-all resize-none"
          disabled={isAnalyzing}
        />
        
        {value && (
          <button
            onClick={onClear}
            className="absolute top-4 right-4 p-2 text-gray-400 hover:text-gray-600 transition-colors"
            title="Clear text"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        )}
      </div>

      <div className="flex items-center justify-between mt-4">
        <span className="text-sm text-gray-500">
          {charCount} character{charCount !== 1 ? 's' : ''}
        </span>
        
        <button
          onClick={onAnalyze}
          disabled={isAnalyzing || !value.trim()}
          className="flex items-center gap-2 px-8 py-3 bg-indigo-600 text-white font-semibold rounded-lg hover:bg-indigo-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          {isAnalyzing ? 'Analyzing...' : 'Analyze'}
        </button>
      </div>
    </div>
  );
}
