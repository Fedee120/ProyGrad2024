import React from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useChat } from '../../hooks/useChat';
import Layout from "../layout";
import './Chat.css';

const Chat = () => {
  const { currentUser } = useAuth();
  const {
    messages,
    inputMessage,
    setInputMessage,
    sendMessage,
    backendStatus,
  } = useChat();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setInputMessage('');
    await sendMessage(inputMessage);
  };

  return (
    <Layout>
      <div className="chat-container">
        <div className="chat-header">
          <h1 className="chat-title">
            Asistente Virtual para Docentes
          </h1>
          {currentUser && (
            <div className="user-info">
              Bienvenido, {currentUser.email}
            </div>
          )}
        </div>

        <div className="chat-sidebar">
          <h2>Comunicación con Backend</h2>
          <div className={`status-indicator ${backendStatus.isUp ? 'status-up' : 'status-down'}`}>
            {backendStatus.message}
          </div>
        </div>

        <div className="chat-messages">
          {messages.map((message, index) => (
            <div key={index} className={`message ${message.role}`}>
              <div className="message-content">{message.content}</div>
            </div>
          ))}
        </div>

        <form onSubmit={handleSubmit} className="chat-input-form">
          <input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            placeholder="Haz una pregunta..."
            className="chat-input"
          />
          <button type="submit" className="chat-submit">
            Enviar
          </button>
        </form>
      </div>
    </Layout>
  );
};

export default Chat; 