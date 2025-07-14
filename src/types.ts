export interface Verse {
  id: string;
  book: string;
  chapter: number;
  verse: number;
  text: string;
}

export interface Chapter {
  id: string;
  book: string;
  chapter: number;
  title: string;
  verses: Verse[];
}

export interface Book {
  id: string;
  name: string;
  fullName: string;
  chapters: Chapter[];
}

export interface Scripture {
  books: Book[];
}

export interface UserNote {
  id: string;
  verseId: string;
  text: string;
  color: string;
  createdAt: string;
  updatedAt: string;
}

export interface UserHighlight {
  id: string;
  verseId: string;
  color: string;
  createdAt: string;
}

export interface Bookmark {
  id: string;
  verseId: string;
  title: string;
  createdAt: string;
}

export interface ReadingProgress {
  bookId: string;
  chapterId: string;
  verseId: string;
  lastRead: string;
  completed: boolean;
}

export interface SearchResult {
  verse: Verse;
  matchText: string;
  context: string;
}

export interface StudySession {
  date: string;
  chaptersRead: string[];
  notesAdded: number;
  timeSpent: number; // in minutes
}

export interface AppState {
  currentBook: string;
  currentChapter: number;
  currentVerse?: number;
  searchQuery: string;
  searchResults: SearchResult[];
  userNotes: UserNote[];
  userHighlights: UserHighlight[];
  bookmarks: Bookmark[];
  readingProgress: ReadingProgress[];
  studySessions: StudySession[];
  sidebarOpen: boolean;
  activeView: 'read' | 'search' | 'notes' | 'bookmarks' | 'progress';
}