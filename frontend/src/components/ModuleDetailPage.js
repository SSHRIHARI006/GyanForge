import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  Brain, 
  FileText, 
  Download, 
  ArrowLeft, 
  Clock, 
  User,
  PlayCircle
} from 'lucide-react';
import { Button, Card, Badge, LoadingSpinner } from './ui';
import apiService from '../services/apiService';
import { useAuth } from '../contexts/AuthContext';

const ModuleDetailPage = () => {
  const { moduleId } = useParams();
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  
  const [module, setModule] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }
    loadModule();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [moduleId, isAuthenticated]);

  const loadModule = async () => {
    try {
      setLoading(true);
      const moduleData = await apiService.getModule(moduleId);
      setModule(moduleData);
    } catch (err) {
      setError('Failed to load module. Please try again.');
      console.error('Error loading module:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadPDF = async () => {
    try {
      const pdfBlob = await apiService.getAssignmentPdf(moduleId);
      const url = window.URL.createObjectURL(pdfBlob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${module.title.replace(/[^a-z0-9]/gi, '_').toLowerCase()}_assignment.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Error downloading PDF:', error);
    }
  };

  const getDifficultyColor = (difficulty) => {
    switch (difficulty) {
      case 'easy': return 'success';
      case 'medium': return 'warning';
      case 'hard': return 'error';
      default: return 'gray';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-dark-800">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (error || !module) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-dark-800">
        <Card className="max-w-md">
          <div className="text-center">
            <h2 className="text-2xl font-bold text-gray-100 mb-4">Error</h2>
            <p className="text-gray-400 mb-6">{error || 'Module not found.'}</p>
            <Button onClick={() => navigate('/dashboard')}>Back to Dashboard</Button>
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-dark-800">
      {/* Header */}
      <div className="bg-dark-900 shadow-sm border-b border-dark-700">
        <div className="max-w-4xl mx-auto px-4 py-6">
          <div className="flex items-center gap-4 mb-4">
            <Button
              variant="ghost"
              onClick={() => navigate('/dashboard')}
              className="flex items-center gap-2"
            >
              <ArrowLeft className="h-4 w-4" />
              Back to Dashboard
            </Button>
          </div>
          
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-3">
                <Badge variant={getDifficultyColor(module.difficulty)}>
                  {module.difficulty || 'Medium'}
                </Badge>
                <div className="flex items-center gap-1 text-gray-400">
                  <Clock className="h-4 w-4" />
                  <span className="text-sm">{module.duration || 30} min</span>
                </div>
              </div>
              
              <h1 className="text-3xl font-bold text-gray-100 mb-2">
                {module.title}
              </h1>
              
              <div className="flex items-center gap-4 text-sm text-gray-400">
                <div className="flex items-center gap-1">
                  <User className="h-4 w-4" />
                  <span>Created by AI</span>
                </div>
                {module.created_at && (
                  <span>
                    {new Date(module.created_at).toLocaleDateString()}
                  </span>
                )}
              </div>
            </div>
            
            <div className="flex gap-3">
              {module.quiz_questions && module.quiz_questions.length > 0 && (
                <Button
                  onClick={() => navigate(`/quiz/${moduleId}`)}
                  className="flex items-center gap-2"
                >
                  <Brain className="h-4 w-4" />
                  Take Quiz ({module.quiz_questions.length})
                </Button>
              )}
              
              {module.assignment_latex && (
                <Button
                  variant="outline"
                  onClick={handleDownloadPDF}
                  className="flex items-center gap-2"
                >
                  <Download className="h-4 w-4" />
                  Download Assignment
                </Button>
              )}
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2">
            <Card>
              <div className="prose max-w-none">
                <h2 className="text-xl font-semibold text-gray-100 mb-4">
                  Learning Content
                </h2>
                <div className="text-gray-300 leading-relaxed whitespace-pre-wrap">
                  {module.content}
                </div>
              </div>
            </Card>

            {/* Assignment Preview */}
            {module.assignment_latex && (
              <Card className="mt-6">
                <h2 className="text-xl font-semibold text-gray-100 mb-4">
                  Assignment Preview
                </h2>
                <div className="bg-dark-700 rounded-lg p-4 border-l-4 border-primary-500">
                  <div className="flex items-center gap-2 mb-3">
                    <FileText className="h-5 w-5 text-primary-400" />
                    <span className="font-medium text-gray-100">
                      Practice Assignment
                    </span>
                  </div>
                  <div className="text-gray-700 font-mono text-sm whitespace-pre-wrap bg-white p-4 rounded border">
                    {module.assignment_latex.substring(0, 300)}...
                  </div>
                  <div className="mt-4">
                    <Button
                      variant="outline"
                      onClick={handleDownloadPDF}
                      className="flex items-center gap-2"
                    >
                      <Download className="h-4 w-4" />
                      Download Full Assignment (PDF)
                    </Button>
                  </div>
                </div>
              </Card>
            )}
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Quiz Section */}
            {module.quiz_questions && module.quiz_questions.length > 0 && (
              <Card>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Test Your Knowledge
                </h3>
                <div className="space-y-4">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center">
                      <Brain className="h-6 w-6 text-primary-600" />
                    </div>
                    <div>
                      <div className="font-medium text-gray-900">
                        Interactive Quiz
                      </div>
                      <div className="text-sm text-gray-600">
                        {module.quiz_questions.length} questions
                      </div>
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    {module.quiz_questions.slice(0, 3).map((question, index) => (
                      <div key={index} className="text-sm text-gray-600 pl-4 border-l-2 border-gray-200">
                        Q{index + 1}: {question.question.substring(0, 60)}...
                      </div>
                    ))}
                    {module.quiz_questions.length > 3 && (
                      <div className="text-sm text-gray-500 pl-4">
                        +{module.quiz_questions.length - 3} more questions
                      </div>
                    )}
                  </div>
                  
                  <Button
                    onClick={() => navigate(`/quiz/${moduleId}`)}
                    className="w-full flex items-center justify-center gap-2"
                  >
                    <PlayCircle className="h-4 w-4" />
                    Start Quiz
                  </Button>
                </div>
              </Card>
            )}

            {/* Module Stats */}
            <Card>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Module Details
              </h3>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-600">Difficulty</span>
                  <Badge variant={getDifficultyColor(module.difficulty)}>
                    {module.difficulty || 'Medium'}
                  </Badge>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Duration</span>
                  <span className="font-medium">{module.duration || 30} min</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Content Length</span>
                  <span className="font-medium">{module.content?.length || 0} chars</span>
                </div>
                {module.quiz_questions && (
                  <div className="flex justify-between">
                    <span className="text-gray-600">Questions</span>
                    <span className="font-medium">{module.quiz_questions.length}</span>
                  </div>
                )}
                <div className="flex justify-between">
                  <span className="text-gray-600">Assignment</span>
                  <span className="font-medium">
                    {module.assignment_latex ? '✅ Available' : '❌ Not available'}
                  </span>
                </div>
              </div>
            </Card>

            {/* Actions */}
            <Card>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Quick Actions
              </h3>
              <div className="space-y-3">
                <Button
                  variant="outline"
                  onClick={() => navigate('/dashboard')}
                  className="w-full flex items-center justify-center gap-2"
                >
                  <ArrowLeft className="h-4 w-4" />
                  Back to Dashboard
                </Button>
                
                {module.assignment_latex && (
                  <Button
                    variant="outline"
                    onClick={handleDownloadPDF}
                    className="w-full flex items-center justify-center gap-2"
                  >
                    <Download className="h-4 w-4" />
                    Download Assignment
                  </Button>
                )}
              </div>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ModuleDetailPage;
