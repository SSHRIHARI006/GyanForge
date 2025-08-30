import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import './EnhancedModules.css';

const EnhancedModules = () => {
  const { user, token } = useAuth();
  const [modules, setModules] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [selectedModule, setSelectedModule] = useState(null);
  const [newModuleData, setNewModuleData] = useState({
    topic: '',
    difficulty: 'Beginner'
  });
  const [showCreateForm, setShowCreateForm] = useState(false);

  // Fetch user modules
  const fetchModules = async () => {
    if (!token) return;
    
    try {
      const response = await fetch('/api/v1/modules', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      const data = await response.json();
      if (response.ok) {
        setModules(data);
      } else {
        setError('Failed to fetch modules');
      }
    } catch (error) {
      console.error('Error fetching modules:', error);
      setError('Failed to fetch modules');
    }
  };

  // Create new comprehensive module
  const createModule = async () => {
    if (!newModuleData.topic.trim()) {
      setError('Please enter a topic');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await fetch('/api/v1/enhanced-modules/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(newModuleData)
      });

      if (response.ok) {
        const data = await response.json();
        setModules([...modules, data]);
        setNewModuleData({ topic: '', difficulty: 'Beginner' });
        setShowCreateForm(false);
        alert('Module created successfully!');
      } else {
        setError('Failed to create module');
      }
    } catch (error) {
      console.error('Error creating module:', error);
      setError('Failed to create module');
    } finally {
      setLoading(false);
    }
  };

  // Download notes as PDF
  const downloadNotes = async (moduleId, moduleTitle) => {
    try {
      const response = await fetch(`/api/v1/enhanced-modules/${moduleId}/download`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `${moduleTitle.replace(/[^a-z0-9]/gi, '_').toLowerCase()}.pdf`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
      } else {
        alert('Failed to generate notes PDF');
      }
    } catch (error) {
      console.error('Error downloading notes:', error);
      alert('Failed to download notes');
    }
  };

  // Download assignments as PDF
  const downloadAssignments = async (moduleId, moduleTitle) => {
    try {
      const response = await fetch(`/api/v1/enhanced-modules/${moduleId}/download`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `${moduleTitle.replace(/[^a-z0-9]/gi, '_').toLowerCase()}_assignment.pdf`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      } else {
        alert('Failed to generate assignments PDF');
      }
    } catch (error) {
      console.error('Error downloading assignments:', error);
      alert('Failed to download assignments');
    }
  };

  useEffect(() => {
    fetchModules();
  }, []);

  const ModuleCard = ({ module }) => (
    <div className="module-card">
      <div className="module-header">
        <h3>{module.title || module.topic}</h3>
        <span className={`difficulty-badge ${module.difficulty?.toLowerCase()}`}>
          {module.difficulty}
        </span>
      </div>
      
      <div className="module-content">
        {/* Learning objectives */}
        {module.learning_objectives && (
          <div className="section">
            <h4>Learning Objectives</h4>
            <ul>
              {module.learning_objectives.map((objective, index) => (
                <li key={index}>{objective}</li>
              ))}
            </ul>
          </div>
        )}

        {/* Recommended Videos */}
        {module.recommended_videos && module.recommended_videos.length > 0 && (
          <div className="section">
            <h4>Recommended Videos</h4>
            <div className="videos-grid">
              {module.recommended_videos.slice(0, 3).map((video, index) => (
                <div key={index} className="video-card">
                  <img src={video.thumbnail} alt={video.title} />
                  <div className="video-info">
                    <h5>{video.title}</h5>
                    <p>{video.channel}</p>
                    <p>{video.duration} • {video.views}</p>
                    <a href={video.url} target="_blank" rel="noopener noreferrer">
                      Watch Video
                    </a>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Content Summary */}
        {module.content && (
          <div className="section">
            <h4>Content Overview</h4>
            <p>{module.content.introduction || module.content.summary}</p>
            
            {module.content.key_concepts && (
              <div className="key-concepts">
                <strong>Key Concepts:</strong>
                <div className="concepts-tags">
                  {module.content.key_concepts.map((concept, index) => (
                    <span key={index} className="concept-tag">{concept}</span>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      <div className="module-actions">
        <button onClick={() => setSelectedModule(module)} className="btn-primary">
          View Details
        </button>
        <button onClick={() => downloadNotes(module.id, module.title)} className="btn-secondary">
          Download Notes
        </button>
        <button onClick={() => downloadAssignments(module.id, module.title)} className="btn-secondary">
          Download Assignments
        </button>
      </div>
    </div>
  );

  const ModuleDetails = ({ module, onClose }) => (
    <div className="module-details-overlay">
      <div className="module-details">
        <div className="details-header">
          <h2>{module.title || module.topic}</h2>
          <button onClick={onClose} className="close-btn">×</button>
        </div>
        
        <div className="details-content">
          {/* Content */}
          {module.content && (
            <div className="details-section">
              <h3>Educational Content</h3>
              <p>{module.content.detailed_explanation}</p>
              
              {module.content.practical_examples && (
                <div className="examples">
                  <h4>Practical Examples</h4>
                  {module.content.practical_examples.map((example, index) => (
                    <div key={index} className="example">
                      <h5>{example.title}</h5>
                      <p>{example.description}</p>
                      {example.code_snippet && (
                        <pre className="code-snippet">{example.code_snippet}</pre>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Notes */}
          {module.notes && (
            <div className="details-section">
              <h3>Study Notes</h3>
              {module.notes.sections?.map((section, index) => (
                <div key={index} className="note-section">
                  <h4>{section.heading}</h4>
                  <p>{section.content}</p>
                  {section.key_points && (
                    <ul>
                      {section.key_points.map((point, idx) => (
                        <li key={idx}>{point}</li>
                      ))}
                    </ul>
                  )}
                </div>
              ))}
            </div>
          )}

          {/* Assignments */}
          {module.assignments && (
            <div className="details-section">
              <h3>Assignments</h3>
              {module.assignments.map((assignment, index) => (
                <div key={index} className="assignment">
                  <h4>{assignment.title}</h4>
                  <p>{assignment.description}</p>
                  <p><strong>Estimated Time:</strong> {assignment.estimated_time}</p>
                  {assignment.instructions && (
                    <ol>
                      {assignment.instructions.map((instruction, idx) => (
                        <li key={idx}>{instruction}</li>
                      ))}
                    </ol>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );

  return (
    <div className="enhanced-modules">
      <div className="modules-header">
        <h1>Learning Modules</h1>
        <button 
          onClick={() => setShowCreateForm(true)} 
          className="btn-primary"
          disabled={loading}
        >
          Create New Module
        </button>
      </div>

      {error && <div className="error-message">{error}</div>}

      {showCreateForm && (
        <div className="create-form-overlay">
          <div className="create-form">
            <h2>Create New Learning Module</h2>
            
            <div className="form-group">
              <label>Topic</label>
              <input
                type="text"
                value={newModuleData.topic}
                onChange={(e) => setNewModuleData({...newModuleData, topic: e.target.value})}
                placeholder="e.g., Introduction to Python Programming"
                disabled={loading}
              />
            </div>

            <div className="form-group">
              <label>Difficulty Level</label>
              <select
                value={newModuleData.difficulty}
                onChange={(e) => setNewModuleData({...newModuleData, difficulty: e.target.value})}
                disabled={loading}
              >
                <option value="Beginner">Beginner</option>
                <option value="Intermediate">Intermediate</option>
                <option value="Advanced">Advanced</option>
              </select>
            </div>

            <div className="form-actions">
              <button 
                onClick={createModule} 
                className="btn-primary"
                disabled={loading}
              >
                {loading ? 'Generating...' : 'Generate Module'}
              </button>
              <button 
                onClick={() => setShowCreateForm(false)} 
                className="btn-secondary"
                disabled={loading}
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      <div className="modules-grid">
        {modules.map((module, index) => (
          <ModuleCard key={module.id || index} module={module} />
        ))}
      </div>

      {modules.length === 0 && !loading && (
        <div className="empty-state">
          <h3>No modules yet</h3>
          <p>Create your first learning module to get started!</p>
        </div>
      )}

      {selectedModule && (
        <ModuleDetails 
          module={selectedModule} 
          onClose={() => setSelectedModule(null)} 
        />
      )}
    </div>
  );
};

export default EnhancedModules;
