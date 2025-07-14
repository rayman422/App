import React from 'react';
import { Menu, Book, Search, StickyNote, Bookmark, TrendingUp, HelpCircle } from 'lucide-react';

interface HeaderProps {
  activeView: 'read' | 'search' | 'notes' | 'bookmarks' | 'progress' | 'plans';
  onViewChange: (view: 'read' | 'search' | 'notes' | 'bookmarks' | 'progress' | 'plans') => void;
  onToggleSidebar: () => void;
  sidebarOpen: boolean;
  onShowHelp?: () => void;
}

const Header: React.FC<HeaderProps> = ({
  activeView,
  onViewChange,
  onToggleSidebar,
  sidebarOpen,
  onShowHelp
}) => {
  const navItems = [
    { id: 'read', label: 'Read', icon: Book },
    { id: 'search', label: 'Search', icon: Search },
    { id: 'notes', label: 'Notes', icon: StickyNote },
    { id: 'bookmarks', label: 'Bookmarks', icon: Bookmark },
    { id: 'progress', label: 'Progress', icon: TrendingUp },
  ] as const;

  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="flex items-center justify-between px-4 py-3">
        <div className="flex items-center space-x-4">
          <button
            onClick={onToggleSidebar}
            className="p-2 rounded-md hover:bg-gray-100 transition-colors"
            aria-label="Toggle sidebar"
          >
            <Menu className="w-5 h-5 text-gray-600" />
          </button>
          
          <h1 className="text-xl font-bold text-primary-700">
            Book of Mormon Study
          </h1>
        </div>

        <div className="flex items-center space-x-2">
          <nav className="flex space-x-1">
            {navItems.map(({ id, label, icon: Icon }) => (
              <button
                key={id}
                onClick={() => onViewChange(id)}
                className={`
                  flex items-center space-x-2 px-3 py-2 rounded-md font-medium transition-colors
                  ${activeView === id
                    ? 'bg-primary-100 text-primary-700 border border-primary-200'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                  }
                `}
              >
                <Icon className="w-4 h-4" />
                <span className="hidden sm:block">{label}</span>
              </button>
            ))}
          </nav>
          
          {onShowHelp && (
            <button
              onClick={onShowHelp}
              className="p-2 rounded-md text-gray-600 hover:text-gray-900 hover:bg-gray-100 transition-colors"
              title="Show help"
            >
              <HelpCircle className="w-5 h-5" />
            </button>
          )}
        </div>
      </div>
    </header>
  );
};

export default Header;