interface LanguageChartProps {
  distribution: {
    tagalog: number;
    english: number;
  };
}

export default function LanguageChart({ distribution }: LanguageChartProps) {
  const total = distribution.tagalog + distribution.english;
  const tagalogPercentage = total > 0 ? Math.round((distribution.tagalog / total) * 100) : 0;
  const englishPercentage = total > 0 ? Math.round((distribution.english / total) * 100) : 0;

  return (
    <div className="max-w-5xl mx-auto bg-white rounded-2xl shadow-xl p-8 mb-6">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">Language Distribution</h2>
      
      <div className="space-y-6">
        {/* Tagalog */}
        <div>
          <div className="flex justify-between items-center mb-2">
            <span className="text-lg font-medium text-gray-700">Tagalog</span>
            <span className="text-lg font-semibold text-gray-900">{distribution.tagalog} words</span>
          </div>
          <div className="w-full h-8 bg-gray-200 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-purple-500 to-purple-600 transition-all duration-500 ease-out flex items-center justify-end pr-3"
              style={{ width: `${tagalogPercentage}%` }}
            >
              {tagalogPercentage > 10 && (
                <span className="text-white text-sm font-semibold">{tagalogPercentage}%</span>
              )}
            </div>
          </div>
        </div>

        {/* English */}
        <div>
          <div className="flex justify-between items-center mb-2">
            <span className="text-lg font-medium text-gray-700">English</span>
            <span className="text-lg font-semibold text-gray-900">{distribution.english} words</span>
          </div>
          <div className="w-full h-8 bg-gray-200 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-green-500 to-green-600 transition-all duration-500 ease-out flex items-center justify-end pr-3"
              style={{ width: `${englishPercentage}%` }}
            >
              {englishPercentage > 10 && (
                <span className="text-white text-sm font-semibold">{englishPercentage}%</span>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
