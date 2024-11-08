import React, { useState, useEffect } from 'react';
import { ChatMessage, BackendResponse } from '../../types/chat';
import { useAuth } from '../../contexts/AuthContext';
import './Chat.css';

const BACKEND_URL = 'http://backend:8080';

const Chat: React.FC = () => {
  const { user } = useAuth();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [backendStatus, setBackendStatus] = useState<{
    isUp: boolean;
    message: string;
  }>({ isUp: false, message: 'Checking status...' });

  const checkBackendStatus = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/check_status`);
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      setBackendStatus({ isUp: true, message: 'Backend is up!' });
    } catch (error) {
      const errorMessage = `Error checking backend status: ${error}`;
      setBackendStatus({ isUp: false, message: errorMessage });
      console.error(errorMessage);
    }
  };

  const sendQueryToBackend = async (query: string): Promise<string> => {
    try {
      const response = await fetch(`${BACKEND_URL}/invoke_agent`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${user?.token}`,
        },
        body: JSON.stringify({
          message: query,
          userId: user?.uid,
        }),
      });

      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      const data = await response.json();
      return data.response;
    } catch (error) {
      const errorMessage = `Error communicating with backend: ${error}`;
      console.error(errorMessage);
      return errorMessage;
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputMessage.trim()) return;

    const userMessage: ChatMessage = {
      role: 'user',
      content: inputMessage,
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputMessage('');

    const assistantResponse = await sendQueryToBackend(inputMessage);
    const assistantMessage: ChatMessage = {
      role: 'assistant',
      content: assistantResponse,
    };

    setMessages((prev) => [...prev, assistantMessage]);
  };

  useEffect(() => {
    checkBackendStatus();
    const intervalId = setInterval(checkBackendStatus, 30000); // Check every 30 seconds
    return () => clearInterval(intervalId);
  }, []);

  return (
    <div className="chat-container">
      <div className="chat-header">
        <h1 className="chat-title">
          Asistente Virtual para Docentes
        </h1>
        {user && (
          <div className="user-info">
            Bienvenido, {user.email}
          </div>
        )}
      </div>

      <div className="chat-sidebar">
        <h2>Comunicación con Backend</h2>
        <div
          className={`status-indicator ${
            backendStatus.isUp ? 'status-up' : 'status-down'
          }`}
        >
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
  );
};

export default Chat; 