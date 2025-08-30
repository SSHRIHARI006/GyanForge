import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../contexts/AuthContext';
import './EnhancedChatBox.css';

const EnhancedChatBox = () => {
  const { user, token } = useAuth();
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [suggestions, setSuggestions] = useState([]);
  const [learningInsights, setLearningInsights] = useState([]);
  const [recommendedActions, setRecommendedActions] = useState([]);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Add welcome message
    setMessages([{
      id: 1,
      text: "Hi! I'm your AI learning assistant. I can help you with your studies, answer questions about your modules, and provide personalized learning guidance. What would you like to know?",
      isBot: true,
      timestamp: new Date().toLocaleTimeString()
    }]);
    
    // Set initial suggestions
    setSuggestions([
      "What should I learn next?",
      "Explain a concept from my current module",
      "Give me study tips",
      "How can I improve my understanding?"
    ]);
  }, []);

  const sendMessage = async (messageText = inputMessage) => {
    if (!messageText.trim()) return;

    // Add user message
    const userMessage = {
      id: Date.now(),
      text: messageText,
      isBot: false,
      timestamp: new Date().toLocaleTimeString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await fetch('/api/v1/enhanced-chat/message', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          message: messageText,
          current_module: null // Could be set based on current context
        })
      });

      const data = await response.json();
      
      if (data.success) {
        // Add bot response
        const botMessage = {
          id: Date.now() + 1,
          text: data.response,
          isBot: true,
          timestamp: new Date().toLocaleTimeString(),
          contextUsed: data.context_used
        };

        setMessages(prev => [...prev, botMessage]);
        
        // Update suggestions and insights
        if (data.suggestions) setSuggestions(data.suggestions);
        if (data.learning_insights) setLearningInsights(data.learning_insights);
        if (data.recommended_actions) setRecommendedActions(data.recommended_actions);
      } else {
        throw new Error('Failed to get response');
      }
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = {
        id: Date.now() + 1,
        text: "I'm sorry, I'm having trouble responding right now. Please try again in a moment.",
        isBot: true,
        isError: true,
        timestamp: new Date().toLocaleTimeString()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div style={{ 
      display: 'flex', 
      height: '600px', 
      border: '1px solid #ddd', 
      borderRadius: '10px',
      backgroundColor: 'white'
    }}>
      {/* Main Chat Area */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        {/* Header */}
        <div style={{ 
          padding: '15px', 
          borderBottom: '1px solid #eee',
          backgroundColor: '#f8f9fa',
          borderRadius: '10px 10px 0 0'
        }}>
          <h3 style={{ margin: 0 }}>🤖 AI Learning Assistant</h3>
        </div>

        {/* Messages Area */}
        <div style={{ 
          flex: 1, 
          padding: '20px', 
          overflowY: 'auto',
          backgroundColor: '#fafafa'
        }}>
          {messages.map((message) => (
            <div
              key={message.id}
              style={{
                display: 'flex',
                justifyContent: message.isBot ? 'flex-start' : 'flex-end',
                marginBottom: '15px'
              }}
            >
              <div
                style={{
                  maxWidth: '70%',
                  padding: '12px 16px',
                  borderRadius: '18px',
                  backgroundColor: message.isBot 
                    ? (message.isError ? '#f8d7da' : '#e3f2fd')
                    : '#007bff',
                  color: message.isBot 
                    ? (message.isError ? '#721c24' : '#1565c0')
                    : 'white',
                  position: 'relative'
                }}
              >
                <div style={{ marginBottom: '5px' }}>
                  {message.text}
                </div>
                <div style={{ 
                  fontSize: '11px', 
                  opacity: 0.7,
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center'
                }}>
                  <span>{message.timestamp}</span>
                  {message.contextUsed && (
                    <span style={{ 
                      backgroundColor: 'rgba(255,255,255,0.3)', 
                      padding: '2px 6px', 
                      borderRadius: '10px',
                      fontSize: '10px'
                    }}>
                      Context-Aware
                    </span>
                  )}
                </div>
              </div>
            </div>
          ))}
          
          {isLoading && (
            <div style={{ display: 'flex', justifyContent: 'flex-start', marginBottom: '15px' }}>
              <div style={{
                padding: '12px 16px',
                borderRadius: '18px',
                backgroundColor: '#e3f2fd',
                color: '#1565c0'
              }}>
                Thinking...
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div style={{ padding: '15px', borderTop: '1px solid #eee' }}>
          {/* Quick Suggestions */}
          {suggestions.length > 0 && (
            <div style={{ marginBottom: '10px' }}>
              <div style={{ fontSize: '12px', color: '#666', marginBottom: '5px' }}>Quick suggestions:</div>
              <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                {suggestions.slice(0, 3).map((suggestion, index) => (
                  <button
                    key={index}
                    onClick={() => sendMessage(suggestion)}
                    style={{
                      backgroundColor: '#f1f3f4',
                      border: '1px solid #dadce0',
                      borderRadius: '16px',
                      padding: '6px 12px',
                      fontSize: '12px',
                      cursor: 'pointer',
                      color: '#3c4043'
                    }}
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
            </div>
          )}

          <div style={{ display: 'flex', gap: '10px' }}>
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask me anything about your learning..."
              style={{
                flex: 1,
                padding: '12px',
                border: '1px solid #ddd',
                borderRadius: '25px',
                outline: 'none',
                fontSize: '14px'
              }}
              disabled={isLoading}
            />
            <button
              onClick={() => sendMessage()}
              disabled={isLoading || !inputMessage.trim()}
              style={{
                backgroundColor: '#007bff',
                color: 'white',
                border: 'none',
                borderRadius: '50%',
                width: '45px',
                height: '45px',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                opacity: (isLoading || !inputMessage.trim()) ? 0.5 : 1
              }}
            >
              ➤
            </button>
          </div>
        </div>
      </div>

      {/* Sidebar with Insights and Actions */}
      <div style={{ 
        width: '300px', 
        borderLeft: '1px solid #eee',
        backgroundColor: '#f8f9fa',
        display: 'flex',
        flexDirection: 'column'
      }}>
        {/* Learning Insights */}
        {learningInsights.length > 0 && (
          <div style={{ padding: '15px', borderBottom: '1px solid #eee' }}>
            <h4 style={{ margin: '0 0 10px 0', fontSize: '14px', color: '#495057' }}>💡 Learning Insights</h4>
            {learningInsights.map((insight, index) => (
              <div key={index} style={{ 
                backgroundColor: '#e8f5e8',
                padding: '8px 12px',
                borderRadius: '8px',
                marginBottom: '8px',
                fontSize: '13px',
                color: '#155724'
              }}>
                {insight}
              </div>
            ))}
          </div>
        )}

        {/* Recommended Actions */}
        {recommendedActions.length > 0 && (
          <div style={{ padding: '15px', borderBottom: '1px solid #eee' }}>
            <h4 style={{ margin: '0 0 10px 0', fontSize: '14px', color: '#495057' }}>🎯 Recommended Actions</h4>
            {recommendedActions.map((action, index) => (
              <div key={index} style={{ 
                backgroundColor: '#fff3cd',
                padding: '8px 12px',
                borderRadius: '8px',
                marginBottom: '8px',
                fontSize: '13px',
                color: '#856404',
                cursor: 'pointer',
                border: '1px solid #ffeaa7'
              }}>
                {action}
              </div>
            ))}
          </div>
        )}

        {/* Chat Tips */}
        <div style={{ padding: '15px', flex: 1 }}>
          <h4 style={{ margin: '0 0 10px 0', fontSize: '14px', color: '#495057' }}>💬 Chat Tips</h4>
          <ul style={{ margin: 0, paddingLeft: '15px', fontSize: '12px', color: '#6c757d' }}>
            <li style={{ marginBottom: '5px' }}>Ask specific questions about your modules</li>
            <li style={{ marginBottom: '5px' }}>Request explanations of difficult concepts</li>
            <li style={{ marginBottom: '5px' }}>Get personalized study recommendations</li>
            <li style={{ marginBottom: '5px' }}>Ask for help with assignments</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default EnhancedChatBox;
