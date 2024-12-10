import React from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useChat } from '../../hooks/useChat';
import Layout from "../layout";
import './Chat.css';
import Button from 'src/components/common/Button/Button';
import { FaInfoCircle } from 'react-icons/fa';

interface Message {
  role: string;
  content: string;
  citations?: string[];
}

const Chat: React.FC = () => {
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
    if (inputMessage.trim()) {
      setInputMessage('');
      await sendMessage(inputMessage);
    }
  };

  return (
    <Layout>
      <div className="chat-container">
        <div className="chat-header">
          <h1 className="chat-title">
            Asistente Virtual para Docentes
          </h1>
        </div>

        <div className="chat-tip-container">
          <FaInfoCircle className="chat-tip-icon" />
          <p className="chat-tip-text">
            Este es un espacio seguro para interactuar. Tus conversaciones se guardan solo para mejorar tu experiencia y puedes eliminarlas cuando lo desees. Tu privacidad es importante: ningún contenido se comparte con terceros.
          </p>
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