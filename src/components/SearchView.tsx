import React, { useState, useEffect } from 'react';
import { Scripture, SearchResult } from '../types';
import { Search, ExternalLink } from 'lucide-react';
import Fuse from 'fuse.js';

interface SearchViewProps {
  searchQuery: string;
  searchResults: SearchResult[];
  onSearchQueryChange: (query: string) => void;
  onSearchResultsChange: (results: SearchResult[]) => void;
  onNavigateToVerse: (bookId: string, chapter: number, verse?: number) => void;
  bookOfMormon: Scripture;
}

const SearchView: React.FC<SearchViewProps> = ({
  searchQuery,
  searchResults,
  onSearchQueryChange,
  onSearchResultsChange,
  onNavigateToVerse,
  bookOfMormon
}) => {
  const [isSearching, setIsSearching] = useState(false);

  // Flatten all verses for search
  const allVerses = bookOfMormon.books.flatMap(book =>
    book.chapters.flatMap(chapter => chapter.verses)
  );

  const fuse = new Fuse(allVerses, {
    keys: ['text'],
    threshold: 0.3,
    includeMatches: true,
    minMatchCharLength: 3
  });

  useEffect(() => {
    if (searchQuery.trim().length >= 3) {
      setIsSearching(true);
      const searchTimer = setTimeout(() => {
        const fuseResults = fuse.search(searchQuery);
        const results: SearchResult[] = fuseResults.map(result => ({
          verse: result.item,
          matchText: result.matches?.[0]?.value || result.item.text,
          context: getContext(result.item.text, searchQuery)
        }));
        onSearchResultsChange(results);
        setIsSearching(false);
      }, 300);

      return () => clearTimeout(searchTimer);
    } else {
      onSearchResultsChange([]);
    }
  }, [searchQuery]);

  const getContext = (text: string, query: string) => {
    const queryLower = query.toLowerCase();
    const textLower = text.toLowerCase();
    const index = textLower.indexOf(queryLower);
    
    if (index === -1) return text;
    
    const start = Math.max(0, index - 50);
    const end = Math.min(text.length, index + query.length + 50);
    
    let context = text.slice(start, end);
    if (start > 0) context = '...' + context;
    if (end < text.length) context = context + '...';
    
    return context;
  };

  const highlightMatch = (text: string, query: string) => {
    if (!query) return text;
    
    const regex = new RegExp(`(${query})`, 'gi');
    const parts = text.split(regex);
    
    return parts.map((part, index) => 
      regex.test(part) ? (
        <mark key={index} className="search-highlight">{part}</mark>
      ) : part
    );
  };

  const handleResultClick = (result: SearchResult) => {
    const verse = result.verse;
    onNavigateToVerse(verse.book.toLowerCase().replace(/\s+/g, '-'), verse.chapter, verse.verse);
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">Search Scripture</h1>
        <p className="text-gray-600 mb-6">
          Search through the Book of Mormon to find specific verses, topics, or concepts.
        </p>
        
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => onSearchQueryChange(e.target.value)}
            placeholder="Search for words, phrases, or concepts..."
            className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent text-lg"
            autoFocus
          />
        </div>
        
        {searchQuery.length > 0 && searchQuery.length < 3 && (
          <p className="mt-2 text-sm text-gray-500">
            Enter at least 3 characters to search
          </p>
        )}
      </div>

      {isSearching && (
        <div className="flex items-center justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
          <span className="ml-3 text-gray-600">Searching...</span>
        </div>
      )}

      {searchResults.length > 0 && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold text-gray-900">
              Search Results ({searchResults.length})
            </h2>
          </div>
          
          {searchResults.map((result, index) => (
            <div
              key={`${result.verse.id}-${index}`}
              className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer"
              onClick={() => handleResultClick(result)}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-2">
                    <span className="text-sm font-medium text-primary-600">
                      {result.verse.book} {result.verse.chapter}:{result.verse.verse}
                    </span>
                    <ExternalLink className="w-4 h-4 text-gray-400" />
                  </div>
                  
                  <p className="text-gray-800 leading-relaxed">
                    {highlightMatch(result.context, searchQuery)}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {searchQuery.length >= 3 && searchResults.length === 0 && !isSearching && (
        <div className="text-center py-8">
          <Search className="w-12 h-12 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No results found</h3>
          <p className="text-gray-600">
            Try different keywords or check your spelling
          </p>
        </div>
      )}
    </div>
  );
};

export default SearchView;