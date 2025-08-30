import React from 'react';
import { useNavigate } from 'react-router-dom';
import { LogIn, UserPlus, BookOpen, Brain, Award, TrendingUp, Users, Zap } from 'lucide-react';
import { Button, Card } from './ui';
import { useAuth } from '../contexts/AuthContext';
import './landing.css';

function LandingPage() {
  const navigate = useNavigate();
  const { isAuthenticated, user } = useAuth();

  return (
    <div className="min-h-screen bg-gradient-to-br from-dark-900 via-dark-800 to-dark-900">
      {/* Navigation */}
      <nav className="flex items-center justify-between px-6 py-4 bg-dark-800/80 backdrop-blur-sm border-b border-dark-700">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
            <Brain className="h-5 w-5 text-white" />
          </div>
          <span className="text-xl font-bold text-gray-100">GyanForge</span>
        </div>
        
        <div className="flex items-center gap-3">
          {isAuthenticated ? (
            <>
              <span className="text-gray-300">Welcome, {user?.full_name}!</span>
              <Button onClick={() => navigate('/dashboard')}>
                Go to Dashboard
              </Button>
            </>
          ) : (
            <>
              <Button variant="ghost" onClick={() => navigate('/login')}>
                <LogIn className="h-4 w-4 mr-2" />
                Sign In
              </Button>
              <Button onClick={() => navigate('/register')}>
                <UserPlus className="h-4 w-4 mr-2" />
                Sign Up
              </Button>
            </>
          )}
        </div>
      </nav>

      {/* Hero Section */}
      <div className="max-w-6xl mx-auto px-6 py-20">
        <div className="text-center mb-16">
          <h1 className="text-5xl md:text-6xl font-bold text-gray-100 mb-6">
            Your AI-Powered
            <span className="text-primary-400 block">Learning Companion</span>
          </h1>
          <p className="text-xl text-gray-400 mb-8 max-w-3xl mx-auto">
            Transform your learning journey with personalized AI-generated modules, 
            interactive quizzes, and instant feedback. Master any topic at your own pace.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            {isAuthenticated ? (
              <>
                <Button 
                  size="lg" 
                  onClick={() => navigate('/dashboard')}
                  className="text-lg px-8 py-4"
                >
                  <BookOpen className="mr-2 h-5 w-5" />
                  Continue Learning
                </Button>
                <Button 
                  variant="outline" 
                  size="lg"
                  onClick={() => navigate('/dashboard')}
                  className="text-lg px-8 py-4"
                >
                  <Brain className="mr-2 h-5 w-5" />
                  Take a Quiz
                </Button>
              </>
            ) : (
              <>
                <Button 
                  size="lg" 
                  onClick={() => navigate('/register')}
                  className="text-lg px-8 py-4"
                >
                  <Zap className="mr-2 h-5 w-5" />
                  Start Learning Free
                </Button>
                <Button 
                  variant="outline" 
                  size="lg"
                  onClick={() => navigate('/login')}
                  className="text-lg px-8 py-4"
                >
                  <LogIn className="mr-2 h-5 w-5" />
                  Sign In
                </Button>
              </>
            )}
          </div>
        </div>

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mb-20">
          <Card className="text-center hover:shadow-lg transition-all bg-dark-800 border-dark-700">
            <div className="w-16 h-16 bg-primary-900 rounded-full flex items-center justify-center mx-auto mb-4">
              <Brain className="h-8 w-8 text-primary-400" />
            </div>
            <h3 className="text-xl font-semibold text-gray-100 mb-3">
              AI-Generated Content
            </h3>
            <p className="text-gray-400">
              Get personalized learning modules created by advanced AI based on your specific learning goals and difficulty preferences.
            </p>
          </Card>

          <Card className="text-center hover:shadow-lg transition-all bg-dark-800 border-dark-700">
            <div className="w-16 h-16 bg-green-900 rounded-full flex items-center justify-center mx-auto mb-4">
              <Award className="h-8 w-8 text-green-400" />
            </div>
            <h3 className="text-xl font-semibold text-gray-100 mb-3">
              Interactive Quizzes
            </h3>
            <p className="text-gray-400">
              Test your knowledge with automatically generated quizzes that adapt to your learning progress and provide instant feedback.
            </p>
          </Card>

          <Card className="text-center hover:shadow-lg transition-all bg-dark-800 border-dark-700">
            <div className="w-16 h-16 bg-yellow-900 rounded-full flex items-center justify-center mx-auto mb-4">
              <BookOpen className="h-8 w-8 text-yellow-400" />
            </div>
            <h3 className="text-xl font-semibold text-gray-100 mb-3">
              Practice Assignments
            </h3>
            <p className="text-gray-400">
              Reinforce your learning with practical assignments and downloadable PDF worksheets tailored to each topic.
            </p>
          </Card>

          <Card className="text-center hover:shadow-lg transition-all bg-dark-800 border-dark-700">
            <div className="w-16 h-16 bg-blue-900 rounded-full flex items-center justify-center mx-auto mb-4">
              <TrendingUp className="h-8 w-8 text-blue-400" />
            </div>
            <h3 className="text-xl font-semibold text-gray-100 mb-3">
              Progress Tracking
            </h3>
            <p className="text-gray-400">
              Monitor your learning journey with detailed analytics, completion rates, and personalized recommendations.
            </p>
          </Card>

          <Card className="text-center hover:shadow-lg transition-all bg-dark-800 border-dark-700">
            <div className="w-16 h-16 bg-purple-900 rounded-full flex items-center justify-center mx-auto mb-4">
              <Users className="h-8 w-8 text-purple-400" />
            </div>
            <h3 className="text-xl font-semibold text-gray-100 mb-3">
              Adaptive Learning
            </h3>
            <p className="text-gray-400">
              Experience learning that adapts to your pace, learning style, and knowledge gaps for maximum effectiveness.
            </p>
          </Card>

          <Card className="text-center hover:shadow-lg transition-all bg-dark-800 border-dark-700">
            <div className="w-16 h-16 bg-red-900 rounded-full flex items-center justify-center mx-auto mb-4">
              <Zap className="h-8 w-8 text-red-400" />
            </div>
            <h3 className="text-xl font-semibold text-gray-100 mb-3">
              Instant Feedback
            </h3>
            <p className="text-gray-400">
              Get immediate feedback on your progress, detailed explanations for quiz answers, and suggestions for improvement.
            </p>
          </Card>
        </div>

        {/* CTA Section */}
        <div className="text-center bg-gradient-to-r from-primary-800 to-blue-800 rounded-2xl p-12 text-white border border-dark-700">
          <h2 className="text-3xl font-bold mb-4">
            Ready to Transform Your Learning?
          </h2>
          <p className="text-xl opacity-90 mb-8 max-w-2xl mx-auto">
            Join thousands of learners who are already using AI to accelerate their education. 
            Start your personalized learning journey today.
          </p>
          
          {isAuthenticated ? (
            <Button 
              size="lg" 
              variant="secondary"
              onClick={() => navigate('/dashboard')}
              className="text-lg px-8 py-4"
            >
              <BookOpen className="mr-2 h-5 w-5" />
              Go to Dashboard
            </Button>
          ) : (
            <Button 
              size="lg" 
              variant="secondary"
              onClick={() => navigate('/register')}
              className="text-lg px-8 py-4"
            >
              <UserPlus className="mr-2 h-5 w-5" />
              Create Free Account
            </Button>
          )}
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="max-w-6xl mx-auto px-6">
          <div className="flex flex-col md:flex-row items-center justify-between">
            <div className="flex items-center gap-2 mb-4 md:mb-0">
              <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
                <Brain className="h-5 w-5 text-white" />
              </div>
              <span className="text-xl font-bold">GyanForge</span>
            </div>
            
            <div className="text-gray-400 text-center md:text-right">
              <p>&copy; 2025 GyanForge. Empowering learners with AI.</p>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default LandingPage;
