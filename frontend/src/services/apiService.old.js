import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://127.0.0.1:8000';

// TEMPORARY: Mock data for testing frontend without backend
const MOCK_MODE = false;

const mockModules = [
  {
    id: '1',
    title: 'Introduction to React Hooks',
    content: 'React Hooks are functions that let you "hook into" React state and lifecycle features from function components. They were introduced in React 16.8 and have revolutionized how we write React components.\n\nThe most commonly used hooks are:\n- useState: For managing component state\n- useEffect: For side effects and lifecycle events\n- useContext: For consuming context values\n- useReducer: For complex state management\n\nHooks allow you to reuse stateful logic between components without changing your component hierarchy. This makes your code more readable and easier to test.',
    difficulty: 'medium',
    duration: 45,
    created_at: '2024-01-15T10:00:00Z',
    quiz_questions: [
      {
        question: 'What React version introduced Hooks?',
        options: ['React 16.6', 'React 16.8', 'React 17.0', 'React 18.0'],
        correct_answer: 'React 16.8'
      },
      {
        question: 'Which hook is used for managing component state?',
        options: ['useEffect', 'useState', 'useContext', 'useReducer'],
        correct_answer: 'useState'
      },
      {
        question: 'What is the main benefit of React Hooks?',
        options: ['Better performance', 'Reusable stateful logic', 'Smaller bundle size', 'TypeScript support'],
        correct_answer: 'Reusable stateful logic'
      }
    ],
    assignment_latex: true
  },
  {
    id: '2',
    title: 'JavaScript ES6 Features',
    content: 'ES6 (ECMAScript 2015) introduced many powerful features to JavaScript that modernized the language and made it more expressive and easier to work with.\n\nKey ES6 features include:\n- Arrow Functions: Shorter syntax for function expressions\n- Template Literals: String interpolation with backticks\n- Destructuring: Extract values from arrays and objects\n- Spread Operator: Expand iterables\n- Promises: Handle asynchronous operations\n- Classes: Object-oriented programming syntax\n- Modules: Import and export functionality\n\nThese features have become standard in modern JavaScript development and are essential for any JavaScript developer to master.',
    difficulty: 'easy',
    duration: 30,
    created_at: '2024-01-14T15:30:00Z',
    quiz_questions: [
      {
        question: 'What is the syntax for arrow functions?',
        options: ['() => {}', 'function() {}', '=> () {}', '() -> {}'],
        correct_answer: '() => {}'
      },
      {
        question: 'Which feature allows string interpolation?',
        options: ['Arrow functions', 'Template literals', 'Destructuring', 'Promises'],
        correct_answer: 'Template literals'
      }
    ],
    assignment_latex: true
  },
  {
    id: '3',
    title: 'Python Data Structures',
    content: 'Python provides several built-in data structures that are essential for effective programming. Understanding when and how to use each one is crucial for writing efficient Python code.\n\nMain Python data structures:\n- Lists: Ordered, mutable collections\n- Tuples: Ordered, immutable collections\n- Dictionaries: Key-value pairs, unordered (before Python 3.7)\n- Sets: Unordered collections of unique elements\n- Strings: Immutable sequences of characters\n\nEach data structure has its own methods and use cases. Lists are great for when you need to modify the collection, tuples for fixed data, dictionaries for lookups, and sets for unique collections.',
    difficulty: 'easy',
    duration: 25,
    created_at: '2024-01-13T09:15:00Z',
    quiz_questions: [
      {
        question: 'Which data structure is mutable in Python?',
        options: ['Tuple', 'String', 'List', 'Integer'],
        correct_answer: 'List'
      },
      {
        question: 'What data structure uses key-value pairs?',
        options: ['List', 'Tuple', 'Set', 'Dictionary'],
        correct_answer: 'Dictionary'
      },
      {
        question: 'Which data structure only contains unique elements?',
        options: ['List', 'Tuple', 'Set', 'Dictionary'],
        correct_answer: 'Set'
      }
    ],
    assignment_latex: false
  }
];

class ApiService {
  constructor() {
    this.api = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add auth token interceptor
    this.api.interceptors.request.use((config) => {
      const token = localStorage.getItem('authToken');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    // Add response interceptor for error handling
    this.api.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          localStorage.removeItem('authToken');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  // Auth methods
  async login(email, password) {
    if (MOCK_MODE) {
      return { access_token: 'mock-token' };
    }
    const response = await this.api.post('/api/v1/auth/login', {
      email: email,
      password: password,
    });
    const { access_token } = response.data;
    localStorage.setItem('authToken', access_token);
    return response.data;
  }

  async register(email, password, fullName) {
    if (MOCK_MODE) {
      return { message: 'User registered successfully' };
    }
    const response = await this.api.post('/api/v1/auth/register', {
      email: email,
      password: password,
    });
    return response.data;
  }

  async getCurrentUser() {
    if (MOCK_MODE) {
      return { 
        id: 'demo-user', 
        email: 'demo@example.com', 
        full_name: 'Demo User' 
      };
    }
    const response = await this.api.get('/api/v1/users/me');
    return response.data;
  }

  // Learning modules
  async generateModule(prompt, difficulty = 'medium', duration = 30) {
    if (MOCK_MODE) {
      const newModule = {
        id: Date.now().toString(),
        title: `Generated: ${prompt.substring(0, 50)}...`,
        content: `This is a generated module about: ${prompt}\n\nThis module covers the fundamentals and provides comprehensive learning materials to help you understand the topic thoroughly.`,
        difficulty,
        duration,
        created_at: new Date().toISOString(),
        quiz_questions: [
          {
            question: `What is the main concept of ${prompt.split(' ')[0]}?`,
            options: ['Option A', 'Option B', 'Option C', 'Option D'],
            correct_answer: 'Option A'
          }
        ],
        assignment_latex: true
      };
      mockModules.unshift(newModule);
      return newModule;
    }
    const user = await this.getCurrentUser();
    const response = await this.api.post('/api/v1/modules/generate', {
      user_id: user.id,
      prompt,
      difficulty,
      duration,
    });
    return response.data;
  }

  async getModule(moduleId) {
    if (MOCK_MODE) {
      return mockModules.find(m => m.id === moduleId) || mockModules[0];
    }
    const response = await this.api.get(`/api/v1/modules/${moduleId}`);
    return response.data;
  }

  async getUserModules() {
    if (MOCK_MODE) {
      return mockModules;
    }
    const response = await this.api.get('/api/v1/modules/');
    return response.data;
  }

  // Quiz methods
  async submitQuiz(moduleId, answers) {
    if (MOCK_MODE) {
      const correctCount = Object.values(answers).filter(answer => answer.includes('correct') || answer.includes('React 16.8') || answer.includes('useState')).length;
      const totalQuestions = Object.keys(answers).length;
      const score = (correctCount / totalQuestions) * 100;
      
      return {
        score: score,
        correct_answers: correctCount,
        total_questions: totalQuestions,
        feedback: score >= 80 ? 'Excellent work!' : score >= 60 ? 'Good job!' : 'Keep practicing!',
        next_steps: 'Continue with more advanced topics or review the material.'
      };
    }
    const user = await this.getCurrentUser();
    const response = await this.api.post('/api/v1/quizzes/submit', {
      user_id: user.id,
      module_id: moduleId,
      answers,
    });
    return response.data;
  }

  // Assignment methods
  async getAssignmentLatex(moduleId) {
    if (MOCK_MODE) {
      return { latex: '\\documentclass{article}\\begin{document}Sample Assignment\\end{document}' };
    }
    const response = await this.api.get(`/api/v1/assignments/${moduleId}/latex`);
    return response.data;
  }

  async getAssignmentPdf(moduleId) {
    if (MOCK_MODE) {
      // Create a mock PDF blob
      const pdfContent = '%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n>>\nendobj\n\nxref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n0000000074 00000 n \n0000000120 00000 n \ntrailer\n<<\n/Size 4\n/Root 1 0 R\n>>\nstartxref\n178\n%%EOF';
      return new Blob([pdfContent], { type: 'application/pdf' });
    }
    const response = await this.api.get(`/api/v1/assignments/${moduleId}/pdf`, {
      responseType: 'blob',
    });
    return response.data;
  }

  // User progress
  async getUserProgress() {
    if (MOCK_MODE) {
      return {
        total_modules: mockModules.length,
        completed_modules: Math.floor(mockModules.length * 0.6),
        total_quiz_attempts: 15,
        average_score: 85.5
      };
    }
    const response = await this.api.get('/api/v1/progress/');
    return response.data;
  }

  // Utility methods
  isAuthenticated() {
    if (MOCK_MODE) {
      return true; // Always authenticated in mock mode
    }
    return !!localStorage.getItem('authToken');
  }

  logout() {
    if (MOCK_MODE) {
      console.log('Mock logout - would redirect to home');
      return;
    }
    localStorage.removeItem('authToken');
    window.location.href = '/';
  }
}

// Singleton instance
const apiServiceInstance = new ApiService();
export default apiServiceInstance;
