import { useState, useEffect } from 'react';
import { ChatMessage } from '../types/chat';
import { chatService } from '../services/chatService';
import { useAuth } from '../contexts/AuthContext';
import { generateThreadId } from '../utils/threadUtils';

export function useChat() {
  const { currentUser, getIdToken } = useAuth();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [threadId] = useState(generateThreadId());
  const [isTyping, setIsTyping] = useState(false);
  const [hasError, setHasError] = useState(false);

  const sendMessage = async (message: string) => {
    if (!message.trim() || !currentUser) return;
    setHasError(false);

    const userMessage: ChatMessage = {
      id: "-",
      role: 'user',
      content: message,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setIsTyping(true);
    
    try {
      const token = await getIdToken();
      await new Promise(resolve => setTimeout(resolve, 500)); // Wait for 500ms to ensure token is listed in the backend
      
      const messageHistory = messages.map(msg => ({
        role: msg.role,
        content: msg.content
      }));

      const { id, timestamp, response, citations } = await chatService.sendMessage(
        message, 
        currentUser.uid, 
        token,
        messageHistory,
        threadId
      );
      
      const assistantMessage: ChatMessage = {
        id,
        role: 'assistant',
        content: response,
        timestamp,
        citations
      };
      
      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage: ChatMessage = {
        id: "-",
        role: 'error',
        content: error instanceof Error ? error.message : 'Error sending message',
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, errorMessage]);
      setHasError(true);
    } finally {
      setIsTyping(false);
    }
  };

  return {
    messages,
    inputMessage,
    setInputMessage,
    sendMessage,
    threadId,
    isTyping,
    hasError,
  };
} 