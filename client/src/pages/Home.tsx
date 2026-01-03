import { useState } from 'react';
import TextInput from '../components/TextInput';
import ResultDisplay from '../components/ResultDisplay';
import { analyzeText } from '../utils/api';

interface AnalysisResult {
  original_text: string;
  detected_obfuscation: boolean;
  obfuscation_percentage: number;
  deciphered_text?: string;
  character_count: number;
  confidence?: number;
  fuzzy_matches?: Array<{
    original: string;
    match: string;
    score: number;
  }>;
}

function Home() {
  const [activeTab, setActiveTab] = useState<'detector' | 'about'>('detector');
  const [text, setText] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleAnalyze = async () => {
    if (!text.trim()) {
      setError('Please enter some text to analyze');
      return;
    }

    setIsAnalyzing(true);
    setError(null);
    
    try {
      const analysisResult = await analyzeText(text);
      
      setResult({
        original_text: analysisResult.original_text,
        detected_obfuscation: analysisResult.detected_obfuscation,
        obfuscation_percentage: analysisResult.obfuscation_percentage,
        deciphered_text: analysisResult.deciphered_text,
        character_count: analysisResult.character_count,
        fuzzy_matches: analysisResult.fuzzy_matches,
      });
    } catch (err) {
      setError('Failed to analyze text. Please try again.');
      console.error(err);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleClear = () => {
    setText('');
    setResult(null);
    setError(null);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-blue-50 to-indigo-50">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-5xl font-bold text-indigo-900 mb-2">
            Taglish Obfuscation Detector
          </h1>
          <p className="text-lg text-gray-600">
            Finite Automata-based Detection & Deobfuscation System
          </p>
        </div>

        {/* Tabs */}
        <div className="flex justify-center mb-8">
          <div className="inline-flex rounded-lg shadow-sm">
            <button
              onClick={() => setActiveTab('detector')}
              className={`px-8 py-3 text-lg font-semibold rounded-l-lg transition-colors ${
                activeTab === 'detector'
                  ? 'bg-indigo-600 text-white'
                  : 'bg-white text-gray-700 hover:bg-gray-50'
              }`}
            >
              Detector
            </button>
            <button
              onClick={() => setActiveTab('about')}
              className={`px-8 py-3 text-lg font-semibold rounded-r-lg transition-colors ${
                activeTab === 'about'
                  ? 'bg-indigo-600 text-white'
                  : 'bg-white text-gray-700 hover:bg-gray-50'
              }`}
            >
              About
            </button>
          </div>
        </div>

        {/* Content */}
        {activeTab === 'detector' ? (
          <div className="max-w-5xl mx-auto">
            <div className="bg-white rounded-2xl shadow-xl p-8 mb-6">
              <TextInput
                value={text}
                onChange={setText}
                onAnalyze={handleAnalyze}
                onClear={handleClear}
                isAnalyzing={isAnalyzing}
              />
              
              {error && (
                <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
                  {error}
                </div>
              )}
            </div>

            {result && (
              <ResultDisplay result={result} />
            )}
          </div>
        ) : (
          <div className="max-w-4xl mx-auto bg-white rounded-2xl shadow-xl p-8">
            <h2 className="text-3xl font-bold text-indigo-900 mb-6">
              About This Project
            </h2>
            <div className="prose prose-lg max-w-none text-gray-700">
              <p className="mb-4">
                The <strong>Taglish Obfuscation Detector</strong> is an advanced system designed to 
                identify and decipher obfuscated Taglish (Tagalog-English) text using finite automata 
                theory, sophisticated fuzzy matching algorithms, and natural language processing techniques.
              </p>
              
              <h3 className="text-2xl font-semibold text-indigo-800 mt-6 mb-3">
                Key Features
              </h3>
              <ul className="list-disc list-inside space-y-2 mb-4">
                <li>Real-time obfuscation detection with accurate percentage calculation</li>
                <li>Automatic deciphering of leetspeak and character substitutions</li>
                <li>Advanced fuzzy matching with multi-factor scoring algorithm</li>
                <li>Word-by-word deobfuscation visualization with confidence scores</li>
                <li>Comprehensive dictionary: 234,499 words (Filipino + English)</li>
                <li>Duplication normalization (heeeey → hey)</li>
                <li>Support for common obfuscation patterns (3→e, 1→i, 0→o, 4→a, 5→s, etc.)</li>
                <li>Character-level finite automata processing</li>
              </ul>

              <h3 className="text-2xl font-semibold text-indigo-800 mt-6 mb-3">
                How It Works
              </h3>
              <ol className="list-decimal list-inside space-y-2 mb-4">
                <li><strong>Detection:</strong> Identifies obfuscation patterns using NFAs and pattern matching</li>
                <li><strong>Transformation:</strong> Reverses leetspeak and normalizes character duplication</li>
                <li><strong>Dictionary Lookup:</strong> Checks against comprehensive Filipino and English dictionaries</li>
                <li><strong>Fuzzy Matching:</strong> Uses multi-factor scoring (Levenshtein distance, length penalties/bonuses, prefix matching) to find the best word match</li>
                <li><strong>Visualization:</strong> Displays word-by-word transformations with confidence scores</li>
                <li><strong>Output:</strong> Returns original text, deobfuscated text, obfuscation percentage, and detailed word matches</li>
              </ol>

              <h3 className="text-2xl font-semibold text-indigo-800 mt-6 mb-3">
                Technology Stack
              </h3>
              <ul className="list-disc list-inside space-y-2 mb-4">
                <li><strong>Frontend:</strong> React + TypeScript + Vite + TailwindCSS</li>
                <li><strong>Backend:</strong> Python Flask with finite automata implementation</li>
                <li><strong>Theory:</strong> Finite State Machines & Pattern Matching</li>
                <li><strong>NLP Libraries:</strong> RapidFuzz (fuzzy matching with Levenshtein distance)</li>
                <li><strong>Dictionaries:</strong> Custom Filipino/Taglish netspeak patterns + English word corpus (JSON-based)</li>
              </ul>

              <h3 className="text-2xl font-semibold text-indigo-800 mt-6 mb-3">
                Fuzzy Matching Algorithm
              </h3>
              <p className="mb-4">
                Our sophisticated multi-factor scoring system ensures accurate word matching:
              </p>
              <ul className="list-disc list-inside space-y-2">
                <li><strong>Base Score:</strong> Levenshtein distance similarity</li>
                <li><strong>Length Penalty:</strong> -5% per missing character (prevents truncated matches)</li>
                <li><strong>Length Bonus:</strong> +4% per character after 3 (favors complete words)</li>
                <li><strong>Prefix Matching:</strong> +3% per matching character in first 3 positions</li>
                <li><strong>Exact Length Match:</strong> +2% bonus when lengths match perfectly</li>
                <li><strong>Dynamic Thresholds:</strong> 75% for 4+ char words, 60% for 3-char words</li>
              </ul>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default Home;