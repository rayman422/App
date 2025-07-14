import React from 'react';
import { Bookmark as BookmarkType, Scripture } from '../types';
import { Bookmark, ExternalLink, Trash2, Calendar } from 'lucide-react';

interface BookmarksViewProps {
  bookmarks: BookmarkType[];
  onNavigateToVerse: (bookId: string, chapter: number, verse?: number) => void;
  onRemoveBookmark: (bookmarkId: string) => void;
  scriptureData: Scripture;
}

const BookmarksView: React.FC<BookmarksViewProps> = ({
  bookmarks,
  onNavigateToVerse,
  onRemoveBookmark,
  scriptureData
}) => {
  const getVerseInfo = (verseId: string) => {
    for (const volume of scriptureData.volumes) {
      for (const book of volume.books) {
        for (const chapter of book.chapters) {
          const verse = chapter.verses.find(v => v.id === verseId);
          if (verse) {
            return {
              reference: `${verse.book} ${verse.chapter}:${verse.verse}`,
              text: verse.text,
              bookId: book.id,
              chapter: verse.chapter,
              verse: verse.verse
            };
          }
        }
      }
    }
    return null;
  };

  const handleRemoveBookmark = (bookmarkId: string) => {
    if (window.confirm('Are you sure you want to remove this bookmark?')) {
      onRemoveBookmark(bookmarkId);
    }
  };

  const sortedBookmarks = bookmarks.sort((a, b) => 
    new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
  );

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">My Bookmarks</h1>
        <p className="text-gray-600">
          Quick access to your saved verses and favorite passages.
        </p>
      </div>

      {sortedBookmarks.length === 0 ? (
        <div className="text-center py-12">
          <Bookmark className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No bookmarks yet</h3>
          <p className="text-gray-600">
            Click on any verse while reading to add it to your bookmarks!
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          <div className="text-sm text-gray-500 mb-4">
            {sortedBookmarks.length} bookmark{sortedBookmarks.length !== 1 ? 's' : ''}
          </div>
          
          {sortedBookmarks.map((bookmark) => {
            const verseInfo = getVerseInfo(bookmark.verseId);
            if (!verseInfo) return null;

            return (
              <div
                key={bookmark.id}
                className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm hover:shadow-md transition-shadow"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <Bookmark className="w-5 h-5 text-yellow-500 fill-current" />
                    <h3 className="font-medium text-gray-900">{bookmark.title}</h3>
                  </div>
                  
                  <button
                    onClick={() => handleRemoveBookmark(bookmark.id)}
                    className="p-2 text-gray-400 hover:text-red-600 rounded-md hover:bg-gray-100"
                    title="Remove bookmark"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>

                <div className="bg-scripture-50 border-l-4 border-scripture-400 p-4 mb-4">
                  <p className="text-gray-800 leading-relaxed font-scripture">
                    {verseInfo.text}
                  </p>
                </div>

                <div className="flex items-center justify-between">
                  <button
                    onClick={() => onNavigateToVerse(verseInfo.bookId, verseInfo.chapter, verseInfo.verse)}
                    className="flex items-center space-x-2 text-primary-600 hover:text-primary-700 font-medium"
                  >
                    <span>Go to {verseInfo.reference}</span>
                    <ExternalLink className="w-4 h-4" />
                  </button>
                  
                  <div className="flex items-center space-x-1 text-xs text-gray-500">
                    <Calendar className="w-3 h-3" />
                    <span>Added {new Date(bookmark.createdAt).toLocaleDateString()}</span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default BookmarksView;