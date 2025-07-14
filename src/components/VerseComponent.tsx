import React from 'react';
import { Verse, UserNote, UserHighlight } from '../types';
import { MessageSquare } from 'lucide-react';

interface VerseComponentProps {
  verse: Verse;
  isSelected: boolean;
  onClick: () => void;
  userNotes: UserNote[];
  userHighlights: UserHighlight[];
}

const VerseComponent: React.FC<VerseComponentProps> = ({
  verse,
  isSelected,
  onClick,
  userNotes,
  userHighlights
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
                      <p className="text-xs text-blue-600 mt-1">
                        {new Date(note.createdAt).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
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
        </div>
      </div>
    </div>
  );
};

export default VerseComponent;