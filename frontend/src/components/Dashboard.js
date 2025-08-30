import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  BookOpen, 
  Brain, 
  FileText, 
  Download, 
  Plus, 
  Clock, 
  CheckCircle, 
  TrendingUp,
  Search,
  PlayCircle,
  Trash2
} from 'lucide-react';
import { Button, Card, Badge, Input, LoadingSpinner } from './ui';
import apiService from '../services/apiService';
import { useAuth } from '../contexts/AuthContext';

const Dashboard = () => {
  const navigate = useNavigate();
  const { user, isAuthenticated } = useAuth();
  
  const [modules, setModules] = useState([]);
  const [filteredModules, setFilteredModules] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterDifficulty, setFilterDifficulty] = useState('all');
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [createLoading, setCreateLoading] = useState(false);
  const [newModuleForm, setNewModuleForm] = useState({
    prompt: '',
    difficulty: 'medium',
    duration: 30
  });

  const filterModules = () => {
    let filtered = modules;
    
    if (searchTerm) {
      filtered = filtered.filter(module => 
        module.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        module.content.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }
    
    if (filterDifficulty !== 'all') {
      filtered = filtered.filter(module => module.difficulty === filterDifficulty);
    }
    
    setFilteredModules(filtered);
  };

  useEffect(() => {
    if (isAuthenticated) {
      loadModules();
    }
  }, [isAuthenticated]);

  useEffect(() => {
    filterModules();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [modules, searchTerm, filterDifficulty]);

  const loadModules = async () => {
    try {
      setLoading(true);
      console.log('🔍 Loading modules...');
      console.log('🔑 Auth status:', isAuthenticated);
      console.log('👤 User:', user);
      
      const data = await apiService.getUserModules();
      console.log('📦 Received modules:', data);
      setModules(data);
    } catch (error) {
      console.error('❌ Error loading modules:', error);
      console.error('Error details:', error.response?.data);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateModule = async (e) => {
    e.preventDefault();
    try {
      setCreateLoading(true);
      console.log('🚀 Creating module with:', newModuleForm);
      
      const response = await apiService.generateModule(
        newModuleForm.prompt,
        newModuleForm.difficulty,
        newModuleForm.duration
      );
      
      console.log('📦 Module creation response:', response);
      
      // Check if response has the expected structure
      if (response.success && response.module) {
        // Add the new module to the list
        setModules(prev => [response.module, ...prev]);
        console.log('✅ Module added to list');
      } else {
        console.warn('⚠️ Unexpected response structure:', response);
        // Fallback: refresh the entire modules list
        await loadModules();
      }
      
      setShowCreateForm(false);
      setNewModuleForm({ prompt: '', difficulty: 'medium', duration: 30 });
    } catch (error) {
      console.error('❌ Error creating module:', error);
    } finally {
      setCreateLoading(false);
    }
  };

  const handleDownloadPDF = async (moduleId, title) => {
    try {
      const pdfBlob = await apiService.getAssignmentPdf(moduleId);
      const url = window.URL.createObjectURL(pdfBlob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${title.replace(/[^a-z0-9]/gi, '_').toLowerCase()}_assignment.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Error downloading PDF:', error);
    }
  };

  const handleDeleteModule = async (moduleId, title) => {
    if (window.confirm(`Are you sure you want to delete "${title}"? This action cannot be undone.`)) {
      try {
        await apiService.deleteModule(moduleId);
        // Remove the module from the local state
        setModules(prev => prev.filter(module => module.id !== moduleId));
        console.log('✅ Module deleted successfully');
      } catch (error) {
        console.error('Error deleting module:', error);
        alert('Failed to delete module. Please try again.');
      }
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

  const getModuleStats = () => {
    const total = modules.length;
    const completed = modules.filter(m => m.completed).length;
    const avgDuration = modules.reduce((sum, m) => sum + (m.duration || 30), 0) / total || 0;
    
    return { total, completed, avgDuration };
  };

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-dark-800">
        <Card className="max-w-md">
          <div className="text-center">
            <h2 className="text-2xl font-bold text-gray-100 mb-4">Please Log In</h2>
            <p className="text-gray-400 mb-6">Access your personalized dashboard by logging in.</p>
            <Button onClick={() => navigate('/login')}>Go to Login</Button>
          </div>
        </Card>
      </div>
    );
  }

  const stats = getModuleStats();

  return (
    <div className="min-h-screen bg-dark-800">
      {/* Header */}
      <div className="bg-dark-900 shadow-sm border-b border-dark-700">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-100">
                Welcome back, {user?.full_name || user?.email}!
              </h1>
              <p className="text-gray-600 mt-1">
                Continue your learning journey with AI-powered modules
              </p>
            </div>
            <div className="flex gap-3">
              <Button 
                onClick={() => setShowCreateForm(true)}
                className="flex items-center gap-2"
              >
                <Plus className="h-4 w-4" />
                Create Module
              </Button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card className="text-center">
            <div className="flex items-center justify-center w-12 h-12 bg-primary-800 rounded-lg mx-auto mb-4">
              <BookOpen className="h-6 w-6 text-primary-200" />
            </div>
            <div className="text-2xl font-bold text-gray-100">{stats.total}</div>
            <div className="text-sm text-gray-400">Total Modules</div>
          </Card>
          
          <Card className="text-center">
            <div className="flex items-center justify-center w-12 h-12 bg-green-800 rounded-lg mx-auto mb-4">
              <CheckCircle className="h-6 w-6 text-green-200" />
            </div>
            <div className="text-2xl font-bold text-gray-100">{stats.completed}</div>
            <div className="text-sm text-gray-400">Completed</div>
          </Card>
          
          <Card className="text-center">
            <div className="flex items-center justify-center w-12 h-12 bg-yellow-800 rounded-lg mx-auto mb-4">
              <Clock className="h-6 w-6 text-yellow-200" />
            </div>
            <div className="text-2xl font-bold text-gray-100">{stats.avgDuration.toFixed(0)}</div>
            <div className="text-sm text-gray-400">Avg Duration (min)</div>
          </Card>
          
          <Card className="text-center">
            <div className="flex items-center justify-center w-12 h-12 bg-purple-800 rounded-lg mx-auto mb-4">
              <TrendingUp className="h-6 w-6 text-purple-200" />
            </div>
            <div className="text-2xl font-bold text-gray-100">
              {stats.total > 0 ? Math.round((stats.completed / stats.total) * 100) : 0}%
            </div>
            <div className="text-sm text-gray-400">Progress</div>
          </Card>
        </div>

        {/* Search and Filter */}
        <div className="flex flex-col md:flex-row gap-4 mb-6">
          <div className="flex-1">
            <Input
              placeholder="Search modules..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
          </div>
          
          <select
            value={filterDifficulty}
            onChange={(e) => setFilterDifficulty(e.target.value)}
            className="px-4 py-2 border border-dark-600 bg-dark-700 text-gray-100 rounded-lg focus:ring-primary-500 focus:border-primary-500"
          >
            <option value="all">All Difficulties</option>
            <option value="easy">Easy</option>
            <option value="medium">Medium</option>
            <option value="hard">Hard</option>
          </select>
        </div>

        {/* Modules Grid */}
        {loading ? (
          <div className="flex justify-center py-12">
            <LoadingSpinner size="lg" />
          </div>
        ) : filteredModules.length === 0 ? (
          <Card className="text-center py-12">
            <BookOpen className="mx-auto h-12 w-12 text-gray-500 mb-4" />
            <h3 className="text-lg font-medium text-gray-100 mb-2">No modules found</h3>
            <p className="text-gray-400 mb-6">
              {modules.length === 0 
                ? "Create your first learning module to get started!"
                : "Try adjusting your search or filter criteria."}
            </p>
            {modules.length === 0 && (
              <Button onClick={() => setShowCreateForm(true)}>
                <Plus className="mr-2 h-4 w-4" />
                Create Your First Module
              </Button>
            )}
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredModules.map((module) => (
              <Card key={module.id} className="hover:shadow-md transition-shadow">
                <div className="flex items-start justify-between mb-4">
                  <Badge variant={getDifficultyColor(module.difficulty)}>
                    {module.difficulty || 'Medium'}
                  </Badge>
                  <div className="text-sm text-gray-400">
                    {module.duration || 30} min
                  </div>
                </div>
                
                <h3 className="text-lg font-semibold text-gray-100 mb-2">
                  {module.title}
                </h3>
                
                <p className="text-gray-400 text-sm mb-4 line-clamp-3">
                  {module.content?.substring(0, 150)}...
                </p>
                
                <div className="flex items-center gap-2 mb-4">
                  {module.quiz_questions && module.quiz_questions.length > 0 && (
                    <Badge variant="primary" size="sm">
                      <Brain className="h-3 w-3 mr-1" />
                      {module.quiz_questions.length} Questions
                    </Badge>
                  )}
                  {module.assignment_latex && (
                    <Badge variant="gray" size="sm">
                      <FileText className="h-3 w-3 mr-1" />
                      Assignment
                    </Badge>
                  )}
                </div>
                
                <div className="flex gap-2">
                  <Button
                    size="sm"
                    onClick={() => navigate(`/learn/${module.id}`)}
                    className="flex-1"
                  >
                    <PlayCircle className="mr-1 h-3 w-3" />
                    Learn
                  </Button>
                  
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => navigate(`/module/${module.id}`)}
                  >
                    <BookOpen className="mr-1 h-3 w-3" />
                    Details
                  </Button>
                  
                  {module.quiz_questions && module.quiz_questions.length > 0 && (
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => navigate(`/quiz/${module.id}`)}
                    >
                      <Brain className="mr-1 h-3 w-3" />
                      Quiz
                    </Button>
                  )}
                  
                  {module.assignment_latex && (
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => handleDownloadPDF(module.id, module.title)}
                    >
                      <Download className="h-3 w-3" />
                    </Button>
                  )}
                  
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => handleDeleteModule(module.id, module.title)}
                    className="text-red-400 hover:text-red-300 hover:bg-red-900/20"
                  >
                    <Trash2 className="h-3 w-3" />
                  </Button>
                </div>
              </Card>
            ))}
          </div>
        )}
      </div>

      {/* Create Module Modal */}
      {showCreateForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <Card className="w-full max-w-md">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-gray-100">Create New Module</h2>
              <button
                onClick={() => setShowCreateForm(false)}
                className="text-gray-500 hover:text-gray-300"
              >
                ×
              </button>
            </div>
            
            <form onSubmit={handleCreateModule} className="space-y-4">
              <Input
                label="What do you want to learn?"
                placeholder="e.g., Python functions, React hooks, Machine learning basics..."
                value={newModuleForm.prompt}
                onChange={(e) => setNewModuleForm(prev => ({ ...prev, prompt: e.target.value }))}
                required
              />
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-1">
                    Difficulty
                  </label>
                  <select
                    value={newModuleForm.difficulty}
                    onChange={(e) => setNewModuleForm(prev => ({ ...prev, difficulty: e.target.value }))}
                    className="w-full px-3 py-2 border border-dark-600 bg-dark-700 text-gray-100 rounded-md focus:ring-primary-500 focus:border-primary-500"
                  >
                    <option value="easy">Easy</option>
                    <option value="medium">Medium</option>
                    <option value="hard">Hard</option>
                  </select>
                </div>
                
                <Input
                  label="Duration (min)"
                  type="number"
                  min="15"
                  max="180"
                  value={newModuleForm.duration}
                  onChange={(e) => setNewModuleForm(prev => ({ ...prev, duration: parseInt(e.target.value) }))}
                />
              </div>
              
              <div className="flex gap-3 pt-4">
                <Button
                  type="submit"
                  loading={createLoading}
                  className="flex-1"
                >
                  Create Module
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => setShowCreateForm(false)}
                >
                  Cancel
                </Button>
              </div>
            </form>
          </Card>
        </div>
      )}
    </div>
  );
};

export default Dashboard;
