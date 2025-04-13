import React, { useRef, useEffect, useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useChat } from '../../hooks/useChat';
import Layout from "../layout";
import './Chat.css';
import Button from 'src/components/common/Button/Button';
import { formatMessageTime } from '../../utils/dateUtils';
import { feedbackService } from '../../services/feedbackService';
import { toast } from 'react-toastify';
import { useNavigate } from 'react-router-dom';

const Chat = () => {
  const { currentUser } = useAuth();
  const navigate = useNavigate();
  const {
    messages,
    inputMessage,
    setInputMessage,
    sendMessage,
    threadId,
    isTyping,
    hasError,
  } = useChat();

  const [showFeedback, setShowFeedback] = useState(false);
  const [feedbackText, setFeedbackText] = useState('');
  const [submittingFeedback, setSubmittingFeedback] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
      .then(() => {
        toast.success('ID copiado al portapapeles');
      })
      .catch(err => {
        console.error('Error al copiar: ', err);
        toast.error('No se pudo copiar al portapapeles');
      });
  };

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

  const handleFeedbackSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!feedbackText.trim() || !currentUser?.email) return;

    setSubmittingFeedback(true);
    try {
      await feedbackService.submitFeedback({
        email: currentUser.email,
        threadId,
        messageId: messages.length > 0 ? messages[messages.length - 1].id : null,
        appVersion: process.env.REACT_APP_APP_VERSION || 'unknown',
        comment: feedbackText
      });
      setFeedbackText('');
      setShowFeedback(false);
      toast.success('Feedback enviado correctamente');
    } catch (error) {
      console.error('Error submitting feedback:', error);
      toast.error(error instanceof Error ? error.message : 'Error al enviar el feedback');
    } finally {
      setSubmittingFeedback(false);
    }
  };

  return (
    <Layout>
      <div className="chat-container">
        <div className="chat-header">
          <h1 className="chat-title">
            Asistente Virtual: Integrando IA en la Educación
          </h1>
          <div className="header-info">
            <div className="metadata-column">
              <div className="app-version">
                Version: {process.env.REACT_APP_APP_VERSION ?? ' unknown'}
              </div>
              <div className="thread-id">
                ID: {threadId}
                <button
                  className="copy-button"
                  onClick={() => copyToClipboard(threadId)}
                  title="Copiar ID"
                >
                  <svg 
                    width="14" 
                    height="14" 
                    viewBox="0 0 24 24" 
                    fill="none" 
                    stroke="currentColor" 
                    strokeWidth="2" 
                    strokeLinecap="round" 
                    strokeLinejoin="round"
                  >
                    <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                    <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
                  </svg>
                </button>
              </div>
            </div>
            <div className="header-actions">
              <Button 
                onClick={() => setShowFeedback(true)}
                size="small"
                className="feedback-button"
              >
                <svg 
                  width="16" 
                  height="16" 
                  viewBox="0 0 24 24" 
                  fill="none" 
                  stroke="currentColor" 
                  strokeWidth="2" 
                  strokeLinecap="round" 
                  strokeLinejoin="round"
                >
                  <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
                </svg>
              </Button>
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

        {showFeedback && (
          <div className="feedback-modal">
            <div className="feedback-content">
              <h3>Comentarios para los desarrolladores del Asistente Virtual</h3>
              <form onSubmit={handleFeedbackSubmit}>
                <textarea
                  value={feedbackText}
                  onChange={(e) => setFeedbackText(e.target.value)}
                  placeholder="Escribe tus comentarios aquí..."
                  rows={4}
                  disabled={submittingFeedback}
                />
                <div className="feedback-actions">
                  <Button 
                    type="button" 
                    onClick={() => setShowFeedback(false)}
                    disabled={submittingFeedback}
                  >
                    Cancelar
                  </Button>
                  <Button 
                    type="submit"
                    disabled={!feedbackText.trim() || submittingFeedback}
                  >
                    Enviar
                  </Button>
                </div>
              </form>
            </div>
          </div>
        )}

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