import React from 'react';
import { Verse, UserNote, UserHighlight } from '../types';
import { MessageSquare, BookOpen, Tag } from 'lucide-react';
import CrossReferences from './CrossReferences';

interface VerseComponentProps {
  verse: Verse;
  isSelected: boolean;
  onClick: () => void;
  userNotes: UserNote[];
  userHighlights: UserHighlight[];
  showCrossReferences?: boolean;
  onNavigateToReference?: (volume: string, book: string, chapter: number, verse: number) => void;
}

const VerseComponent: React.FC<VerseComponentProps> = ({
  verse,
  isSelected,
  onClick,
  userNotes,
  userHighlights,
  showCrossReferences = true,
  onNavigateToReference
}) => {
  const hasHighlight = userHighlights.length > 0;
  const hasNotes = userNotes.length > 0;

  const getHighlightStyle = () => {
    if (!hasHighlight) return '';
    const highlight = userHighlights[0]; // Use the first highlight for now
    switch (highlight.color) {
      case 'yellow':
        return 'bg-yellow-100 border-l-4 border-yellow-400';
      case 'blue':
        return 'bg-blue-100 border-l-4 border-blue-400';
      case 'green':
        return 'bg-green-100 border-l-4 border-green-400';
      case 'pink':
        return 'bg-pink-100 border-l-4 border-pink-400';
      default:
        return 'bg-gray-100 border-l-4 border-gray-400';
    }
  };

  return (
    <div
      className={`
        verse-container p-3 rounded-lg cursor-pointer transition-all duration-200
        ${isSelected ? 'ring-2 ring-primary-500 bg-primary-50' : 'hover:bg-gray-50'}
        ${hasHighlight ? getHighlightStyle() : ''}
      `}
      onClick={onClick}
    >
      <div className="flex items-start space-x-3">
        <span className="verse-number">{verse.verse}</span>
        <div className="flex-1">
          <p className="verse-text">{verse.text}</p>
          
          {/* Display notes */}
          {hasNotes && (
            <div className="mt-3 space-y-2">
              {userNotes.map((note) => (
                <div
                  key={note.id}
                  className="bg-blue-50 border border-blue-200 rounded-md p-3"
                >
                  <div className="flex items-start space-x-2">
                    <MessageSquare className="w-4 h-4 text-blue-600 mt-0.5 flex-shrink-0" />
                    <div className="flex-1">
                      <p className="text-sm text-blue-800">{note.text}</p>
                      <div className="flex items-center justify-between mt-2">
                        <p className="text-xs text-blue-600">
                          {new Date(note.createdAt).toLocaleDateString()}
                        </p>
                        {note.tags && note.tags.length > 0 && (
                          <div className="flex items-center space-x-1">
                            <Tag className="w-3 h-3 text-blue-500" />
                            <span className="text-xs text-blue-600">
                              {note.tags.join(', ')}
                            </span>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Display topical guide entries */}
          {verse.topicalGuideEntries && verse.topicalGuideEntries.length > 0 && (
            <div className="mt-3">
              <div className="flex items-center space-x-2 mb-2">
                <BookOpen className="w-4 h-4 text-gray-600" />
                <span className="text-sm font-medium text-gray-700">Topical Guide:</span>
              </div>
              <div className="flex flex-wrap gap-1">
                {verse.topicalGuideEntries.map((entry, index) => (
                  <span
                    key={index}
                    className="inline-block bg-gray-100 text-gray-700 text-xs px-2 py-1 rounded-full"
                  >
                    {entry}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Display cross-references */}
          {showCrossReferences && verse.crossReferences && onNavigateToReference && (
            <CrossReferences
              crossReferences={verse.crossReferences}
              onNavigateToReference={onNavigateToReference}
            />
          )}
        </div>
        
        {/* Indicators */}
        <div className="flex flex-col space-y-1">
          {hasNotes && (
            <div className="w-2 h-2 bg-blue-500 rounded-full" title="Has notes" />
          )}
          {hasHighlight && (
            <div className="w-2 h-2 bg-yellow-500 rounded-full" title="Highlighted" />
          )}
          {verse.crossReferences && verse.crossReferences.length > 0 && (
            <div className="w-2 h-2 bg-green-500 rounded-full" title="Has cross-references" />
          )}
          {verse.topicalGuideEntries && verse.topicalGuideEntries.length > 0 && (
            <div className="w-2 h-2 bg-purple-500 rounded-full" title="Topical Guide entries" />
          )}
        </div>
      </div>
    </div>
  );
};

export default VerseComponent;