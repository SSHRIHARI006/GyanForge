import React, { useState } from 'react';

function ChatBox() {
  const [input, setInput] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log('You asked:', input);
    setInput('');
  };

  return (
    <form className="chat-box" onSubmit={handleSubmit}>
      <input
        type="text"
        placeholder="Ask Study Buddy..."
        value={input}
        onChange={(e) => setInput(e.target.value)}
      />
      <button type="submit">➤</button>
    </form>
  );
}

export default ChatBox;
