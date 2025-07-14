import React, { useState, useEffect, useCallback } from 'react';
import { Scripture, UserNote, UserHighlight, Verse } from '../types';
import { ChevronLeft, ChevronRight, Highlighter, Bookmark, MessageSquare } from 'lucide-react';
import VerseComponent from './VerseComponent';

interface ScriptureReaderProps {
  scriptureData: Scripture;
  currentVolume: string;
  currentBook: string;
  currentChapter: number;
  currentVerse?: number;
  userNotes: UserNote[];
  userHighlights: UserHighlight[];
  showCrossReferences?: boolean;
  onNavigateToVerse: (volumeId: string, bookId: string, chapter: number, verse?: number) => void;
  onNavigateToReference?: (volume: string, book: string, chapter: number, verse: number) => void;
  onAddNote: (verseId: string, text: string, color?: string) => void;
  onAddHighlight: (verseId: string, color?: string) => void;
  onRemoveHighlight: (highlightId: string) => void;
  onAddBookmark: (verseId: string, title: string) => void;
  onUpdateReadingProgress: (bookId: string, chapterId: string, verseId: string) => void;
  onAddToast?: (toast: any) => void;
}

const ScriptureReader: React.FC<ScriptureReaderProps> = ({
  scriptureData,
  currentVolume,
  currentBook,
  currentChapter,
  currentVerse,
  userNotes,
  userHighlights,
  showCrossReferences = true,
  onNavigateToVerse,
  onNavigateToReference,
  onAddNote,
  onAddHighlight,
  onRemoveHighlight,
  onAddBookmark,
  onUpdateReadingProgress,
  onAddToast
}) => {
  const [selectedVerse, setSelectedVerse] = useState<string | null>(null);
  const [showNoteDialog, setShowNoteDialog] = useState(false);
  const [noteText, setNoteText] = useState('');

  const currentVolumeData = scriptureData.volumes.find(volume => volume.id === currentVolume);
  const currentBookData = currentVolumeData?.books.find(book => book.id === currentBook);
  const currentChapterData = currentBookData?.chapters.find(chapter => chapter.chapter === currentChapter);

  const canGoPrevious = useCallback(() => {
    if (!currentBookData || !currentVolumeData) return false;
    if (currentChapter > 1) return true;
    const currentBookIndex = currentVolumeData.books.findIndex(book => book.id === currentBook);
    return currentBookIndex > 0;
  }, [currentBookData, currentVolumeData, currentChapter, currentBook]);

  const canGoNext = useCallback(() => {
    if (!currentBookData || !currentVolumeData) return false;
    if (currentChapter < currentBookData.chapters.length) return true;
    const currentBookIndex = currentVolumeData.books.findIndex(book => book.id === currentBook);
    return currentBookIndex < currentVolumeData.books.length - 1;
  }, [currentBookData, currentVolumeData, currentChapter, currentBook]);

  const goToPrevious = useCallback(() => {
    if (!currentBookData || !currentVolumeData) return;
    
    if (currentChapter > 1) {
      onNavigateToVerse(currentVolume, currentBook, currentChapter - 1);
    } else {
      const currentBookIndex = currentVolumeData.books.findIndex(book => book.id === currentBook);
      if (currentBookIndex > 0) {
        const prevBook = currentVolumeData.books[currentBookIndex - 1];
        const lastChapter = prevBook.chapters[prevBook.chapters.length - 1];
        onNavigateToVerse(currentVolume, prevBook.id, lastChapter.chapter);
      }
    }
  }, [currentBookData, currentVolumeData, currentChapter, currentVolume, currentBook, onNavigateToVerse]);

  const goToNext = useCallback(() => {
    if (!currentBookData || !currentVolumeData) return;
    
    if (currentChapter < currentBookData.chapters.length) {
      onNavigateToVerse(currentVolume, currentBook, currentChapter + 1);
    } else {
      const currentBookIndex = currentVolumeData.books.findIndex(book => book.id === currentBook);
      if (currentBookIndex < currentVolumeData.books.length - 1) {
        const nextBook = currentVolumeData.books[currentBookIndex + 1];
        onNavigateToVerse(currentVolume, nextBook.id, 1);
      }
    }
  }, [currentBookData, currentVolumeData, currentChapter, currentVolume, currentBook, onNavigateToVerse]);

  const handleVerseClick = (verse: Verse) => {
    setSelectedVerse(verse.id === selectedVerse ? null : verse.id);
    onUpdateReadingProgress(currentBook, currentChapterData?.id || '', verse.id);
  };

  const handleAddNote = () => {
    if (selectedVerse && noteText.trim()) {
      onAddNote(selectedVerse, noteText.trim());
      setNoteText('');
      setShowNoteDialog(false);
      setSelectedVerse(null);
      
      if (onAddToast) {
        onAddToast({
          type: 'success',
          title: 'Note added',
          message: 'Your study note has been saved.',
          duration: 2000
        });
      }
    }
  };

  const handleAddHighlight = (color: string = 'yellow') => {
    if (selectedVerse) {
      onAddHighlight(selectedVerse, color);
      setSelectedVerse(null);
      
      if (onAddToast) {
        onAddToast({
          type: 'success',
          title: 'Verse highlighted',
          message: `Added ${color} highlight to verse.`,
          duration: 2000
        });
      }
    }
  };

  const handleAddBookmark = () => {
    if (selectedVerse && currentChapterData) {
      const verse = currentChapterData.verses.find(v => v.id === selectedVerse);
      if (verse) {
        const title = `${currentBookData?.name} ${currentChapter}:${verse.verse}`;
        onAddBookmark(selectedVerse, title);
        setSelectedVerse(null);
        
        if (onAddToast) {
          onAddToast({
            type: 'success',
            title: 'Bookmark added',
            message: `Bookmarked ${title}`,
            duration: 2000
          });
        }
      }
    }
  };

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyPress = (e: KeyboardEvent) => {
      // Don't trigger shortcuts when typing in input fields
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) {
        return;
      }

      switch (e.key) {
        case 'ArrowLeft':
          if (canGoPrevious()) {
            e.preventDefault();
            goToPrevious();
          }
          break;
        case 'ArrowRight':
          if (canGoNext()) {
            e.preventDefault();
            goToNext();
          }
          break;
        case 'Escape':
          if (selectedVerse) {
            e.preventDefault();
            setSelectedVerse(null);
            setShowNoteDialog(false);
            setNoteText('');
          }
          break;
      }
    };

    document.addEventListener('keydown', handleKeyPress);
    return () => document.removeEventListener('keydown', handleKeyPress);
  }, [canGoPrevious, canGoNext, goToPrevious, goToNext, selectedVerse]);

  if (!currentBookData || !currentChapterData) {
    return (
      <div className="flex items-center justify-center h-full">
        <p className="text-gray-500">Chapter not found</p>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      {/* Keyboard shortcuts help */}
      <div className="text-center mb-4">
        <p className="text-xs text-gray-500">
          Use ← → arrow keys to navigate chapters • ESC to clear selection • Click verses to interact
        </p>
      </div>

      {/* Navigation Header */}
      <div className="flex items-center justify-between mb-6">
        <button
          onClick={goToPrevious}
          disabled={!canGoPrevious()}
          className="btn-secondary disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
        >
          <ChevronLeft className="w-4 h-4" />
          <span>Previous</span>
        </button>

                  <div className="text-center">
            <h1 className="book-title">{currentBookData.fullName}</h1>
            <h2 className="chapter-heading">Chapter {currentChapter}</h2>
            {currentChapterData.title && (
              <p className="text-gray-600 italic">{currentChapterData.title}</p>
            )}
            {currentChapterData.summary && (
              <p className="text-sm text-gray-500 mt-2 max-w-2xl mx-auto">{currentChapterData.summary}</p>
            )}
          </div>

        <button
          onClick={goToNext}
          disabled={!canGoNext()}
          className="btn-secondary disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
        >
          <span>Next</span>
          <ChevronRight className="w-4 h-4" />
        </button>
      </div>

      {/* Scripture Text */}
      <div className="space-y-4">
        {currentChapterData.verses.map((verse) => (
          <VerseComponent
            key={verse.id}
            verse={verse}
            isSelected={selectedVerse === verse.id}
            onClick={() => handleVerseClick(verse)}
            userNotes={userNotes.filter(note => note.verseId === verse.id)}
            userHighlights={userHighlights.filter(highlight => highlight.verseId === verse.id)}
            showCrossReferences={showCrossReferences}
            onNavigateToReference={onNavigateToReference}
            onRemoveHighlight={onRemoveHighlight}
          />
        ))}
      </div>

      {/* Verse Action Panel */}
      {selectedVerse && (
        <div className="fixed bottom-4 left-1/2 transform -translate-x-1/2 bg-white shadow-lg border border-gray-200 rounded-lg p-4 flex items-center space-x-3">
          <button
            onClick={() => setShowNoteDialog(true)}
            className="flex items-center space-x-2 px-3 py-2 bg-blue-100 text-blue-700 rounded-md hover:bg-blue-200 transition-colors"
          >
            <MessageSquare className="w-4 h-4" />
            <span>Add Note</span>
          </button>

          <div className="relative group">
            <button
              onClick={() => handleAddHighlight('yellow')}
              className="flex items-center space-x-2 px-3 py-2 bg-yellow-100 text-yellow-700 rounded-md hover:bg-yellow-200 transition-colors"
            >
              <Highlighter className="w-4 h-4" />
              <span>Highlight</span>
            </button>
            <div className="absolute top-full left-0 mt-1 bg-white shadow-lg border border-gray-200 rounded-md p-2 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-10">
              <div className="flex space-x-1">
                <button
                  onClick={() => handleAddHighlight('yellow')}
                  className="w-6 h-6 bg-yellow-200 rounded border-2 border-yellow-400 hover:scale-110 transition-transform"
                  title="Yellow highlight"
                />
                <button
                  onClick={() => handleAddHighlight('blue')}
                  className="w-6 h-6 bg-blue-200 rounded border-2 border-blue-400 hover:scale-110 transition-transform"
                  title="Blue highlight"
                />
                <button
                  onClick={() => handleAddHighlight('green')}
                  className="w-6 h-6 bg-green-200 rounded border-2 border-green-400 hover:scale-110 transition-transform"
                  title="Green highlight"
                />
                <button
                  onClick={() => handleAddHighlight('pink')}
                  className="w-6 h-6 bg-pink-200 rounded border-2 border-pink-400 hover:scale-110 transition-transform"
                  title="Pink highlight"
                />
              </div>
            </div>
          </div>

          <button
            onClick={handleAddBookmark}
            className="flex items-center space-x-2 px-3 py-2 bg-green-100 text-green-700 rounded-md hover:bg-green-200 transition-colors"
          >
            <Bookmark className="w-4 h-4" />
            <span>Bookmark</span>
          </button>

          <button
            onClick={() => setSelectedVerse(null)}
            className="px-3 py-2 text-gray-500 hover:text-gray-700 transition-colors"
          >
            Cancel
          </button>
        </div>
      )}

      {/* Note Dialog */}
      {showNoteDialog && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full">
            <h3 className="text-lg font-medium mb-4">Add Note</h3>
            <textarea
              value={noteText}
              onChange={(e) => setNoteText(e.target.value)}
              placeholder="Enter your note..."
              className="w-full h-32 p-3 border border-gray-300 rounded-md resize-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              autoFocus
            />
            <div className="flex space-x-3 mt-4">
              <button
                onClick={handleAddNote}
                className="btn-primary flex-1"
                disabled={!noteText.trim()}
              >
                Save Note
              </button>
              <button
                onClick={() => {
                  setShowNoteDialog(false);
                  setNoteText('');
                }}
                className="btn-secondary flex-1"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ScriptureReader;