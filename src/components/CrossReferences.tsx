import React, { useState } from 'react';
import { CrossReference } from '../types';
import { ExternalLink, ChevronDown, ChevronRight, Book } from 'lucide-react';

interface CrossReferencesProps {
  crossReferences: CrossReference[];
  onNavigateToReference: (volume: string, book: string, chapter: number, verse: number) => void;
}

const CrossReferences: React.FC<CrossReferencesProps> = ({
  crossReferences,
  onNavigateToReference
}) => {
  const [isExpanded, setIsExpanded] = useState(false);

  if (!crossReferences || crossReferences.length === 0) {
    return null;
  }

  const volumeColors = {
    ot: 'bg-purple-50 border-purple-200 text-purple-800',
    nt: 'bg-blue-50 border-blue-200 text-blue-800',
    bom: 'bg-green-50 border-green-200 text-green-800',
    dc: 'bg-yellow-50 border-yellow-200 text-yellow-800',
    pogp: 'bg-pink-50 border-pink-200 text-pink-800'
  };

  const volumeNames = {
    ot: 'Old Testament',
    nt: 'New Testament',
    bom: 'Book of Mormon',
    dc: 'Doctrine & Covenants',
    pogp: 'Pearl of Great Price'
  };

  return (
    <div className="mt-4 bg-gray-50 rounded-lg p-4 border border-gray-200">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="flex items-center space-x-2 text-sm font-medium text-gray-700 hover:text-gray-900 transition-colors"
      >
        {isExpanded ? (
          <ChevronDown className="w-4 h-4" />
        ) : (
          <ChevronRight className="w-4 h-4" />
        )}
        <Book className="w-4 h-4" />
        <span>Cross-References ({crossReferences.length})</span>
      </button>

      {isExpanded && (
        <div className="mt-3 space-y-3">
          {crossReferences.map((ref) => (
            <div
              key={ref.id}
              className={`border rounded-lg p-3 cursor-pointer hover:shadow-sm transition-shadow ${volumeColors[ref.volume]}`}
              onClick={() => onNavigateToReference(ref.volume, ref.book, ref.chapter, ref.verse)}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-2">
                    <span className="text-xs font-medium uppercase tracking-wide opacity-75">
                      {volumeNames[ref.volume]}
                    </span>
                    <ExternalLink className="w-3 h-3 opacity-60" />
                  </div>
                  <div className="font-medium text-sm mb-1">
                    {ref.label}
                  </div>
                  <p className="text-sm opacity-90 leading-relaxed">
                    {ref.text}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default CrossReferences;