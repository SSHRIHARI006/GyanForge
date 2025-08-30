import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  Play, 
  Pause, 
  MessageCircle, 
  Send, 
  BookOpen, 
  Video, 
  ArrowLeft,
  Bot,
  User,
  CheckCircle,
  XCircle,
  Lightbulb,
  Download,
  FileText
} from 'lucide-react';
import { Button, Card, Badge, LoadingSpinner } from './ui';
import apiService from '../services/apiService';
import { useAuth } from '../contexts/AuthContext';

const LearningPage = () => {
  const { moduleId } = useParams();
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const chatEndRef = useRef(null);
  
  const [module, setModule] = useState(null);
  const [loading, setLoading] = useState(true);
  const [currentSection, setCurrentSection] = useState('video'); // video, content, quiz, chat
  const [chatMessages, setChatMessages] = useState([
    {
      type: 'bot',
      message: "Hi! I'm your AI learning assistant. I'll help you understand this topic better. Ready to start learning?",
      timestamp: Date.now()
    }
  ]);
  const [currentInput, setCurrentInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [quizMode, setQuizMode] = useState(false);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [selectedAnswer, setSelectedAnswer] = useState('');
  const [showResult, setShowResult] = useState(false);
  
  // Quiz state
  const [quizQuestions, setQuizQuestions] = useState([]);
  const [quizAnswers, setQuizAnswers] = useState({});
  const [quizCompleted, setQuizCompleted] = useState(false);
  const [quizScore, setQuizScore] = useState(null);

  // Get video ID from module's video_links (from backend API)
  const getVideoIdFromModule = (module) => {
    if (!module || !module.video_links) return 'LlvBzyy-558'; // Fallback
    
    try {
      const videoLinks = typeof module.video_links === 'string' 
        ? JSON.parse(module.video_links) 
        : module.video_links;
      
      if (Array.isArray(videoLinks) && videoLinks.length > 0) {
        const firstVideo = videoLinks[0];
        if (firstVideo.url) {
          // Extract video ID from YouTube URL
          const match = firstVideo.url.match(/(?:youtu\.be\/|youtube\.com\/(?:embed\/|v\/|watch\?v=|watch\?.+&v=))([^&?]+)/);
          if (match && match[1]) {
            return match[1];
          }
        }
      }
    } catch (error) {
      console.error('Error parsing video links:', error);
    }
    
    return 'LlvBzyy-558'; // Fallback if no valid video found
  };

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }
    loadModule();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [moduleId, isAuthenticated]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatMessages]);

  const loadModule = async () => {
    try {
      setLoading(true);
      const moduleData = await apiService.getModule(moduleId);
      setModule(moduleData);
      
      // Extract quiz questions from module
      if (moduleData.quiz_data) {
        try {
          const quizData = typeof moduleData.quiz_data === 'string' 
            ? JSON.parse(moduleData.quiz_data) 
            : moduleData.quiz_data;
          setQuizQuestions(quizData.questions || []);
        } catch (error) {
          console.error('Error parsing quiz data:', error);
          setQuizQuestions([]);
        }
      }
    } catch (error) {
      console.error('Error loading module:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSendMessage = async () => {
    if (!currentInput.trim()) return;

    const userMessage = {
      type: 'user',
      message: currentInput,
      timestamp: Date.now()
    };

    setChatMessages(prev => [...prev, userMessage]);
    const messageText = currentInput;
    setCurrentInput('');
    setIsTyping(true);

    try {
      // Call the enhanced chat API
      const response = await apiService.sendChatMessage(messageText, moduleId);
      
      const botMessage = {
        type: 'bot',
        message: response.response || "I'm here to help you learn! Feel free to ask any questions about this topic.",
        timestamp: Date.now()
      };

      setChatMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('Chat error:', error);
      
      // Fallback response if API fails
      const fallbackResponses = [
        "That's a great question about this topic! Can you tell me more about what specifically you'd like to understand?",
        "I can see you're thinking deeply about this subject. What aspect would you like me to explain further?",
        "Excellent question! Let me help you understand this concept better.",
        "That's an important point to clarify. What would help make this clearer for you?",
        "Good observation! This is definitely worth exploring further."
      ];

      const botMessage = {
        type: 'bot',
        message: fallbackResponses[Math.floor(Math.random() * fallbackResponses.length)],
        timestamp: Date.now()
      };

      setChatMessages(prev => [...prev, botMessage]);
    } finally {
      setIsTyping(false);
    }
  };

  const startQuizMode = () => {
    setQuizMode(true);
    setCurrentQuestion(0);
    const introMessage = {
      type: 'bot',
      message: "Great! Let's test your knowledge. I'll ask you questions one by one. Ready for the first question?",
      timestamp: Date.now()
    };
    setChatMessages(prev => [...prev, introMessage]);
    
    setTimeout(() => {
      showNextQuestion();
    }, 1000);
  };

  const showNextQuestion = () => {
    if (!module?.quiz_questions || currentQuestion >= module.quiz_questions.length) {
      const completeMessage = {
        type: 'bot',
        message: "🎉 Congratulations! You've completed all the questions. Great work on your learning journey!",
        timestamp: Date.now()
      };
      setChatMessages(prev => [...prev, completeMessage]);
      setQuizMode(false);
      return;
    }

    const question = module.quiz_questions[currentQuestion];
    const questionMessage = {
      type: 'bot',
      message: `Question ${currentQuestion + 1}: ${question.question}`,
      options: question.options,
      questionId: currentQuestion,
      timestamp: Date.now()
    };
    setChatMessages(prev => [...prev, questionMessage]);
  };

  const handleAnswerSelect = (answer, questionId) => {
    // Store the answer for submission
    setQuizAnswers(prev => ({
      ...prev,
      [questionId]: answer
    }));
    
    setSelectedAnswer(answer);
    
    // If we're in the old interactive chat-quiz mode, continue with chat responses
    if (quizMode && module.quiz_questions) {
      const question = module.quiz_questions[questionId];
      const isCorrect = answer === question.correct_answer;
      
      const userAnswer = {
        type: 'user',
        message: answer,
        timestamp: Date.now()
      };

      const feedback = {
        type: 'bot',
        message: isCorrect 
          ? "✅ Correct! Well done!" 
          : `❌ Not quite. The correct answer is: ${question.correct_answer}`,
        timestamp: Date.now() + 1
      };

      setChatMessages(prev => [...prev, userAnswer, feedback]);
      
      setTimeout(() => {
        setCurrentQuestion(prev => prev + 1);
        setTimeout(showNextQuestion, 500);
      }, 2000);
    }
  };

  const handleDownloadPDF = async () => {
    try {
      await apiService.downloadModulePDF(moduleId);
    } catch (error) {
      console.error('Error downloading PDF:', error);
      // You could add a toast notification here
      alert('Failed to download PDF. Please try again.');
    }
  };

  const handleQuizSubmit = async () => {
    try {
      const result = await apiService.submitQuiz(moduleId, quizAnswers);
      setQuizScore(result);
      setQuizCompleted(true);
    } catch (error) {
      console.error('Error submitting quiz:', error);
      alert('Failed to submit quiz. Please try again.');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-dark-800">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (!module) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-dark-800">
        <Card className="max-w-md">
          <div className="text-center">
            <h2 className="text-2xl font-bold text-gray-100 mb-4">Module Not Found</h2>
            <Button onClick={() => navigate('/dashboard')}>Back to Dashboard</Button>
          </div>
        </Card>
      </div>
    );
  }

  const videoId = getVideoIdFromModule(module);

  return (
    <div className="min-h-screen bg-dark-800">
      {/* Header */}
      <div className="bg-dark-900 border-b border-dark-700 px-4 py-3">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Button 
              variant="ghost" 
              size="sm"
              onClick={() => navigate('/dashboard')}
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back
            </Button>
            <div>
              <h1 className="text-lg font-bold text-gray-100">{module.title}</h1>
              <div className="flex items-center gap-2 mt-1">
                <Badge variant="primary" size="sm">{module.difficulty}</Badge>
                <span className="text-gray-400 text-sm">{module.duration} min</span>
              </div>
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            <Button
              variant={currentSection === 'video' ? 'primary' : 'ghost'}
              size="sm"
              onClick={() => setCurrentSection('video')}
            >
              <Video className="h-4 w-4 mr-1" />
              Video
            </Button>
            <Button
              variant={currentSection === 'content' ? 'primary' : 'ghost'}
              size="sm"
              onClick={() => setCurrentSection('content')}
            >
              <BookOpen className="h-4 w-4 mr-1" />
              Content
            </Button>
            <Button
              variant={currentSection === 'quiz' ? 'primary' : 'ghost'}
              size="sm"
              onClick={() => setCurrentSection('quiz')}
            >
              <FileText className="h-4 w-4 mr-1" />
              Quiz
            </Button>
            <Button
              variant={currentSection === 'chat' ? 'primary' : 'ghost'}
              size="sm"
              onClick={() => setCurrentSection('chat')}
            >
              <MessageCircle className="h-4 w-4 mr-1" />
              AI Chat
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={handleDownloadPDF}
              className="text-blue-400 hover:text-blue-300"
            >
              <Download className="h-4 w-4 mr-1" />
              Download PDF
            </Button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto p-4">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Learning Content */}
          <div className="lg:col-span-2">
            {currentSection === 'video' && (
              <Card className="mb-4">
                <div className="aspect-video">
                  <iframe
                    width="100%"
                    height="100%"
                    src={`https://www.youtube.com/embed/${videoId}`}
                    title="Learning Video"
                    frameBorder="0"
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                    allowFullScreen
                    className="rounded-lg"
                  ></iframe>
                </div>
                <div className="p-4">
                  <h3 className="text-lg font-semibold text-gray-100 mb-2">
                    Recommended Video: {module.title}
                  </h3>
                  <p className="text-gray-400 text-sm">
                    This video provides visual explanations and examples to complement your learning.
                  </p>
                </div>
              </Card>
            )}

            {currentSection === 'content' && (
              <Card>
                <div className="p-6">
                  <h2 className="text-2xl font-bold text-gray-100 mb-4">
                    <BookOpen className="inline h-6 w-6 mr-2" />
                    Learning Material
                  </h2>
                  <div className="prose prose-invert max-w-none">
                    <div className="text-gray-300 leading-relaxed whitespace-pre-wrap">
                      {(() => {
                        try {
                          // Try to parse as JSON first
                          const contentObj = JSON.parse(module.content);
                          return contentObj.content || module.content;
                        } catch {
                          // If not JSON, display as-is
                          return module.content;
                        }
                      })()}
                    </div>
                  </div>
                </div>
              </Card>
            )}

            {currentSection === 'quiz' && (
              <Card>
                <div className="p-6">
                  <h2 className="text-2xl font-bold text-gray-100 mb-4 flex items-center">
                    <FileText className="h-6 w-6 mr-2 text-primary-400" />
                    Knowledge Quiz
                  </h2>
                  
                  {!quizCompleted && quizQuestions.length > 0 ? (
                    <div className="space-y-6">
                      {quizQuestions.map((question, index) => (
                        <div key={index} className="border border-dark-600 rounded-lg p-4">
                          <h3 className="text-lg font-semibold text-gray-100 mb-3">
                            Question {index + 1}: {question.question}
                          </h3>
                          
                          <div className="space-y-2">
                            {question.type === 'multiple_choice' && question.options ? (
                              question.options.map((option, optIndex) => (
                                <label key={optIndex} className="flex items-center space-x-3 cursor-pointer p-2 hover:bg-dark-700 rounded">
                                  <input
                                    type="radio"
                                    name={`question_${index}`}
                                    value={option}
                                    checked={quizAnswers[index] === option}
                                    onChange={() => handleAnswerSelect(option, index)}
                                    className="text-primary-500"
                                  />
                                  <span className="text-gray-300">{option}</span>
                                </label>
                              ))
                            ) : question.type === 'true_false' ? (
                              <>
                                <label className="flex items-center space-x-3 cursor-pointer p-2 hover:bg-dark-700 rounded">
                                  <input
                                    type="radio"
                                    name={`question_${index}`}
                                    value="true"
                                    checked={quizAnswers[index] === "true"}
                                    onChange={() => handleAnswerSelect("true", index)}
                                    className="text-primary-500"
                                  />
                                  <span className="text-gray-300">True</span>
                                </label>
                                <label className="flex items-center space-x-3 cursor-pointer p-2 hover:bg-dark-700 rounded">
                                  <input
                                    type="radio"
                                    name={`question_${index}`}
                                    value="false"
                                    checked={quizAnswers[index] === "false"}
                                    onChange={() => handleAnswerSelect("false", index)}
                                    className="text-primary-500"
                                  />
                                  <span className="text-gray-300">False</span>
                                </label>
                              </>
                            ) : null}
                          </div>
                        </div>
                      ))}
                      
                      <Button 
                        onClick={handleQuizSubmit}
                        disabled={Object.keys(quizAnswers).length !== quizQuestions.length}
                        className="w-full mt-6"
                      >
                        Submit Quiz
                      </Button>
                    </div>
                  ) : quizCompleted && quizScore ? (
                    <div className="text-center space-y-4">
                      <div className="text-4xl font-bold text-primary-400">
                        {quizScore.score?.toFixed(1)}%
                      </div>
                      <p className="text-gray-300">
                        You got {quizScore.correct_answers} out of {quizScore.total_questions} questions correct!
                      </p>
                      
                      {quizScore.feedback && (
                        <div className="space-y-3 mt-6">
                          <h3 className="text-lg font-semibold text-gray-100">Detailed Feedback:</h3>
                          {quizScore.feedback.map((item, index) => (
                            <div key={index} className="text-left border border-dark-600 rounded-lg p-4">
                              <p className="font-medium text-gray-100">{item.question}</p>
                              <p className="text-sm text-gray-400 mt-1">
                                Your answer: <span className={item.is_correct ? 'text-green-400' : 'text-red-400'}>
                                  {item.user_answer}
                                </span>
                              </p>
                              {!item.is_correct && (
                                <p className="text-sm text-gray-400">
                                  Correct answer: <span className="text-green-400">{item.correct_answer}</span>
                                </p>
                              )}
                              {item.explanation && (
                                <p className="text-sm text-gray-300 mt-2">{item.explanation}</p>
                              )}
                            </div>
                          ))}
                        </div>
                      )}
                      
                      <Button 
                        onClick={() => {
                          setQuizCompleted(false);
                          setQuizAnswers({});
                          setQuizScore(null);
                        }}
                        variant="ghost"
                        className="mt-4"
                      >
                        Retake Quiz
                      </Button>
                    </div>
                  ) : (
                    <div className="text-center text-gray-400">
                      <p>No quiz questions available for this module.</p>
                    </div>
                  )}
                </div>
              </Card>
            )}

            {currentSection === 'chat' && (
              <Card className="h-[600px] flex flex-col">
                <div className="p-4 border-b border-dark-700">
                  <h2 className="text-lg font-semibold text-gray-100 flex items-center">
                    <Bot className="h-5 w-5 mr-2 text-primary-400" />
                    AI Learning Assistant
                  </h2>
                  <p className="text-gray-400 text-sm">Ask questions or start a quiz to test your knowledge</p>
                </div>
                
                {/* Chat Messages */}
                <div className="flex-1 overflow-y-auto p-4 space-y-4">
                  {chatMessages.map((msg, index) => (
                    <div key={index} className={`flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}>
                      <div className={`flex items-start gap-2 max-w-xs lg:max-w-sm ${msg.type === 'user' ? 'flex-row-reverse' : ''}`}>
                        <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                          msg.type === 'user' ? 'bg-primary-600' : 'bg-green-600'
                        }`}>
                          {msg.type === 'user' ? (
                            <User className="h-4 w-4 text-white" />
                          ) : (
                            <Bot className="h-4 w-4 text-white" />
                          )}
                        </div>
                        <div className={`rounded-lg p-3 ${
                          msg.type === 'user' 
                            ? 'bg-primary-600 text-white' 
                            : 'bg-dark-700 text-gray-100'
                        }`}>
                          <p className="text-sm">{msg.message}</p>
                          {msg.options && (
                            <div className="mt-3 space-y-2">
                              {msg.options.map((option, optIndex) => (
                                <button
                                  key={optIndex}
                                  onClick={() => handleAnswerSelect(option, msg.questionId)}
                                  className="block w-full text-left p-2 rounded bg-dark-600 hover:bg-dark-500 text-gray-200 text-sm transition-colors"
                                >
                                  {option}
                                </button>
                              ))}
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                  
                  {isTyping && (
                    <div className="flex justify-start">
                      <div className="flex items-start gap-2">
                        <div className="w-8 h-8 rounded-full bg-green-600 flex items-center justify-center">
                          <Bot className="h-4 w-4 text-white" />
                        </div>
                        <div className="bg-dark-700 rounded-lg p-3">
                          <div className="flex space-x-1">
                            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                  <div ref={chatEndRef} />
                </div>

                {/* Chat Input */}
                <div className="p-4 border-t border-dark-700">
                  <div className="flex gap-2 mb-2">
                    <Button 
                      size="sm" 
                      variant="outline"
                      onClick={startQuizMode}
                      disabled={quizMode}
                    >
                      Start Quiz
                    </Button>
                    <Button 
                      size="sm" 
                      variant="outline"
                      onClick={() => {
                        const helpMessage = {
                          type: 'bot',
                          message: "I can help you understand this topic better! Ask me about key concepts, examples, or request practice questions.",
                          timestamp: Date.now()
                        };
                        setChatMessages(prev => [...prev, helpMessage]);
                      }}
                    >
                      <Lightbulb className="h-4 w-4 mr-1" />
                      Help
                    </Button>
                  </div>
                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={currentInput}
                      onChange={(e) => setCurrentInput(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                      placeholder="Ask a question or type your thoughts..."
                      className="flex-1 px-3 py-2 bg-dark-700 border border-dark-600 rounded-md text-gray-100 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500"
                      disabled={quizMode}
                    />
                    <Button onClick={handleSendMessage} disabled={!currentInput.trim() || quizMode}>
                      <Send className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </Card>
            )}
          </div>

          {/* Progress Sidebar */}
          <div className="space-y-4">
            <Card>
              <div className="p-4">
                <h3 className="text-lg font-semibold text-gray-100 mb-3">Learning Progress</h3>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-gray-400 text-sm">Video</span>
                    <div className="flex items-center">
                      {currentSection === 'video' ? (
                        <Play className="h-4 w-4 text-green-400" />
                      ) : (
                        <CheckCircle className="h-4 w-4 text-green-400" />
                      )}
                    </div>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-gray-400 text-sm">Content</span>
                    <div className="flex items-center">
                      {currentSection === 'content' ? (
                        <BookOpen className="h-4 w-4 text-blue-400" />
                      ) : (
                        <CheckCircle className="h-4 w-4 text-green-400" />
                      )}
                    </div>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-gray-400 text-sm">AI Practice</span>
                    <div className="flex items-center">
                      {currentSection === 'quiz' ? (
                        <MessageCircle className="h-4 w-4 text-purple-400" />
                      ) : (
                        <CheckCircle className="h-4 w-4 text-green-400" />
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </Card>

            <Card>
              <div className="p-4">
                <h3 className="text-lg font-semibold text-gray-100 mb-3">Quick Tips</h3>
                <div className="space-y-2 text-sm text-gray-400">
                  <p>💡 Watch the video first for visual learning</p>
                  <p>📖 Read the content for detailed understanding</p>
                  <p>🤖 Use AI chat to clarify doubts and practice</p>
                  <p>❓ Ask specific questions for better help</p>
                </div>
              </div>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LearningPage;
