import React, { useRef, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useChat } from '../../hooks/useChat';
import Layout from "../layout";
import './Chat.css';
import Button from 'src/components/common/Button/Button';
import { formatMessageTime } from '../../utils/dateUtils';

const Chat = () => {
  const { currentUser } = useAuth();
  const {
    messages,
    inputMessage,
    setInputMessage,
    sendMessage,
    backendStatus,
    threadId,
    isTyping,
    hasError,
  } = useChat();

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setInputMessage('');
    await sendMessage(inputMessage);
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  // Scroll when messages change or typing state changes
  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  return (
    <Layout>
      <div className="chat-container">
        <div className="chat-header">
          <h1 className="chat-title">
            Asistente Virtual para Docentes
          </h1>
          <div className="header-info">
            <div className={`status-indicator-small ${backendStatus.isUp ? 'status-up' : 'status-down'}`}>
              {backendStatus.message}
            </div>
            <div className="app-version">
              Version: {process.env.REACT_APP_APP_VERSION ?? ' unknown'}
            </div>
            <div className="thread-id">
              ID: {threadId}
            </div>
          </div>
        </div>

        <div className="chat-messages">
          {messages.map((message) => (
            <div key={message.id} className={`message ${message.role}`}>
              <div className="message-content">
                {message.content}
                <span className="message-timestamp">{formatMessageTime(message.timestamp)}</span>
              </div>
              {message.citations && message.citations.length > 0 && (
                <div className="message-citations">
                  <div className="citations-header">Sources:</div>
                  <ul>
                    {message.citations.map((citation, citationIndex) => (
                      <li key={citationIndex}>{citation}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ))}
          {isTyping && (
            <div className="typing-indicator">
              <span></span>
              <span></span>
              <span></span>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <form onSubmit={handleSubmit} className="chat-input-form">
          <input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            placeholder={hasError ? "Ha habido un error, la conversación no se puede continuar" : "Haz una pregunta..."}
            className="chat-input"
            disabled={isTyping || hasError}
          />
          <Button 
            type="submit" 
            size='large' 
            disabled={isTyping || hasError}
          >
            Enviar
          </Button>
        </form>
      </div>
    </Layout>
  );
};

export default Chat; 