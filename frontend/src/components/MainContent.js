import React from 'react';

function MainContent() {
  return (
    <div className="main-content">
      <section id="variables">
        <h2>Variables & Data Types</h2>
        <p>This section explains JavaScript variables, let/const/var, and data types.</p>
      </section>

      <section id="js-basics">
        <h2>JavaScript Basics</h2>
        <p>Syntax, loops, conditionals, and core programming constructs.</p>
      </section>

      <section id="react-components">
        <h2>React Components</h2>
        <p>Introduction to functional components, props, and component-based design.</p>
      </section>

      <section id="apis-fetch">
        <h2>APIs & Fetch</h2>
        <p>Using fetch(), promises, async/await, and REST APIs.</p>
      </section>

      <section id="flask-integration">
        <h2>Flask Integration</h2>
        <p>Backend API with Flask and integrating with React frontend.</p>
      </section>
    </div>
  );
}

export default MainContent;
