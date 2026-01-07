import { useState } from 'react';
import TextInput from '../components/TextInput';
import ResultDisplay from '../components/ResultDisplay';
import { analyzeText } from '../utils/api';
import logo from '../assets/auto-decode-logo.png';

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
    <div className="min-h-screen" style={{ backgroundColor: '#f9fafb' }}>
      <div className="container mx-auto pt-16 px-8 pb-8 max-w-5xl">
        {/* Header */}
        <div className="mb-10">
          <div className="mb-3 flex justify-center">
            <img src={logo} alt="Auto Decode Logo" className="h-16" />
          </div>
          <p className="text-center text-sm text-gray-500">
            Decoding Filipino Netspeak: Finite Automata for Taglish Obfuscation Detection
          </p>
        </div>

        {/* Tabs */}
        <div className="flex gap-0 mb-8 border-b border-gray-200">
          <button
            onClick={() => setActiveTab('detector')}
            className={`px-8 py-4 text-base font-semibold transition-colors border-b-2 ${
              activeTab === 'detector'
                ? 'text-primary border-primary'
                : 'text-gray-500 border-transparent hover:text-gray-700'
            }`}
          >
            Detector
          </button>
          <button
            onClick={() => setActiveTab('about')}
            className={`px-8 py-4 text-base font-semibold transition-colors border-b-2 ${
              activeTab === 'about'
                ? 'text-primary border-primary'
                : 'text-gray-500 border-transparent hover:text-gray-700'
            }`}
          >
            About
          </button>
        </div>

        {/* Content */}
        {activeTab === 'detector' ? (
          <div className="space-y-4">
            <div className="bg-white rounded-lg border border-gray-200 p-8">
              <TextInput
                value={text}
                onChange={setText}
                onAnalyze={handleAnalyze}
                onClear={handleClear}
                isAnalyzing={isAnalyzing}
              />
              
              {error && (
                <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded text-red-700 text-sm">
                  {error}
                </div>
              )}
            </div>

            {result && (
              <ResultDisplay result={result} />
            )}
          </div>
        ) : (
          <div className="bg-white rounded-lg border border-gray-200 p-8">
            <h2 className="text-2xl font-semibold text-gray-900 mb-8">
              About This Project
            </h2>
            <div className="space-y-8 text-base text-gray-600">
              <p className="leading-relaxed">
                The <strong className="text-gray-900">Taglish Obfuscation Detector</strong> is an advanced system designed to 
                identify and decipher obfuscated Taglish (Tagalog-English) text using finite automata 
                theory, sophisticated fuzzy matching algorithms, and natural language processing techniques.
              </p>
              
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Key Features
                </h3>
                <ul className="list-disc list-outside space-y-2 text-gray-600 ml-6">
                  <li>Real-time obfuscation detection with accurate percentage calculation</li>
                  <li>Automatic deciphering of leetspeak and character substitutions</li>
                  <li>Advanced fuzzy matching with multi-factor scoring algorithm</li>
                  <li>Word-by-word deobfuscation visualization with confidence scores</li>
                  <li>Comprehensive dictionary: 234,499 words (Filipino + English)</li>
                  <li>Duplication normalization (heeeey → hey)</li>
                  <li>Support for common obfuscation patterns (3→e, 1→i, 0→o, 4→a, 5→s, etc.)</li>
                  <li>Character-level finite automata processing</li>
                </ul>
              </div>

              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  How It Works
                </h3>
                <ol className="list-decimal list-outside space-y-2 text-gray-600 ml-6">
                  <li><strong className="text-gray-900">Detection:</strong> Identifies obfuscation patterns using NFAs and pattern matching</li>
                  <li><strong className="text-gray-900">Transformation:</strong> Reverses leetspeak and normalizes character duplication</li>
                  <li><strong className="text-gray-900">Dictionary Lookup:</strong> Checks against comprehensive Filipino and English dictionaries</li>
                  <li><strong className="text-gray-900">Fuzzy Matching:</strong> Uses multi-factor scoring (Levenshtein distance, length penalties/bonuses, prefix matching) to find the best word match</li>
                  <li><strong className="text-gray-900">Visualization:</strong> Displays word-by-word transformations with confidence scores</li>
                  <li><strong className="text-gray-900">Output:</strong> Returns original text, deobfuscated text, obfuscation percentage, and detailed word matches</li>
                </ol>
              </div>

              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Technology Stack
                </h3>
                <ul className="list-disc list-outside space-y-2 text-gray-600 ml-6">
                  <li><strong className="text-gray-900">Frontend:</strong> React + TypeScript + Vite + TailwindCSS</li>
                  <li><strong className="text-gray-900">Backend:</strong> Python Flask with finite automata implementation</li>
                  <li><strong className="text-gray-900">Theory:</strong> Finite State Machines & Pattern Matching</li>
                  <li><strong className="text-gray-900">NLP Libraries:</strong> RapidFuzz (fuzzy matching with Levenshtein distance)</li>
                  <li><strong className="text-gray-900">Dictionaries:</strong> Custom Filipino/Taglish netspeak patterns + English word corpus (JSON-based)</li>
                </ul>
              </div>

              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Fuzzy Matching Algorithm
                </h3>
                <p className="text-gray-600 mb-4 leading-relaxed">
                  Our sophisticated multi-factor scoring system ensures accurate word matching:
                </p>
                <ul className="list-disc list-outside space-y-2 text-gray-600 ml-6">
                  <li><strong className="text-gray-900">Base Score:</strong> Levenshtein distance similarity</li>
                  <li><strong className="text-gray-900">Length Penalty:</strong> -5% per missing character (prevents truncated matches)</li>
                  <li><strong className="text-gray-900">Length Bonus:</strong> +4% per character after 3 (favors complete words)</li>
                  <li><strong className="text-gray-900">Prefix Matching:</strong> +3% per matching character in first 3 positions</li>
                  <li><strong className="text-gray-900">Exact Length Match:</strong> +2% bonus when lengths match perfectly</li>
                  <li><strong className="text-gray-900">Dynamic Thresholds:</strong> 75% for 4+ char words, 60% for 3-char words</li>
                </ul>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default Home;