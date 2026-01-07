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
      <label className="block text-base font-medium text-gray-700 mb-4">
        Enter Taglish Obfuscated Text
      </label>
      
      <div className="relative">
        <textarea
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && (e.metaKey || e.ctrlKey) && value.trim()) {
              onAnalyze();
            }
          }}
          placeholder="Type or paste your text here... (e.g., 'h3ll0 w0r1d', 'k4m5t4 n4 p0')"
          className="w-full h-48 p-5 text-base border border-gray-200 rounded-md focus:border-gray-300 focus:ring-0 outline-none transition-colors resize-none text-gray-900 placeholder-gray-400 bg-white"
          disabled={isAnalyzing}
        />
        
        {value && (
          <button
            onClick={onClear}
            className="absolute top-3 right-3 p-1 text-gray-400 hover:text-gray-600 transition-colors rounded"
            title="Clear text"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        )}
      </div>

      <div className="flex items-center justify-between mt-4">
        <span className="text-sm text-gray-500">
          {charCount}/500 characters
        </span>
        
        <button
          onClick={onAnalyze}
          disabled={!value.trim() && !isAnalyzing}
          style={{
            backgroundColor: (value.trim() || isAnalyzing) ? '#9333ea' : '#e5e7eb',
            color: (value.trim() || isAnalyzing) ? '#ffffff' : '#9ca3af'
          }}
          className="px-8 py-3 font-medium rounded-full transition-colors text-base disabled:cursor-not-allowed"
        >
          {isAnalyzing ? 'Analyzing...' : 'Analyze'}
        </button>
      </div>
    </div>
  );
}