import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './sidebar.css';

const topics = [
  { id: 'variables', name: 'Variables & Data Types' },
  { id: 'js-basics', name: 'JS Basics' },
  { id: 'react-components', name: 'React Components' },
  { id: 'apis-fetch', name: 'APIs & Fetch' },
  { id: 'flask-integration', name: 'Flask Integration' },
];

function Sidebar() {
  const [expanded, setExpanded] = useState(false);
  const [completedTopics, setCompletedTopics] = useState([]);
  const [revisionTopics, setRevisionTopics] = useState([]);
  const [showQuiz, setShowQuiz] = useState(false);

  const navigate = useNavigate();

  const isDone = (id) => completedTopics.includes(id);
  const isRevision = (id) => revisionTopics.includes(id);

  const toggleDone = (id) => {
    if (isDone(id)) {
      setCompletedTopics((prev) => prev.filter((t) => t !== id));
      setRevisionTopics((prev) => prev.filter((t) => t !== id));
    } else {
      setCompletedTopics((prev) => [...prev, id]);
    }
  };

  const toggleRevision = (id) => {
    if (isRevision(id)) {
      setRevisionTopics((prev) => prev.filter((t) => t !== id));
    } else {
      if (!isDone(id)) setCompletedTopics((prev) => [...prev, id]);
      setRevisionTopics((prev) => [...prev, id]);
    }
  };

  const pending = topics.filter((topic) => !isDone(topic.id));
  const completed = topics.filter((topic) => isDone(topic.id) && !isRevision(topic.id));
  const revision = topics.filter((topic) => isRevision(topic.id));

  return (
    <>
      <div
        className={`sidebar ${expanded ? 'expanded' : ''}`}
        onMouseEnter={() => setExpanded(true)}
        onMouseLeave={() => setExpanded(false)}
      >
        <div className="sidebar-icon">☰</div>

        {expanded && (
          <div className="sidebar-content-wrapper">
            <div className="sidebar-content">
              <h4>📚 To Be Done</h4>
              <ul>
                {pending.map((topic) => (
                  <li key={topic.id}>
                    <button onClick={() => navigate(`/topics/${topic.id}`)}>{topic.name}</button>
                    <button className="action-btn done" onClick={() => toggleDone(topic.id)}>
                      ✔ Mark Done
                    </button>
                  </li>
                ))}
              </ul>

              <h4>✅ Completed</h4>
              <ul>
                {completed.map((topic) => (
                  <li key={topic.id}>
                    <button onClick={() => navigate(`/topics/${topic.id}`)}>{topic.name}</button>
                    <button className="action-btn revise" onClick={() => toggleRevision(topic.id)}>
                      Revise
                    </button>
                    <button className="action-btn undo" onClick={() => toggleDone(topic.id)}>
                      Undo
                    </button>
                  </li>
                ))}
              </ul>

              <h4>🔁 For Revision</h4>
              <ul>
                {revision.map((topic) => (
                  <li key={topic.id}>
                    <button onClick={() => navigate(`/topics/${topic.id}`)}>{topic.name}</button>
                    <button className="action-btn done" onClick={() => toggleRevision(topic.id)}>
                      Done
                    </button>
                  </li>
                ))}
              </ul>
            </div>

            <button className="quiz-btn" onClick={() => setShowQuiz(true)}>
              🧠 Take Quiz
            </button>
          </div>
        )}
      </div>

      {showQuiz && (
        <div className="quiz-panel">
          <button className="close-quiz" onClick={() => setShowQuiz(false)}>×</button>
          <h3>Quick Quiz</h3>
          <p>Q1: What does <code>const</code> mean in JavaScript?</p>
          <ul>
            <li><input type="radio" name="q1" /> A: It defines a variable that can be reassigned</li>
            <li><input type="radio" name="q1" /> B: It defines a block-scoped, read-only variable</li>
            <li><input type="radio" name="q1" /> C: It defines a global variable</li>
          </ul>
          <button className="submit-btn">Submit</button>
        </div>
      )}
    </>
  );
}

export default Sidebar;
