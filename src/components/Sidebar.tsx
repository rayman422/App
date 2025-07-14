import React from 'react';
import { Scripture, ReadingProgress } from '../types';
import { ChevronRight, ChevronDown, CheckCircle } from 'lucide-react';

interface SidebarProps {
  bookOfMormon: Scripture;
  currentBook: string;
  currentChapter: number;
  onNavigateToVerse: (bookId: string, chapter: number, verse?: number) => void;
  activeView: string;
  readingProgress: ReadingProgress[];
}

const Sidebar: React.FC<SidebarProps> = ({
  bookOfMormon,
  currentBook,
  currentChapter,
  onNavigateToVerse,
  readingProgress
}) => {
  const [expandedBooks, setExpandedBooks] = React.useState<Set<string>>(new Set([currentBook]));

  const toggleBookExpansion = (bookId: string) => {
    const newExpanded = new Set(expandedBooks);
    if (newExpanded.has(bookId)) {
      newExpanded.delete(bookId);
    } else {
      newExpanded.add(bookId);
    }
    setExpandedBooks(newExpanded);
  };

  const isChapterRead = (bookId: string, chapterNum: number) => {
    return readingProgress.some(p => p.bookId === bookId && p.completed);
  };

  return (
    <aside className="sidebar w-80 p-4 overflow-y-auto">
      <div className="space-y-2">
        <h2 className="font-bold text-lg text-gray-900 mb-4">Contents</h2>
        
        {bookOfMormon.books.map((book) => (
          <div key={book.id} className="border border-gray-200 rounded-lg overflow-hidden">
            <button
              onClick={() => toggleBookExpansion(book.id)}
              className={`
                w-full px-3 py-2 text-left flex items-center justify-between
                hover:bg-gray-50 transition-colors
                ${currentBook === book.id ? 'bg-primary-50 text-primary-700' : 'text-gray-700'}
              `}
            >
              <span className="font-medium">{book.name}</span>
              {expandedBooks.has(book.id) ? (
                <ChevronDown className="w-4 h-4" />
              ) : (
                <ChevronRight className="w-4 h-4" />
              )}
            </button>
            
            {expandedBooks.has(book.id) && (
              <div className="border-t border-gray-200 bg-gray-50">
                {book.chapters.map((chapter) => (
                  <button
                    key={chapter.id}
                    onClick={() => onNavigateToVerse(book.id, chapter.chapter)}
                    className={`
                      w-full px-6 py-2 text-left text-sm flex items-center justify-between
                      hover:bg-gray-100 transition-colors
                      ${currentBook === book.id && currentChapter === chapter.chapter
                        ? 'bg-primary-100 text-primary-700 font-medium'
                        : 'text-gray-600'
                      }
                    `}
                  >
                    <span>Chapter {chapter.chapter}</span>
                    {isChapterRead(book.id, chapter.chapter) && (
                      <CheckCircle className="w-4 h-4 text-green-500" />
                    )}
                  </button>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
    </aside>
  );
};

export default Sidebar;