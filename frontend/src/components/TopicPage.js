import React from 'react';
import { useParams } from 'react-router-dom';

const topicDetails = {
  "variables": {
    title: "Variables & Data Types",
    content: "Explanation about var, let, const, and types like string, number, boolean."
  },
  "js-basics": {
    title: "JavaScript Basics",
    content: "Basics like loops, conditions, syntax, operators, etc."
  },
  "react-components": {
    title: "React Components",
    content: "How to use functional components, props, and component structure."
  },
  "apis-fetch": {
    title: "APIs & Fetch",
    content: "Using fetch, async/await, working with REST APIs."
  },
  "flask-integration": {
    title: "Flask Integration",
    content: "Connect frontend with Flask backend using Axios or fetch."
  }
};

function TopicPage() {
  const { topicId } = useParams();
  const topic = topicDetails[topicId];

  if (!topic) return <div style={{ padding: 40 }}>Topic not found.</div>;

  return (
    <div style={{ padding: 40 }}>
      <h1>{topic.title}</h1>
      <p>{topic.content}</p>
    </div>
  );
}

export default TopicPage;
