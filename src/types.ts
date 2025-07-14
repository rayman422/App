export interface CrossReference {
  id: string;
  volume: 'ot' | 'nt' | 'bom' | 'dc' | 'pogp'; // Old Testament, New Testament, Book of Mormon, Doctrine & Covenants, Pearl of Great Price
  book: string;
  chapter: number;
  verse: number;
  text: string;
  label: string; // e.g., "1 Ne. 3:7", "D&C 82:10"
}

export interface Verse {
  id: string;
  book: string;
  chapter: number;
  verse: number;
  text: string;
  crossReferences?: CrossReference[];
  topicalGuideEntries?: string[];
  footnotes?: string[];
}

export interface Chapter {
  id: string;
  book: string;
  chapter: number;
  title: string;
  summary?: string;
  verses: Verse[];
}

export interface Book {
  id: string;
  name: string;
  fullName: string;
  abbreviation: string;
  chapters: Chapter[];
}

export interface ScriptureVolume {
  id: string;
  name: string;
  abbreviation: string;
  books: Book[];
}

export interface Scripture {
  volumes: ScriptureVolume[];
}

export interface UserNote {
  id: string;
  verseId: string;
  text: string;
  color: string;
  createdAt: string;
  updatedAt: string;
  tags?: string[];
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
  description?: string;
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
  volume: string;
  bookName: string;
}

export interface StudySession {
  date: string;
  chaptersRead: string[];
  notesAdded: number;
  timeSpent: number; // in minutes
  crossReferencesViewed: number;
}

export interface ReadingPlan {
  id: string;
  name: string;
  description: string;
  duration: number; // days
  dailyAssignments: {
    day: number;
    assignments: {
      volume: string;
      book: string;
      startChapter: number;
      endChapter: number;
    }[];
  }[];
}

export interface AppState {
  currentVolume: string;
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
  readingPlans: ReadingPlan[];
  activeReadingPlan?: string;
  sidebarOpen: boolean;
  activeView: 'read' | 'search' | 'notes' | 'bookmarks' | 'progress' | 'plans';
  showCrossReferences: boolean;
  fontSize: 'small' | 'medium' | 'large';
  theme: 'light' | 'dark' | 'sepia';
}