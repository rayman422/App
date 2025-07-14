import React from 'react';
import { X, BookOpen, Search, FileText, Bookmark, BarChart3, Keyboard } from 'lucide-react';

interface HelpModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const HelpModal: React.FC<HelpModalProps> = ({ isOpen, onClose }) => {
  if (!isOpen) return null;

  const features = [
    {
      icon: BookOpen,
      title: "Reading Scripture",
      description: "Click verses to interact, use arrow keys (← →) to navigate chapters, and explore cross-references."
    },
    {
      icon: Search,
      title: "Search",
      description: "Type 3+ characters to search across all scriptures. Results show highlighted matches and context."
    },
    {
      icon: FileText,
      title: "Notes",
      description: "Select verses and add personal study insights. Edit and organize your thoughts by tags."
    },
    {
      icon: Bookmark,
      title: "Bookmarks",
      description: "Save important verses for quick reference. Bookmarks show full context and easy navigation."
    },
    {
      icon: BarChart3,
      title: "Progress",
      description: "Track reading completion, study sessions, and set goals. Monitor your scripture study habits."
    },
    {
      icon: Keyboard,
      title: "Shortcuts",
      description: "Use ← → for navigation, ESC to clear selections. Click and interact with verses efficiently."
    }
  ];

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Quick Start Guide</h2>
            <p className="text-gray-600 mt-1">Learn how to use the Book of Mormon Study App</p>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            title="Close help"
          >
            <X className="w-6 h-6 text-gray-500" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6">
          {/* Introduction */}
          <div className="mb-8 p-4 bg-blue-50 rounded-lg border border-blue-200">
            <h3 className="font-semibold text-blue-900 mb-2">Welcome to Scripture Study!</h3>
            <p className="text-blue-800 text-sm">
              This app helps you study the Book of Mormon and Doctrine & Covenants with powerful tools for 
              notes, cross-references, highlighting, and progress tracking. Everything stays private on your device.
            </p>
          </div>

          {/* Features Grid */}
          <div className="grid md:grid-cols-2 gap-6 mb-8">
            {features.map((feature, index) => {
              const IconComponent = feature.icon;
              return (
                <div key={index} className="flex items-start space-x-3 p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
                  <div className="flex-shrink-0 w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
                    <IconComponent className="w-5 h-5 text-primary-600" />
                  </div>
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-1">{feature.title}</h4>
                    <p className="text-sm text-gray-600">{feature.description}</p>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Quick Tips */}
          <div className="bg-gray-50 rounded-lg p-6">
            <h3 className="font-semibold text-gray-900 mb-4">Quick Tips</h3>
            <div className="space-y-3 text-sm text-gray-700">
              <div className="flex items-start space-x-2">
                <span className="w-2 h-2 bg-primary-500 rounded-full mt-2 flex-shrink-0"></span>
                <p><strong>Start Reading:</strong> Use the sidebar to navigate to any book and chapter</p>
              </div>
              <div className="flex items-start space-x-2">
                <span className="w-2 h-2 bg-primary-500 rounded-full mt-2 flex-shrink-0"></span>
                <p><strong>Verse Interaction:</strong> Click any verse to add notes, highlights, or bookmarks</p>
              </div>
              <div className="flex items-start space-x-2">
                <span className="w-2 h-2 bg-primary-500 rounded-full mt-2 flex-shrink-0"></span>
                <p><strong>Cross-References:</strong> Look for green dots and click to explore related scriptures</p>
              </div>
              <div className="flex items-start space-x-2">
                <span className="w-2 h-2 bg-primary-500 rounded-full mt-2 flex-shrink-0"></span>
                <p><strong>Highlights:</strong> Choose from 4 colors and remove by clicking the small X</p>
              </div>
              <div className="flex items-start space-x-2">
                <span className="w-2 h-2 bg-primary-500 rounded-full mt-2 flex-shrink-0"></span>
                <p><strong>Keyboard Navigation:</strong> Use arrow keys to move between chapters quickly</p>
              </div>
            </div>
          </div>

          {/* Color Legend */}
          <div className="mt-6 p-4 border border-gray-200 rounded-lg">
            <h4 className="font-semibold text-gray-900 mb-3">Verse Indicators</h4>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
                <span>Has Notes</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
                <span>Highlighted</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                <span>Cross-References</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-purple-500 rounded-full"></div>
                <span>Topical Guide</span>
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="border-t border-gray-200 p-6 bg-gray-50">
          <div className="flex items-center justify-between">
            <p className="text-sm text-gray-600">
              All your data stays private on your device. Happy studying! 📖
            </p>
            <button
              onClick={onClose}
              className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors font-medium"
            >
              Start Studying
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HelpModal;