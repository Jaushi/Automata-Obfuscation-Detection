import { useEffect, useState } from 'react';

interface AnalysisResult {
  original_text: string;
  detected_obfuscation: boolean;
  obfuscation_percentage: number;
  deciphered_text?: string;
  language_distribution: {
    tagalog: number;
    english: number;
  };
  character_count: number;
}

export default function OverlayView() {
  const [text, setText] = useState('');
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    // Listen for text from main process
    if (window.electronAPI) {
      window.electronAPI.onAnalyzeText((receivedText: string) => {
        setText(receivedText);
        analyzeText(receivedText);
      });
    }
  }, []);

  const analyzeText = async (textToAnalyze: string) => {
    if (!textToAnalyze.trim()) return;

    setIsLoading(true);
    try {
      const analysisResult = await window.electronAPI.analyzeText(textToAnalyze);
      setResult(analysisResult);
    } catch (error) {
      console.error('Analysis failed:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleClose = () => {
    window.electronAPI.hideOverlay();
  };

  return (
    <div className="w-full h-full flex items-center justify-center p-4">
      {/* Siri-style frosted glass overlay */}
      <div className="w-full max-w-md bg-white/80 backdrop-blur-2xl rounded-3xl shadow-2xl border border-white/20 overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 bg-gradient-to-r from-indigo-500/20 to-purple-500/20">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-full flex items-center justify-center">
              <span className="text-white text-sm font-bold">T</span>
            </div>
            <h2 className="text-lg font-semibold text-gray-800">Taglish Detector</h2>
          </div>
          <button
            onClick={handleClose}
            className="w-8 h-8 rounded-full hover:bg-gray-200/50 flex items-center justify-center transition-colors"
          >
            <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Content */}
        <div className="px-6 py-4">
          {isLoading ? (
            <div className="flex flex-col items-center justify-center py-8">
              <div className="w-12 h-12 border-4 border-indigo-500/30 border-t-indigo-500 rounded-full animate-spin mb-4"></div>
              <p className="text-gray-600">Analyzing text...</p>
            </div>
          ) : result ? (
            <div className="space-y-4">
              {/* Status Badge */}
              <div className={`inline-flex items-center gap-2 px-4 py-2 rounded-full ${
                result.detected_obfuscation 
                  ? 'bg-red-100 text-red-700' 
                  : 'bg-green-100 text-green-700'
              }`}>
                {result.detected_obfuscation ? (
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                  </svg>
                ) : (
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                )}
                <span className="text-sm font-semibold">
                  {result.detected_obfuscation ? 'Obfuscated' : 'Clear'}
                </span>
              </div>

              {/* Original Text */}
              <div>
                <label className="block text-xs font-semibold text-gray-500 mb-1">Original</label>
                <div className="px-4 py-3 bg-gray-100/50 rounded-xl">
                  <p className="text-sm text-gray-700 font-mono break-words">{result.original_text}</p>
                </div>
              </div>

              {/* Deciphered Text */}
              {result.detected_obfuscation && result.deciphered_text && (
                <div>
                  <label className="block text-xs font-semibold text-gray-500 mb-1">Deciphered</label>
                  <div className="px-4 py-3 bg-gradient-to-br from-indigo-50 to-purple-50 rounded-xl">
                    <p className="text-sm text-indigo-900 font-mono break-words font-semibold">
                      {result.deciphered_text}
                    </p>
                  </div>
                </div>
              )}

              {/* Quick Stats */}
              <div className="flex gap-2 pt-2">
                <div className="flex-1 text-center px-3 py-2 bg-gray-100/50 rounded-lg">
                  <div className="text-xs text-gray-500">Obfuscation</div>
                  <div className="text-lg font-bold text-indigo-600">
                    {result.obfuscation_percentage.toFixed(0)}%
                  </div>
                </div>
                <div className="flex-1 text-center px-3 py-2 bg-gray-100/50 rounded-lg">
                  <div className="text-xs text-gray-500">Characters</div>
                  <div className="text-lg font-bold text-purple-600">
                    {result.character_count}
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="py-8 text-center">
              <div className="w-16 h-16 mx-auto mb-4 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-2xl flex items-center justify-center">
                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <p className="text-gray-600 text-sm">
                Select text and press <br />
                <kbd className="px-2 py-1 bg-gray-200 rounded text-xs font-mono">Ctrl+Shift+D</kbd> to analyze
              </p>
            </div>
          )}
        </div>

        {/* Footer hint */}
        <div className="px-6 py-3 bg-gray-50/50 border-t border-gray-200/50">
          <p className="text-xs text-gray-500 text-center">
            Press ESC or click outside to close
          </p>
        </div>
      </div>
    </div>
  );
}
