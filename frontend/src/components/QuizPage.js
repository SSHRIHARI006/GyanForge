import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { CheckCircle, XCircle, Clock, Award, ArrowRight, ArrowLeft, RotateCcw } from 'lucide-react';
import { Button, Card, Badge, LoadingSpinner } from './ui';
import apiService from '../services/apiService';
import { useAuth } from '../contexts/AuthContext';

const QuizPage = () => {
  const { moduleId } = useParams();
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  
  const [module, setModule] = useState(null);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState({});
  const [submitted, setSubmitted] = useState(false);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [timeLeft, setTimeLeft] = useState(null);
  const [quizStarted, setQuizStarted] = useState(false);

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }
    loadModule();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [moduleId, isAuthenticated]);

  useEffect(() => {
    let timer;
    if (quizStarted && timeLeft > 0 && !submitted) {
      timer = setInterval(() => {
        setTimeLeft(prev => {
          if (prev <= 1) {
            handleSubmit();
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
    }
    return () => clearInterval(timer);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [quizStarted, timeLeft, submitted]);

  const loadModule = async () => {
    try {
      setLoading(true);
      const moduleData = await apiService.getModule(moduleId);
      setModule(moduleData);
      
      if (moduleData.quiz_questions && moduleData.quiz_questions.length > 0) {
        // Set timer for 2 minutes per question
        setTimeLeft(moduleData.quiz_questions.length * 120);
      }
    } catch (err) {
      setError('Failed to load quiz. Please try again.');
      console.error('Error loading module:', err);
    } finally {
      setLoading(false);
    }
  };

  const startQuiz = () => {
    setQuizStarted(true);
    setCurrentQuestion(0);
    setAnswers({});
    setSubmitted(false);
    setResults(null);
  };

  const handleAnswerSelect = (questionIndex, answer) => {
    setAnswers(prev => ({
      ...prev,
      [questionIndex]: answer
    }));
  };

  const nextQuestion = () => {
    if (currentQuestion < module.quiz_questions.length - 1) {
      setCurrentQuestion(prev => prev + 1);
    }
  };

  const prevQuestion = () => {
    if (currentQuestion > 0) {
      setCurrentQuestion(prev => prev - 1);
    }
  };

  const handleSubmit = async () => {
    try {
      setLoading(true);
      const results = await apiService.submitQuiz(moduleId, answers);
      setResults(results);
      setSubmitted(true);
      setQuizStarted(false);
    } catch (err) {
      setError('Failed to submit quiz. Please try again.');
      console.error('Error submitting quiz:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getScoreColor = (score) => {
    if (score >= 80) return 'success';
    if (score >= 60) return 'warning';
    return 'error';
  };

  const getPerformanceMessage = (score) => {
    if (score >= 90) return 'Outstanding! 🌟';
    if (score >= 80) return 'Excellent work! 🎉';
    if (score >= 70) return 'Good job! 👍';
    if (score >= 60) return 'Not bad, but you can do better! 💪';
    return 'Keep practicing! 📚';
  };

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-dark-800">
        <Card className="max-w-md">
          <div className="text-center">
            <h2 className="text-2xl font-bold text-gray-100 mb-4">Authentication Required</h2>
            <p className="text-gray-400 mb-6">Please log in to take quizzes.</p>
            <Button onClick={() => navigate('/login')}>Go to Login</Button>
          </div>
        </Card>
      </div>
    );
  }

  if (loading && !module) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-dark-800">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-dark-800">
        <Card className="max-w-md">
          <div className="text-center">
            <XCircle className="mx-auto h-12 w-12 text-red-500 mb-4" />
            <h2 className="text-2xl font-bold text-gray-100 mb-4">Error</h2>
            <p className="text-gray-400 mb-6">{error}</p>
            <Button onClick={() => window.location.reload()}>Try Again</Button>
          </div>
        </Card>
      </div>
    );
  }

  if (!module || !module.quiz_questions || module.quiz_questions.length === 0) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-dark-800">
        <Card className="max-w-md">
          <div className="text-center">
            <h2 className="text-2xl font-bold text-gray-100 mb-4">No Quiz Available</h2>
            <p className="text-gray-400 mb-6">This module doesn't have a quiz yet.</p>
            <Button onClick={() => navigate('/dashboard')}>Back to Dashboard</Button>
          </div>
        </Card>
      </div>
    );
  }

  // Quiz start screen
  if (!quizStarted && !submitted) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-dark-800 to-dark-900 py-12">
        <div className="max-w-3xl mx-auto px-4">
          <Card className="text-center">
            <div className="mb-8">
              <div className="mx-auto w-20 h-20 bg-primary-800 rounded-full flex items-center justify-center mb-6">
                <Award className="h-10 w-10 text-primary-200" />
              </div>
              <h1 className="text-3xl font-bold text-gray-100 mb-4">
                Quiz: {module.title}
              </h1>
              <p className="text-lg text-gray-400 mb-6">
                Test your knowledge with {module.quiz_questions.length} questions
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
              <div className="text-center">
                <div className="text-2xl font-bold text-primary-400">
                  {module.quiz_questions.length}
                </div>
                <div className="text-sm text-gray-500">Questions</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-primary-600">
                  {formatTime(module.quiz_questions.length * 120)}
                </div>
                <div className="text-sm text-gray-500">Time Limit</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-primary-600">
                  {module.difficulty || 'Medium'}
                </div>
                <div className="text-sm text-gray-500">Difficulty</div>
              </div>
            </div>

            <div className="bg-blue-50 rounded-lg p-6 mb-8">
              <h3 className="font-semibold text-blue-900 mb-3">Quiz Instructions:</h3>
              <ul className="text-left text-blue-800 space-y-2">
                <li>• You have 2 minutes per question</li>
                <li>• You can navigate between questions</li>
                <li>• Make sure to submit before time runs out</li>
                <li>• You'll get instant feedback after submission</li>
              </ul>
            </div>

            <div className="flex gap-4 justify-center">
              <Button
                onClick={startQuiz}
                size="lg"
                className="px-8"
              >
                Start Quiz
                <ArrowRight className="ml-2 h-5 w-5" />
              </Button>
              <Button
                variant="outline"
                onClick={() => navigate('/dashboard')}
                size="lg"
              >
                Back to Dashboard
              </Button>
            </div>
          </Card>
        </div>
      </div>
    );
  }

  // Quiz results screen
  if (submitted && results) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary-50 to-blue-100 py-12">
        <div className="max-w-3xl mx-auto px-4">
          <Card>
            <div className="text-center mb-8">
              <div className={`mx-auto w-20 h-20 rounded-full flex items-center justify-center mb-6 ${
                results.score >= 80 ? 'bg-green-100' : results.score >= 60 ? 'bg-yellow-100' : 'bg-red-100'
              }`}>
                {results.score >= 80 ? (
                  <CheckCircle className="h-10 w-10 text-green-600" />
                ) : (
                  <Award className="h-10 w-10 text-yellow-600" />
                )}
              </div>
              
              <h1 className="text-3xl font-bold text-gray-100 mb-4">
                Quiz Complete!
              </h1>
              
              <div className="text-6xl font-bold mb-2">
                <Badge variant={getScoreColor(results.score)} size="lg">
                  {results.score.toFixed(1)}%
                </Badge>
              </div>
              
              <p className="text-xl text-gray-400 mb-6">
                {getPerformanceMessage(results.score)}
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
              <div className="text-center p-4 bg-dark-700 rounded-lg">
                <div className="text-lg font-semibold text-gray-100">Score</div>
                <div className="text-2xl font-bold text-primary-400">
                  {results.score.toFixed(1)}%
                </div>
              </div>
              <div className="text-center p-4 bg-dark-700 rounded-lg">
                <div className="text-lg font-semibold text-gray-100">Questions</div>
                <div className="text-2xl font-bold text-primary-400">
                  {Object.keys(answers).length} / {module.quiz_questions.length}
                </div>
              </div>
            </div>

            {results.next_steps && (
              <div className="bg-blue-50 rounded-lg p-6 mb-8">
                <h3 className="font-semibold text-blue-900 mb-3">Next Steps:</h3>
                <p className="text-blue-800">{results.next_steps}</p>
              </div>
            )}

            {results.feedback && Object.keys(results.feedback).length > 0 && (
              <div className="mb-8">
                <h3 className="font-semibold text-gray-900 mb-4">Detailed Feedback:</h3>
                <div className="space-y-3">
                  {Object.entries(results.feedback).map(([questionIndex, feedback]) => (
                    <div key={questionIndex} className="p-4 bg-gray-50 rounded-lg">
                      <div className="flex items-center gap-2 mb-2">
                        <span className="font-medium">Question {parseInt(questionIndex) + 1}:</span>
                        {feedback.includes('Correct') ? (
                          <CheckCircle className="h-5 w-5 text-green-600" />
                        ) : (
                          <XCircle className="h-5 w-5 text-red-500" />
                        )}
                      </div>
                      <p className="text-gray-700">{feedback}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="flex gap-4 justify-center">
              <Button
                onClick={() => {
                  setSubmitted(false);
                  setResults(null);
                  setQuizStarted(false);
                  setAnswers({});
                  setCurrentQuestion(0);
                }}
                variant="outline"
                className="px-6"
              >
                <RotateCcw className="mr-2 h-4 w-4" />
                Retake Quiz
              </Button>
              <Button
                onClick={() => navigate('/dashboard')}
                className="px-6"
              >
                Back to Dashboard
              </Button>
            </div>
          </Card>
        </div>
      </div>
    );
  }

  // Quiz taking screen
  const question = module.quiz_questions[currentQuestion];
  const progress = ((currentQuestion + 1) / module.quiz_questions.length) * 100;

  return (
    <div className="min-h-screen bg-dark-800 py-8">
      <div className="max-w-4xl mx-auto px-4">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <h1 className="text-2xl font-bold text-gray-100">
              Quiz: {module.title}
            </h1>
            <div className="flex items-center gap-4">
              <Badge variant="primary">
                Question {currentQuestion + 1} of {module.quiz_questions.length}
              </Badge>
              {timeLeft > 0 && (
                <div className={`flex items-center gap-2 px-3 py-2 rounded-lg ${
                  timeLeft < 60 ? 'bg-red-100 text-red-700' : 'bg-blue-100 text-blue-700'
                }`}>
                  <Clock className="h-4 w-4" />
                  <span className="font-mono font-semibold">
                    {formatTime(timeLeft)}
                  </span>
                </div>
              )}
            </div>
          </div>
          
          {/* Progress bar */}
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-primary-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>

        <Card>
          <div className="mb-8">
            <h2 className="text-xl font-semibold text-gray-100 mb-6">
              {question.question}
            </h2>
            
            <div className="space-y-3">
              {question.options.map((option, index) => (
                <label
                  key={index}
                  className={`flex items-center p-4 rounded-lg border-2 cursor-pointer transition-all ${
                    answers[currentQuestion] === option
                      ? 'border-primary-500 bg-primary-900'
                      : 'border-dark-600 hover:border-dark-500 hover:bg-dark-700'
                  }`}
                >
                  <input
                    type="radio"
                    name={`question-${currentQuestion}`}
                    value={option}
                    checked={answers[currentQuestion] === option}
                    onChange={() => handleAnswerSelect(currentQuestion, option)}
                    className="sr-only"
                  />
                  <div className={`w-4 h-4 rounded-full border-2 mr-3 flex items-center justify-center ${
                    answers[currentQuestion] === option
                      ? 'border-primary-500 bg-primary-500'
                      : 'border-gray-300'
                  }`}>
                    {answers[currentQuestion] === option && (
                      <div className="w-2 h-2 rounded-full bg-white" />
                    )}
                  </div>
                  <span className="text-gray-700">{option}</span>
                </label>
              ))}
            </div>
          </div>

          {/* Navigation */}
          <div className="flex items-center justify-between">
            <Button
              variant="outline"
              onClick={prevQuestion}
              disabled={currentQuestion === 0}
            >
              <ArrowLeft className="mr-2 h-4 w-4" />
              Previous
            </Button>

            <div className="flex gap-2">
              {module.quiz_questions.map((_, index) => (
                <button
                  key={index}
                  onClick={() => setCurrentQuestion(index)}
                  className={`w-8 h-8 rounded-full text-sm font-medium transition-colors ${
                    index === currentQuestion
                      ? 'bg-primary-600 text-white'
                      : answers[index]
                      ? 'bg-green-100 text-green-700'
                      : 'bg-gray-200 text-gray-600 hover:bg-gray-300'
                  }`}
                >
                  {index + 1}
                </button>
              ))}
            </div>

            {currentQuestion === module.quiz_questions.length - 1 ? (
              <Button
                onClick={handleSubmit}
                disabled={Object.keys(answers).length === 0}
                loading={loading}
              >
                Submit Quiz
              </Button>
            ) : (
              <Button
                onClick={nextQuestion}
                disabled={currentQuestion === module.quiz_questions.length - 1}
              >
                Next
                <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            )}
          </div>
        </Card>
      </div>
    </div>
  );
};

export default QuizPage;
