import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';

const TestPage = () => {
  const { user, token } = useAuth();
  const [testResults, setTestResults] = useState({});
  const [loading, setLoading] = useState(false);

  const runTest = async (testName, testFn) => {
    setLoading(true);
    try {
      const result = await testFn();
      setTestResults(prev => ({
        ...prev,
        [testName]: { status: 'success', data: result }
      }));
    } catch (error) {
      setTestResults(prev => ({
        ...prev,
        [testName]: { status: 'error', error: error.message }
      }));
    }
    setLoading(false);
  };

  const testBackendHealth = async () => {
    const response = await fetch('/api/v1/health');
    return await response.json();
  };

  const testModuleGeneration = async () => {
    const response = await fetch('/api/v1/enhanced-modules/generate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        topic: 'JavaScript Basics',
        difficulty: 'Beginner'
      })
    });
    return await response.json();
  };

  const testChatMessage = async () => {
    const response = await fetch('/api/v1/enhanced-chat/message', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        message: 'What is JavaScript?',
        current_module: null
      })
    });
    return await response.json();
  };

  const testYouTubeSearch = async () => {
    const response = await fetch('/api/v1/enhanced-modules/youtube-search', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        topic: 'Python Programming'
      })
    });
    return await response.json();
  };

  const TestResult = ({ testName, result }) => (
    <div className={`test-result ${result?.status || 'pending'}`}>
      <h4>{testName}</h4>
      {result?.status === 'success' && (
        <div className="success">
          ✅ Success
          <pre>{JSON.stringify(result.data, null, 2)}</pre>
        </div>
      )}
      {result?.status === 'error' && (
        <div className="error">
          ❌ Error: {result.error}
        </div>
      )}
      {!result && <div className="pending">⏳ Pending</div>}
    </div>
  );

  if (!user) {
    return (
      <div className="test-page">
        <h1>Feature Testing</h1>
        <p>Please log in to test the enhanced features.</p>
      </div>
    );
  }

  return (
    <div className="test-page">
      <h1>🧪 Enhanced Features Testing</h1>
      <p>Test all the new features to ensure they're working correctly.</p>

      <div className="test-controls">
        <button 
          onClick={() => runTest('Backend Health', testBackendHealth)}
          disabled={loading}
        >
          Test Backend Health
        </button>
        
        <button 
          onClick={() => runTest('Module Generation', testModuleGeneration)}
          disabled={loading}
        >
          Test Module Generation
        </button>
        
        <button 
          onClick={() => runTest('Chat Message', testChatMessage)}
          disabled={loading}
        >
          Test Chat Message
        </button>
        
        <button 
          onClick={() => runTest('YouTube Search', testYouTubeSearch)}
          disabled={loading}
        >
          Test YouTube Search
        </button>
      </div>

      <div className="test-results">
        <TestResult testName="Backend Health" result={testResults['Backend Health']} />
        <TestResult testName="Module Generation" result={testResults['Module Generation']} />
        <TestResult testName="Chat Message" result={testResults['Chat Message']} />
        <TestResult testName="YouTube Search" result={testResults['YouTube Search']} />
      </div>

      <style jsx>{`
        .test-page {
          padding: 2rem;
          max-width: 1200px;
          margin: 0 auto;
          background: #1a1a2e;
          color: white;
          min-height: 100vh;
        }

        h1 {
          color: #60a5fa;
          margin-bottom: 1rem;
        }

        .test-controls {
          display: flex;
          gap: 1rem;
          margin: 2rem 0;
          flex-wrap: wrap;
        }

        .test-controls button {
          padding: 1rem 2rem;
          background: linear-gradient(45deg, #3b82f6, #8b5cf6);
          color: white;
          border: none;
          border-radius: 0.5rem;
          cursor: pointer;
          font-weight: 600;
          transition: transform 0.2s;
        }

        .test-controls button:hover:not(:disabled) {
          transform: translateY(-2px);
        }

        .test-controls button:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }

        .test-results {
          display: grid;
          gap: 1rem;
        }

        .test-result {
          background: rgba(255, 255, 255, 0.05);
          border-radius: 1rem;
          padding: 1.5rem;
          border: 1px solid rgba(255, 255, 255, 0.1);
        }

        .test-result h4 {
          margin: 0 0 1rem 0;
          color: #e2e8f0;
        }

        .success {
          color: #4ade80;
        }

        .error {
          color: #f87171;
        }

        .pending {
          color: #fbbf24;
        }

        pre {
          background: rgba(0, 0, 0, 0.3);
          padding: 1rem;
          border-radius: 0.5rem;
          overflow-x: auto;
          font-size: 0.8rem;
          margin-top: 0.5rem;
        }
      `}</style>
    </div>
  );
};

export default TestPage;
