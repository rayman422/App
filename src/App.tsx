import React, { useState, useEffect } from 'react';
import { AppState, UserNote, UserHighlight, Bookmark, ReadingProgress, SearchResult } from './types';
import { bookOfMormon } from './data/bookOfMormon';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import ScriptureReader from './components/ScriptureReader';
import SearchView from './components/SearchView';
import NotesView from './components/NotesView';
import BookmarksView from './components/BookmarksView';
import ProgressView from './components/ProgressView';

const STORAGE_KEY = 'book-of-mormon-study-app';

function App() {
  const [appState, setAppState] = useState<AppState>({
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
    sidebarOpen: true,
    activeView: 'read'
  });

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

  const navigateToVerse = (bookId: string, chapter: number, verse?: number) => {
    updateAppState({
      currentBook: bookId,
      currentChapter: chapter,
      currentVerse: verse,
      activeView: 'read'
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
            onNavigateToVerse={navigateToVerse}
            bookOfMormon={bookOfMormon}
          />
        );
      case 'notes':
        return (
          <NotesView
            notes={appState.userNotes}
            onNavigateToVerse={navigateToVerse}
            onUpdateNote={updateNote}
            onDeleteNote={deleteNote}
            bookOfMormon={bookOfMormon}
          />
        );
      case 'bookmarks':
        return (
          <BookmarksView
            bookmarks={appState.bookmarks}
            onNavigateToVerse={navigateToVerse}
            onRemoveBookmark={removeBookmark}
            bookOfMormon={bookOfMormon}
          />
        );
      case 'progress':
        return (
          <ProgressView
            readingProgress={appState.readingProgress}
            studySessions={appState.studySessions}
            bookOfMormon={bookOfMormon}
          />
        );
      default:
        return (
          <ScriptureReader
            bookOfMormon={bookOfMormon}
            currentBook={appState.currentBook}
            currentChapter={appState.currentChapter}
            currentVerse={appState.currentVerse}
            userNotes={appState.userNotes}
            userHighlights={appState.userHighlights}
            onNavigateToVerse={navigateToVerse}
            onAddNote={addNote}
            onAddHighlight={addHighlight}
            onAddBookmark={addBookmark}
            onUpdateReadingProgress={updateReadingProgress}
          />
        );
    }
  };

  return (
    <div className="h-screen flex flex-col">
      <Header
        activeView={appState.activeView}
        onViewChange={(view) => updateAppState({ activeView: view })}
        onToggleSidebar={() => updateAppState({ sidebarOpen: !appState.sidebarOpen })}
        sidebarOpen={appState.sidebarOpen}
      />
      
      <div className="flex flex-1 overflow-hidden">
        {appState.sidebarOpen && (
          <Sidebar
            bookOfMormon={bookOfMormon}
            currentBook={appState.currentBook}
            currentChapter={appState.currentChapter}
            onNavigateToVerse={navigateToVerse}
            activeView={appState.activeView}
            readingProgress={appState.readingProgress}
          />
        )}
        
        <main className="flex-1 overflow-auto">
          {renderMainContent()}
        </main>
      </div>
    </div>
  );
}

export default App;