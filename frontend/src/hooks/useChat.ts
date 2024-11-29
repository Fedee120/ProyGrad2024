import { useState, useEffect } from 'react';
import { ChatMessage } from '../types/chat';
import { chatService } from '../services/chatService';
import { useAuth } from '../contexts/AuthContext';
import { generateThreadId } from '../utils/threadUtils';

export function useChat() {
  const { currentUser } = useAuth();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [threadId] = useState(generateThreadId());
  const [backendStatus, setBackendStatus] = useState<{
    isUp: boolean;
    message: string;
  }>({ isUp: false, message: 'Checking status...' });

  const checkBackendStatus = async () => {
    try {
      await chatService.checkStatus(currentUser?.token);
      setBackendStatus({ isUp: true, message: 'Backend is up!' });
    } catch (error) {
      setBackendStatus({ 
        isUp: false, 
        message: 'Backend is down: ' + (error instanceof Error ? error.message : 'Error checking status')
      });
    }
  };

  const sendMessage = async (message: string) => {
    if (!message.trim() || !currentUser) return;

    const userMessage: ChatMessage = {
      id: "-", // It will be defined in backend
      role: 'user',
      content: message,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    
    try {
      const messageHistory = messages.map(msg => ({
        role: msg.role,
        content: msg.content
      }));

      const { id, timestamp, response, citations } = await chatService.sendMessage(
        message, 
        currentUser.uid, 
        currentUser.token,
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
        role: 'assistant',
        content: error instanceof Error ? error.message : 'Error sending message',
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, errorMessage]);
    }
  };

  useEffect(() => {
    checkBackendStatus();
    const intervalId = setInterval(checkBackendStatus, 30000);
    return () => clearInterval(intervalId);
  }, [currentUser]);

  return {
    messages,
    inputMessage,
    setInputMessage,
    sendMessage,
    backendStatus,
    threadId,
  };
} 