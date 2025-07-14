import React from 'react';
import { ReadingProgress, StudySession, Scripture } from '../types';
import { TrendingUp, BookOpen, Calendar, Clock, Target } from 'lucide-react';

interface ProgressViewProps {
  readingProgress: ReadingProgress[];
  studySessions: StudySession[];
  bookOfMormon: Scripture;
}

const ProgressView: React.FC<ProgressViewProps> = ({
  readingProgress,
  studySessions,
  bookOfMormon
}) => {
  const totalChapters = bookOfMormon.books.reduce((total, book) => total + book.chapters.length, 0);
  const completedChapters = readingProgress.filter(p => p.completed).length;
  const progressPercentage = totalChapters > 0 ? (completedChapters / totalChapters) * 100 : 0;

  const totalSessions = studySessions.length;
  const totalStudyTime = studySessions.reduce((total, session) => total + session.timeSpent, 0);
  const averageSessionTime = totalSessions > 0 ? totalStudyTime / totalSessions : 0;

  const recentSessions = studySessions
    .sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())
    .slice(0, 7);

  const getBookProgress = (bookId: string) => {
    const book = bookOfMormon.books.find(b => b.id === bookId);
    if (!book) return { completed: 0, total: 0, percentage: 0 };
    
    const bookProgress = readingProgress.filter(p => p.bookId === bookId && p.completed);
    const total = book.chapters.length;
    const completed = bookProgress.length;
    const percentage = total > 0 ? (completed / total) * 100 : 0;
    
    return { completed, total, percentage };
  };

  const formatDuration = (minutes: number) => {
    if (minutes < 60) return `${minutes}m`;
    const hours = Math.floor(minutes / 60);
    const remainingMinutes = minutes % 60;
    return remainingMinutes > 0 ? `${hours}h ${remainingMinutes}m` : `${hours}h`;
  };

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">Reading Progress</h1>
        <p className="text-gray-600">
          Track your study progress and see your reading statistics.
        </p>
      </div>

      {/* Overall Progress */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
          <div className="flex items-center">
            <BookOpen className="w-8 h-8 text-blue-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Chapters Read</p>
              <p className="text-2xl font-bold text-gray-900">
                {completedChapters}/{totalChapters}
              </p>
            </div>
          </div>
          <div className="mt-4">
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${progressPercentage}%` }}
              ></div>
            </div>
            <p className="text-sm text-gray-600 mt-1">{progressPercentage.toFixed(1)}% complete</p>
          </div>
        </div>

        <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
          <div className="flex items-center">
            <Calendar className="w-8 h-8 text-green-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Study Sessions</p>
              <p className="text-2xl font-bold text-gray-900">{totalSessions}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
          <div className="flex items-center">
            <Clock className="w-8 h-8 text-purple-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Study Time</p>
              <p className="text-2xl font-bold text-gray-900">{formatDuration(totalStudyTime)}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
          <div className="flex items-center">
            <Target className="w-8 h-8 text-orange-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Avg. Session</p>
              <p className="text-2xl font-bold text-gray-900">{formatDuration(Math.round(averageSessionTime))}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Book Progress */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Progress by Book</h2>
          <div className="space-y-4">
            {bookOfMormon.books.map((book) => {
              const progress = getBookProgress(book.id);
              return (
                <div key={book.id} className="border border-gray-100 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="font-medium text-gray-900">{book.name}</h3>
                    <span className="text-sm text-gray-600">
                      {progress.completed}/{progress.total}
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${progress.percentage}%` }}
                    ></div>
                  </div>
                  <p className="text-xs text-gray-500 mt-1">
                    {progress.percentage.toFixed(0)}% complete
                  </p>
                </div>
              );
            })}
          </div>
        </div>

        {/* Recent Sessions */}
        <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Recent Study Sessions</h2>
          {recentSessions.length === 0 ? (
            <div className="text-center py-8">
              <TrendingUp className="w-12 h-12 text-gray-300 mx-auto mb-3" />
              <p className="text-gray-500">No study sessions recorded yet</p>
            </div>
          ) : (
            <div className="space-y-3">
              {recentSessions.map((session, index) => (
                <div key={index} className="border border-gray-100 rounded-lg p-3">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium text-gray-900">
                        {new Date(session.date).toLocaleDateString()}
                      </p>
                      <p className="text-sm text-gray-600">
                        {session.chaptersRead.length} chapter{session.chaptersRead.length !== 1 ? 's' : ''} read
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="font-medium text-gray-900">
                        {formatDuration(session.timeSpent)}
                      </p>
                      <p className="text-sm text-gray-600">
                        {session.notesAdded} note{session.notesAdded !== 1 ? 's' : ''}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Reading Streak */}
      <div className="mt-8 bg-white rounded-lg p-6 shadow-sm border border-gray-200">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Reading Goals</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center p-4 bg-gray-50 rounded-lg">
            <div className="text-2xl font-bold text-primary-600 mb-2">Daily</div>
            <p className="text-gray-600">Read 1 chapter</p>
            <div className="mt-2 text-sm text-gray-500">
              Keep up your reading habit!
            </div>
          </div>
          
          <div className="text-center p-4 bg-gray-50 rounded-lg">
            <div className="text-2xl font-bold text-green-600 mb-2">Weekly</div>
            <p className="text-gray-600">Complete 1 book</p>
            <div className="mt-2 text-sm text-gray-500">
              Study consistently throughout the week
            </div>
          </div>
          
          <div className="text-center p-4 bg-gray-50 rounded-lg">
            <div className="text-2xl font-bold text-purple-600 mb-2">Monthly</div>
            <p className="text-gray-600">Add 20 notes</p>
            <div className="mt-2 text-sm text-gray-500">
              Deepen your understanding with notes
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProgressView;