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
                theory and natural language processing techniques.
              </p>
              
              <h3 className="text-2xl font-semibold text-indigo-800 mt-6 mb-3">
                Key Features
              </h3>
              <ul className="list-disc list-inside space-y-2 mb-4">
                <li>Real-time obfuscation detection using pattern recognition</li>
                <li>Automatic deciphering of leetspeak and character substitutions</li>
                <li>Duplication normalization (heeeey → hey)</li>
                <li>Character-level finite automata processing</li>
                <li>Fuzzy matching for intelligent word correction</li>
                <li>Support for common obfuscation patterns (3→e, 1→i, 0→o, etc.)</li>
              </ul>

              <h3 className="text-2xl font-semibold text-indigo-800 mt-6 mb-3">
                How It Works
              </h3>
              <ol className="list-decimal list-inside space-y-2 mb-4">
                <li><strong>Detection:</strong> Identifies 5 types of obfuscation patterns using NFAs</li>
                <li><strong>Transformation:</strong> Reverses leetspeak and normalizes character duplication</li>
                <li><strong>Dictionary Lookup:</strong> Checks against netspeak dictionary</li>
                <li><strong>Fuzzy Matching:</strong> Finds closest valid word for unrecognized tokens</li>
                <li><strong>Output:</strong> Returns original and deobfuscated text with confidence</li>
              </ol>

              <h3 className="text-2xl font-semibold text-indigo-800 mt-6 mb-3">
                Technology Stack
              </h3>
              <ul className="list-disc list-inside space-y-2">
                <li><strong>Frontend:</strong> React + TypeScript + Vite + TailwindCSS</li>
                <li><strong>Backend:</strong> Python Flask with finite automata implementation</li>
                <li><strong>Theory:</strong> Finite State Machines & Pattern Matching</li>
                <li><strong>NLP:</strong> Fuzzy string matching with RapidFuzz</li>
              </ul>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default Home;