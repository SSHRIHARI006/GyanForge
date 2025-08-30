import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import ErrorBoundary from './components/ErrorBoundary';
import LandingPage from './components/LandingPage';
import LoginPage from './components/LoginPage';
import RegisterPage from './components/RegisterPage';
import Dashboard from './components/Dashboard';
import ModuleDetailPage from './components/ModuleDetailPage';
import QuizPage from './components/QuizPage';
import LearningPage from './components/LearningPage';
import TopicPage from './components/TopicPage';
import MainContent from './components/MainContent';
import EnhancedModules from './components/EnhancedModules';
import EnhancedChatBox from './components/EnhancedChatBox';
import TestPage from './components/TestPage';
import Sidebar from './components/Sidebar';
import ChatBox from './components/ChatBox';
import './App.css';

function App() {
  useEffect(() => {
    // Enable dark mode by default
    document.documentElement.classList.add('dark');
  }, []);

  return (
    <ErrorBoundary>
      <AuthProvider>
        <Router>
          <div className="min-h-screen bg-gray-50 dark:bg-dark-800">
            <Routes>
              {/* Public routes */}
              <Route path="/" element={<LandingPage />} />
              <Route path="/login" element={<LoginPage />} />
              <Route path="/register" element={<RegisterPage />} />
              
              {/* Protected routes */}
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/modules" element={<EnhancedModules />} />
              <Route path="/module/:moduleId" element={<ModuleDetailPage />} />
              <Route path="/learn/:moduleId" element={<LearningPage />} />
              <Route path="/quiz/:moduleId" element={<QuizPage />} />
              
              {/* Enhanced features routes */}
              <Route 
                path="/chat" 
                element={
                  <div className="min-h-screen bg-gray-50 dark:bg-dark-800 p-4">
                    <EnhancedChatBox />
                  </div>
                } 
              />
              
              {/* Test page for feature validation */}
              <Route path="/test" element={<TestPage />} />
              
              {/* Legacy routes with sidebar (for backward compatibility) */}
              <Route
                path="/topics/:topicId"
                element={
                  <div className="app">
                    <Sidebar />
                    <div className="main">
                      <TopicPage />
                      <ChatBox />
                    </div>
                  </div>
                }
              />
              <Route
                path="/main"
                element={
                  <div className="app">
                    <Sidebar />
                    <div className="main">
                      <MainContent />
                      <ChatBox />
                    </div>
                  </div>
                }
              />
            </Routes>
          </div>
        </Router>
      </AuthProvider>
    </ErrorBoundary>
  );
}

export default App;
