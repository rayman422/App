import React, { useState, useEffect } from 'react';
import { AppState, UserNote, UserHighlight, Bookmark, ReadingProgress } from './types';
import { scriptureData } from './data/scriptureData';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import ScriptureReader from './components/ScriptureReader';
import SearchView from './components/SearchView';
import NotesView from './components/NotesView';
import BookmarksView from './components/BookmarksView';
import ProgressView from './components/ProgressView';
import ErrorBoundary from './components/ErrorBoundary';
import { ToastContainer, ToastData } from './components/Toast';
import HelpModal from './components/HelpModal';

const STORAGE_KEY = 'book-of-mormon-study-app';

function App() {
  const [appState, setAppState] = useState<AppState>({
    currentVolume: 'bom',
    currentBook: '1-nephi',
    currentChapter: 1,
    currentVerse: undefined,
    searchQuery: '',
    searchResults: [],
    userNotes: [],
    userHighlights: [],
    bookmarks: [],
    readingProgress: [],
    studySessions: [],
    readingPlans: [],
    activeReadingPlan: undefined,
    sidebarOpen: true,
    activeView: 'read',
    showCrossReferences: true,
    fontSize: 'medium',
    theme: 'light'
  });

  const [toasts, setToasts] = useState<ToastData[]>([]);
  const [showHelp, setShowHelp] = useState(false);

  // Load data from localStorage on mount
  useEffect(() => {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) {
      try {
        const parsedData = JSON.parse(saved);
        setAppState(prev => ({ ...prev, ...parsedData }));
      } catch (error) {
        console.error('Error loading saved data:', error);
      }
    }
  }, []);

  // Save data to localStorage whenever state changes
  useEffect(() => {
    const dataToSave = {
      userNotes: appState.userNotes,
      userHighlights: appState.userHighlights,
      bookmarks: appState.bookmarks,
      readingProgress: appState.readingProgress,
      studySessions: appState.studySessions,
      currentBook: appState.currentBook,
      currentChapter: appState.currentChapter,
      currentVerse: appState.currentVerse
    };
    localStorage.setItem(STORAGE_KEY, JSON.stringify(dataToSave));
  }, [appState]);

  const updateAppState = (updates: Partial<AppState>) => {
    setAppState(prev => ({ ...prev, ...updates }));
  };

  const addToast = (toast: Omit<ToastData, 'id'>) => {
    const newToast: ToastData = {
      ...toast,
      id: Date.now().toString()
    };
    setToasts(prev => [...prev, newToast]);
  };

  const removeToast = (id: string) => {
    setToasts(prev => prev.filter(toast => toast.id !== id));
  };

  const addNote = (verseId: string, text: string, color: string = 'yellow') => {
    const newNote: UserNote = {
      id: Date.now().toString(),
      verseId,
      text,
      color,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };
    updateAppState({ userNotes: [...appState.userNotes, newNote] });
  };

  const updateNote = (noteId: string, text: string) => {
    const updatedNotes = appState.userNotes.map(note => 
      note.id === noteId 
        ? { ...note, text, updatedAt: new Date().toISOString() }
        : note
    );
    updateAppState({ userNotes: updatedNotes });
  };

  const deleteNote = (noteId: string) => {
    const filteredNotes = appState.userNotes.filter(note => note.id !== noteId);
    updateAppState({ userNotes: filteredNotes });
  };

  const addHighlight = (verseId: string, color: string = 'yellow') => {
    const newHighlight: UserHighlight = {
      id: Date.now().toString(),
      verseId,
      color,
      createdAt: new Date().toISOString()
    };
    updateAppState({ userHighlights: [...appState.userHighlights, newHighlight] });
  };

  const removeHighlight = (highlightId: string) => {
    const filteredHighlights = appState.userHighlights.filter(h => h.id !== highlightId);
    updateAppState({ userHighlights: filteredHighlights });
  };

  const addBookmark = (verseId: string, title: string) => {
    const newBookmark: Bookmark = {
      id: Date.now().toString(),
      verseId,
      title,
      createdAt: new Date().toISOString()
    };
    updateAppState({ bookmarks: [...appState.bookmarks, newBookmark] });
  };

  const removeBookmark = (bookmarkId: string) => {
    const filteredBookmarks = appState.bookmarks.filter(b => b.id !== bookmarkId);
    updateAppState({ bookmarks: filteredBookmarks });
  };

  const updateReadingProgress = (bookId: string, chapterId: string, verseId: string) => {
    const existingProgress = appState.readingProgress.find(p => p.bookId === bookId);
    const newProgress: ReadingProgress = {
      bookId,
      chapterId,
      verseId,
      lastRead: new Date().toISOString(),
      completed: false
    };

    if (existingProgress) {
      const updatedProgress = appState.readingProgress.map(p => 
        p.bookId === bookId ? newProgress : p
      );
      updateAppState({ readingProgress: updatedProgress });
    } else {
      updateAppState({ readingProgress: [...appState.readingProgress, newProgress] });
    }
  };

  const navigateToVerse = (volumeId: string, bookId: string, chapter: number, verse?: number) => {
    updateAppState({
      currentVolume: volumeId,
      currentBook: bookId,
      currentChapter: chapter,
      currentVerse: verse,
      activeView: 'read'
    });
  };

  const navigateToReference = (volume: string, book: string, chapter: number, verse: number) => {
    // Map volume abbreviations to volume IDs
    const volumeMap: { [key: string]: string } = {
      'ot': 'ot',
      'nt': 'nt',
      'bom': 'bom',
      'dc': 'dc',
      'pogp': 'pogp'
    };
    
    const volumeId = volumeMap[volume] || volume;
    const bookId = book.toLowerCase().replace(/\s+/g, '-').replace(/&/g, '');
    
    navigateToVerse(volumeId, bookId, chapter, verse);
    
    addToast({
      type: 'info',
      title: 'Cross-reference opened',
      message: `Navigated to ${book} ${chapter}:${verse}`,
      duration: 2000
    });
  };

  const renderMainContent = () => {
    switch (appState.activeView) {
      case 'search':
        return (
          <SearchView
            searchQuery={appState.searchQuery}
            searchResults={appState.searchResults}
            onSearchQueryChange={(query) => updateAppState({ searchQuery: query })}
            onSearchResultsChange={(results) => updateAppState({ searchResults: results })}
            onNavigateToVerse={(bookId, chapter, verse) => navigateToVerse(appState.currentVolume, bookId, chapter, verse)}
            scriptureData={scriptureData}
          />
        );
              case 'notes':
          return (
            <NotesView
              notes={appState.userNotes}
              onNavigateToVerse={(bookId, chapter, verse) => navigateToVerse(appState.currentVolume, bookId, chapter, verse)}
              onUpdateNote={updateNote}
              onDeleteNote={deleteNote}
              scriptureData={scriptureData}
            />
          );
        case 'bookmarks':
          return (
            <BookmarksView
              bookmarks={appState.bookmarks}
              onNavigateToVerse={(bookId, chapter, verse) => navigateToVerse(appState.currentVolume, bookId, chapter, verse)}
              onRemoveBookmark={removeBookmark}
              scriptureData={scriptureData}
            />
          );
        case 'progress':
          return (
            <ProgressView
              readingProgress={appState.readingProgress}
              studySessions={appState.studySessions}
              scriptureData={scriptureData}
            />
          );
              default:
          return (
            <ScriptureReader
              scriptureData={scriptureData}
              currentVolume={appState.currentVolume}
              currentBook={appState.currentBook}
              currentChapter={appState.currentChapter}
              currentVerse={appState.currentVerse}
              userNotes={appState.userNotes}
              userHighlights={appState.userHighlights}
              showCrossReferences={appState.showCrossReferences}
              onNavigateToVerse={(volumeId, bookId, chapter, verse) => navigateToVerse(volumeId, bookId, chapter, verse)}
              onNavigateToReference={navigateToReference}
              onAddNote={addNote}
              onAddHighlight={addHighlight}
              onRemoveHighlight={removeHighlight}
              onAddBookmark={addBookmark}
              onUpdateReadingProgress={updateReadingProgress}
              onAddToast={addToast}
            />
          );
    }
  };

  return (
    <ErrorBoundary>
      <div className="h-screen flex flex-col">
        <Header
          activeView={appState.activeView}
          onViewChange={(view) => updateAppState({ activeView: view })}
          onToggleSidebar={() => updateAppState({ sidebarOpen: !appState.sidebarOpen })}
          sidebarOpen={appState.sidebarOpen}
          onShowHelp={() => setShowHelp(true)}
        />
        
        <div className="flex flex-1 overflow-hidden">
          {appState.sidebarOpen && (
            <Sidebar
              scriptureData={scriptureData}
              currentVolume={appState.currentVolume}
              currentBook={appState.currentBook}
              currentChapter={appState.currentChapter}
              onNavigateToVerse={(volumeId, bookId, chapter, verse) => navigateToVerse(volumeId, bookId, chapter, verse)}
              activeView={appState.activeView}
              readingProgress={appState.readingProgress}
            />
          )}
          
          <main className="flex-1 overflow-auto">
            {renderMainContent()}
          </main>
        </div>
        
        <ToastContainer
          toasts={toasts}
          onRemoveToast={removeToast}
        />

        <HelpModal
          isOpen={showHelp}
          onClose={() => setShowHelp(false)}
        />
      </div>
    </ErrorBoundary>
  );
}

export default App;