import React, { useState } from 'react';
import { UserNote, Scripture } from '../types';
import { MessageSquare, ExternalLink, Edit3, Trash2, Calendar } from 'lucide-react';

interface NotesViewProps {
  notes: UserNote[];
  onNavigateToVerse: (bookId: string, chapter: number, verse?: number) => void;
  onUpdateNote: (noteId: string, text: string) => void;
  onDeleteNote: (noteId: string) => void;
  bookOfMormon: Scripture;
}

const NotesView: React.FC<NotesViewProps> = ({
  notes,
  onNavigateToVerse,
  onUpdateNote,
  onDeleteNote,
  bookOfMormon
}) => {
  const [editingNote, setEditingNote] = useState<string | null>(null);
  const [editText, setEditText] = useState('');

  const getVerseReference = (verseId: string) => {
    for (const book of bookOfMormon.books) {
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
    return null;
  };

  const handleStartEdit = (note: UserNote) => {
    setEditingNote(note.id);
    setEditText(note.text);
  };

  const handleSaveEdit = () => {
    if (editingNote && editText.trim()) {
      onUpdateNote(editingNote, editText.trim());
      setEditingNote(null);
      setEditText('');
    }
  };

  const handleCancelEdit = () => {
    setEditingNote(null);
    setEditText('');
  };

  const handleDeleteNote = (noteId: string) => {
    if (window.confirm('Are you sure you want to delete this note?')) {
      onDeleteNote(noteId);
    }
  };

  const sortedNotes = notes.sort((a, b) => 
    new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime()
  );

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">My Notes</h1>
        <p className="text-gray-600">
          View and manage all your personal study notes.
        </p>
      </div>

      {sortedNotes.length === 0 ? (
        <div className="text-center py-12">
          <MessageSquare className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No notes yet</h3>
          <p className="text-gray-600">
            Start reading and click on verses to add your first note!
          </p>
        </div>
      ) : (
        <div className="space-y-6">
          <div className="text-sm text-gray-500 mb-4">
            {sortedNotes.length} note{sortedNotes.length !== 1 ? 's' : ''}
          </div>
          
          {sortedNotes.map((note) => {
            const verseInfo = getVerseReference(note.verseId);
            if (!verseInfo) return null;

            return (
              <div key={note.id} className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
                <div className="flex items-start justify-between mb-4">
                  <button
                    onClick={() => onNavigateToVerse(verseInfo.bookId, verseInfo.chapter, verseInfo.verse)}
                    className="flex items-center space-x-2 text-primary-600 hover:text-primary-700 font-medium"
                  >
                    <span>{verseInfo.reference}</span>
                    <ExternalLink className="w-4 h-4" />
                  </button>
                  
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => handleStartEdit(note)}
                      className="p-2 text-gray-400 hover:text-gray-600 rounded-md hover:bg-gray-100"
                      title="Edit note"
                    >
                      <Edit3 className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => handleDeleteNote(note.id)}
                      className="p-2 text-gray-400 hover:text-red-600 rounded-md hover:bg-gray-100"
                      title="Delete note"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>

                <div className="bg-gray-50 border-l-4 border-gray-300 p-4 mb-4">
                  <p className="text-gray-700 text-sm italic">{verseInfo.text}</p>
                </div>

                {editingNote === note.id ? (
                  <div className="space-y-3">
                    <textarea
                      value={editText}
                      onChange={(e) => setEditText(e.target.value)}
                      className="w-full p-3 border border-gray-300 rounded-md resize-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                      rows={3}
                      placeholder="Enter your note..."
                    />
                    <div className="flex space-x-3">
                      <button
                        onClick={handleSaveEdit}
                        className="btn-primary"
                        disabled={!editText.trim()}
                      >
                        Save Changes
                      </button>
                      <button
                        onClick={handleCancelEdit}
                        className="btn-secondary"
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                ) : (
                  <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
                    <p className="text-blue-800">{note.text}</p>
                  </div>
                )}

                <div className="flex items-center space-x-4 mt-4 text-xs text-gray-500">
                  <div className="flex items-center space-x-1">
                    <Calendar className="w-3 h-3" />
                    <span>Created {new Date(note.createdAt).toLocaleDateString()}</span>
                  </div>
                  {note.updatedAt !== note.createdAt && (
                    <div className="flex items-center space-x-1">
                      <span>Updated {new Date(note.updatedAt).toLocaleDateString()}</span>
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default NotesView;