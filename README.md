# Book of Mormon Study App

A comprehensive, modern web application for studying the Book of Mormon with advanced features for notes, bookmarks, search, and progress tracking.

![Book of Mormon Study App](https://img.shields.io/badge/React-18.2.0-blue) ![TypeScript](https://img.shields.io/badge/TypeScript-4.9.0-blue) ![Tailwind](https://img.shields.io/badge/TailwindCSS-3.3.0-blue)

## ✨ Features

### 📖 Scripture Reading
- **Clean, readable interface** with scripture-focused typography
- **Chapter-by-chapter navigation** with previous/next buttons
- **Responsive design** that works on desktop and mobile
- **Verse selection** for adding notes, highlights, and bookmarks

### 🔍 Advanced Search
- **Full-text search** across all Book of Mormon content
- **Fuzzy search** with context highlighting
- **Real-time results** as you type
- **Click to navigate** directly to any verse from search results

### 📝 Personal Study Tools
- **Notes**: Add personal insights and thoughts to any verse
- **Highlights**: Color-code important passages
- **Bookmarks**: Save favorite verses for quick access
- **Edit and delete** your notes and bookmarks anytime

### 📊 Progress Tracking
- **Reading progress** by book and chapter
- **Study session statistics** including time spent and chapters read
- **Goal setting** with daily, weekly, and monthly targets
- **Visual progress indicators** and completion tracking

### 🎨 Modern UI/UX
- **Beautiful, clean design** optimized for reading
- **Intuitive navigation** with collapsible sidebar
- **Smooth animations** and transitions
- **Responsive layout** that adapts to any screen size

## 🚀 Getting Started

### Prerequisites
- Node.js 16 or higher
- npm or yarn package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd book-of-mormon-study-app
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start the development server**
   ```bash
   npm start
   ```

4. **Open your browser**
   Navigate to `http://localhost:3000` to start using the app

### Build for Production

```bash
npm run build
```

This creates an optimized build in the `build` folder ready for deployment.

## 📱 How to Use

### Reading Scripture
1. **Navigation**: Use the sidebar to browse books and chapters
2. **Verse Selection**: Click on any verse to select it
3. **Actions**: When a verse is selected, use the action panel to:
   - Add personal notes
   - Highlight the verse
   - Bookmark for later reference

### Search Function
1. **Access Search**: Click the "Search" tab in the header
2. **Enter Query**: Type at least 3 characters to start searching
3. **View Results**: Browse highlighted search results
4. **Navigate**: Click any result to jump to that verse

### Managing Notes
1. **View Notes**: Click the "Notes" tab to see all your notes
2. **Edit Notes**: Click the edit icon to modify any note
3. **Delete Notes**: Click the trash icon to remove notes
4. **Navigate**: Click the verse reference to jump to that scripture

### Bookmarks
1. **View Bookmarks**: Click the "Bookmarks" tab
2. **Navigate**: Click "Go to [reference]" to jump to any bookmarked verse
3. **Remove**: Click the trash icon to remove bookmarks

### Progress Tracking
1. **View Progress**: Click the "Progress" tab
2. **See Statistics**: View reading completion, study time, and session data
3. **Track Goals**: Monitor daily, weekly, and monthly reading goals

## 💾 Data Storage

All your personal data (notes, bookmarks, highlights, and progress) is stored locally in your browser using localStorage. This means:

- ✅ **Privacy**: Your data never leaves your device
- ✅ **Offline Access**: Works without internet connection
- ✅ **Fast Performance**: No server requests needed
- ⚠️ **Browser Specific**: Data is tied to your specific browser

## 🛠️ Technical Details

### Built With
- **React 18** - Modern React with hooks
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Utility-first styling
- **Lucide React** - Beautiful icons
- **Fuse.js** - Fuzzy search functionality

### Project Structure
```
src/
├── components/          # React components
│   ├── Header.tsx      # Navigation header
│   ├── Sidebar.tsx     # Book/chapter navigation
│   ├── ScriptureReader.tsx  # Main reading interface
│   ├── SearchView.tsx  # Search functionality
│   ├── NotesView.tsx   # Notes management
│   ├── BookmarksView.tsx    # Bookmarks management
│   ├── ProgressView.tsx     # Progress tracking
│   └── VerseComponent.tsx   # Individual verse display
├── data/               # Scripture data
│   └── bookOfMormon.ts # Book of Mormon text
├── types.ts           # TypeScript type definitions
├── App.tsx           # Main app component
└── index.tsx         # App entry point
```

### Key Features Implementation
- **State Management**: React hooks with localStorage persistence
- **Search**: Fuse.js for fuzzy search with highlighting
- **Responsive Design**: Tailwind CSS with mobile-first approach
- **Type Safety**: Full TypeScript implementation
- **Accessibility**: ARIA labels and keyboard navigation

## 🎯 Future Enhancements

Potential features for future development:
- Cross-references and topic indexing
- Reading plans and schedules
- Study groups and sharing
- Audio narration
- Multiple language support
- Export notes to PDF
- Sync across devices

## 🤝 Contributing

This is a study tool designed to help people engage more deeply with the Book of Mormon. Contributions that enhance the study experience are welcome.

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- Book of Mormon text sourced from official publications
- Icons provided by Lucide React
- Typography optimized for scripture reading

---

**Happy Studying!** 📖✨