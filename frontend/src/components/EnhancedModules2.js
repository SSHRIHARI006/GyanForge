import React, { useState, useEffect } from 'react';

const EnhancedModules = () => {
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
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/v1/modules', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      const data = await response.json();
      if (data.success) {
        setModules(data.modules);
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
      const token = localStorage.getItem('token');
      const response = await fetch('/api/v1/modules/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(newModuleData)
      });

      const data = await response.json();
      if (data.success) {
        setModules([...modules, { id: data.module_id, ...data.module, title: newModuleData.topic }]);
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

  useEffect(() => {
    fetchModules();
  }, []);

  return (
    <div className="enhanced-modules" style={{ padding: '20px' }}>
      <div className="modules-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h1>Learning Modules</h1>
        <button 
          onClick={() => setShowCreateForm(true)} 
          style={{ 
            backgroundColor: '#007bff', 
            color: 'white', 
            border: 'none', 
            padding: '10px 20px', 
            borderRadius: '5px',
            cursor: 'pointer'
          }}
          disabled={loading}
        >
          Create New Module
        </button>
      </div>

      {error && (
        <div style={{ backgroundColor: '#f8d7da', color: '#721c24', padding: '10px', borderRadius: '5px', marginBottom: '20px' }}>
          {error}
        </div>
      )}

      {showCreateForm && (
        <div style={{ 
          position: 'fixed', 
          top: 0, 
          left: 0, 
          right: 0, 
          bottom: 0, 
          backgroundColor: 'rgba(0,0,0,0.5)', 
          display: 'flex', 
          justifyContent: 'center', 
          alignItems: 'center', 
          zIndex: 1000 
        }}>
          <div style={{ 
            backgroundColor: 'white', 
            padding: '30px', 
            borderRadius: '10px', 
            minWidth: '400px' 
          }}>
            <h2>Create New Learning Module</h2>
            
            <div style={{ marginBottom: '15px' }}>
              <label style={{ display: 'block', marginBottom: '5px' }}>Topic</label>
              <input
                type="text"
                value={newModuleData.topic}
                onChange={(e) => setNewModuleData({...newModuleData, topic: e.target.value})}
                placeholder="e.g., Introduction to Python Programming"
                style={{ 
                  width: '100%', 
                  padding: '10px', 
                  border: '1px solid #ddd', 
                  borderRadius: '5px' 
                }}
                disabled={loading}
              />
            </div>

            <div style={{ marginBottom: '20px' }}>
              <label style={{ display: 'block', marginBottom: '5px' }}>Difficulty Level</label>
              <select
                value={newModuleData.difficulty}
                onChange={(e) => setNewModuleData({...newModuleData, difficulty: e.target.value})}
                style={{ 
                  width: '100%', 
                  padding: '10px', 
                  border: '1px solid #ddd', 
                  borderRadius: '5px' 
                }}
                disabled={loading}
              >
                <option value="Beginner">Beginner</option>
                <option value="Intermediate">Intermediate</option>
                <option value="Advanced">Advanced</option>
              </select>
            </div>

            <div style={{ display: 'flex', gap: '10px' }}>
              <button 
                onClick={createModule} 
                style={{ 
                  backgroundColor: '#007bff', 
                  color: 'white', 
                  border: 'none', 
                  padding: '10px 20px', 
                  borderRadius: '5px',
                  cursor: 'pointer'
                }}
                disabled={loading}
              >
                {loading ? 'Generating...' : 'Generate Module'}
              </button>
              <button 
                onClick={() => setShowCreateForm(false)} 
                style={{ 
                  backgroundColor: '#6c757d', 
                  color: 'white', 
                  border: 'none', 
                  padding: '10px 20px', 
                  borderRadius: '5px',
                  cursor: 'pointer'
                }}
                disabled={loading}
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))', gap: '20px' }}>
        {modules.map((module, index) => (
          <div key={module.id || index} style={{ 
            border: '1px solid #ddd', 
            borderRadius: '10px', 
            padding: '20px', 
            backgroundColor: 'white',
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
          }}>
            <div style={{ marginBottom: '15px' }}>
              <h3 style={{ margin: '0 0 5px 0' }}>{module.title || module.topic}</h3>
              <span style={{ 
                backgroundColor: module.difficulty === 'Beginner' ? '#28a745' : 
                                module.difficulty === 'Intermediate' ? '#ffc107' : '#dc3545',
                color: 'white',
                padding: '2px 8px',
                borderRadius: '12px',
                fontSize: '12px'
              }}>
                {module.difficulty}
              </span>
            </div>
            
            {/* Learning objectives */}
            {module.learning_objectives && (
              <div style={{ marginBottom: '15px' }}>
                <h4>Learning Objectives</h4>
                <ul style={{ margin: '5px 0', paddingLeft: '20px' }}>
                  {module.learning_objectives.map((objective, idx) => (
                    <li key={idx}>{objective}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* Recommended Videos */}
            {module.recommended_videos && module.recommended_videos.length > 0 && (
              <div style={{ marginBottom: '15px' }}>
                <h4>Recommended Videos ({module.recommended_videos.length})</h4>
                <div style={{ display: 'grid', gap: '10px' }}>
                  {module.recommended_videos.slice(0, 2).map((video, idx) => (
                    <div key={idx} style={{ 
                      display: 'flex', 
                      gap: '10px', 
                      padding: '10px', 
                      border: '1px solid #eee', 
                      borderRadius: '5px' 
                    }}>
                      <img src={video.thumbnail} alt={video.title} style={{ width: '60px', height: '45px', objectFit: 'cover' }} />
                      <div>
                        <h6 style={{ margin: '0 0 5px 0', fontSize: '14px' }}>{video.title.substring(0, 50)}...</h6>
                        <p style={{ margin: '0', fontSize: '12px', color: '#666' }}>{video.channel}</p>
                        <a href={video.url} target="_blank" rel="noopener noreferrer" style={{ fontSize: '12px' }}>
                          Watch Video
                        </a>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
              <button 
                onClick={() => setSelectedModule(module)} 
                style={{ 
                  backgroundColor: '#007bff', 
                  color: 'white', 
                  border: 'none', 
                  padding: '8px 15px', 
                  borderRadius: '5px',
                  cursor: 'pointer',
                  fontSize: '14px'
                }}
              >
                View Details
              </button>
              <button 
                style={{ 
                  backgroundColor: '#28a745', 
                  color: 'white', 
                  border: 'none', 
                  padding: '8px 15px', 
                  borderRadius: '5px',
                  cursor: 'pointer',
                  fontSize: '14px'
                }}
              >
                Download Notes
              </button>
            </div>
          </div>
        ))}
      </div>

      {modules.length === 0 && !loading && (
        <div style={{ textAlign: 'center', padding: '40px' }}>
          <h3>No modules yet</h3>
          <p>Create your first learning module to get started!</p>
        </div>
      )}

      {selectedModule && (
        <div style={{ 
          position: 'fixed', 
          top: 0, 
          left: 0, 
          right: 0, 
          bottom: 0, 
          backgroundColor: 'rgba(0,0,0,0.5)', 
          display: 'flex', 
          justifyContent: 'center', 
          alignItems: 'center', 
          zIndex: 1000 
        }}>
          <div style={{ 
            backgroundColor: 'white', 
            padding: '30px', 
            borderRadius: '10px', 
            maxWidth: '800px',
            maxHeight: '80vh',
            overflow: 'auto'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
              <h2>{selectedModule.title || selectedModule.topic}</h2>
              <button 
                onClick={() => setSelectedModule(null)} 
                style={{ 
                  backgroundColor: 'transparent', 
                  border: 'none', 
                  fontSize: '24px',
                  cursor: 'pointer'
                }}
              >
                ×
              </button>
            </div>
            
            <div>
              {/* Content */}
              {selectedModule.content && (
                <div style={{ marginBottom: '20px' }}>
                  <h3>Educational Content</h3>
                  <p>{selectedModule.content.detailed_explanation}</p>
                  
                  {selectedModule.content.practical_examples && (
                    <div>
                      <h4>Practical Examples</h4>
                      {selectedModule.content.practical_examples.map((example, idx) => (
                        <div key={idx} style={{ marginBottom: '15px', padding: '15px', backgroundColor: '#f8f9fa', borderRadius: '5px' }}>
                          <h5>{example.title}</h5>
                          <p>{example.description}</p>
                          {example.code_snippet && (
                            <pre style={{ backgroundColor: '#e9ecef', padding: '10px', borderRadius: '3px', overflow: 'auto' }}>
                              {example.code_snippet}
                            </pre>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {/* All Videos */}
              {selectedModule.recommended_videos && selectedModule.recommended_videos.length > 0 && (
                <div style={{ marginBottom: '20px' }}>
                  <h3>All Recommended Videos</h3>
                  <div style={{ display: 'grid', gap: '15px' }}>
                    {selectedModule.recommended_videos.map((video, idx) => (
                      <div key={idx} style={{ 
                        display: 'flex', 
                        gap: '15px', 
                        padding: '15px', 
                        border: '1px solid #eee', 
                        borderRadius: '8px' 
                      }}>
                        <img src={video.thumbnail} alt={video.title} style={{ width: '120px', height: '90px', objectFit: 'cover' }} />
                        <div>
                          <h5 style={{ margin: '0 0 10px 0' }}>{video.title}</h5>
                          <p style={{ margin: '0 0 5px 0', color: '#666' }}>{video.channel}</p>
                          <p style={{ margin: '0 0 10px 0', fontSize: '14px', color: '#666' }}>{video.duration} • {video.views}</p>
                          <a href={video.url} target="_blank" rel="noopener noreferrer" style={{ 
                            backgroundColor: '#dc3545',
                            color: 'white',
                            padding: '8px 15px',
                            textDecoration: 'none',
                            borderRadius: '5px',
                            fontSize: '14px'
                          }}>
                            Watch on YouTube
                          </a>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default EnhancedModules;
