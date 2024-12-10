import React from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useChat } from '../../hooks/useChat';
import { useSuggestions } from '../../hooks/useSuggestions';
import Layout from "../layout";
import Suggestions from '../../components/Suggestions/Suggestions';
import './Chat.css';
import Button from 'src/components/common/Button/Button';

const Chat = () => {
  const { currentUser } = useAuth();
  const {
    messages,
    inputMessage,
    setInputMessage,
    sendMessage,
    backendStatus,
  } = useChat();

  const {
    suggestions,
    isLoading: suggestionsLoading,
    handleSuggestionClick
  } = useSuggestions(messages);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const messageToSend = inputMessage;
    setInputMessage('');
    await sendMessage(messageToSend);
  };

  return (
    <Layout>
      <div className="chat-container">
        <div className="chat-header">
          <h1 className="chat-title">
            Asistente Virtual para Docentes
          </h1>
        </div>

        <div className="chat-status">
          <h2>Comunicación con Backend</h2>
          <div className={`status-indicator ${backendStatus.isUp ? 'status-up' : 'status-down'}`}>
            {backendStatus.message}
          </div>
        </div>

        <div className="chat-messages">
          {messages.map((message, index) => (
            <div key={index} className={`message ${message.role}`}>
              <div className="message-content">{message.content}</div>
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
        </div>

        <Suggestions
          suggestions={suggestions}
          isLoading={suggestionsLoading}
          onSuggestionClick={(suggestion) => handleSuggestionClick(suggestion, sendMessage)}
        />

        <form onSubmit={handleSubmit} className="chat-input-form">
          <input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            placeholder="Haz una pregunta..."
            className="chat-input"
          />
          <Button type="submit" size='large'>
            Enviar
          </Button>
        </form>
      </div>
    </Layout>
  );
};

export default Chat; 