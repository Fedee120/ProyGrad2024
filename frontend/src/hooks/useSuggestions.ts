import { useState, useEffect } from 'react';
import { suggestionsService } from '../services/suggestionsService';
import { useAuth } from '../contexts/AuthContext';
import { ChatMessage } from '../types/chat';

export function useSuggestions(messages: ChatMessage[]) {
  const { currentUser } = useAuth();
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const fetchSuggestions = async () => {
    if (!currentUser || messages.length === 0) return;

    setIsLoading(true);
    try {
      const messageHistory = messages.map(msg => ({
        role: msg.role,
        content: msg.content
      }));

      const newSuggestions = await suggestionsService.getSuggestions(
        messageHistory,
        currentUser.token
      );
      
      setSuggestions(newSuggestions);
    } catch (error) {
      console.error('Error fetching suggestions:', error);
      setSuggestions([]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSuggestionClick = async (suggestion: string, onSend: (msg: string) => Promise<void>) => {
    // Eliminar la sugerencia clickeada inmediatamente
    setSuggestions([]);
    // Enviar el mensaje en segundo plano
    onSend(suggestion).catch(error => {
      console.error('Error sending suggestion:', error);
    });
  };

  // Actualizar sugerencias cuando cambian los mensajes
  useEffect(() => {
    if (messages.length > 0 && messages[messages.length - 1].role === 'assistant') {
      fetchSuggestions();
    }
  }, [messages]);

  return {
    suggestions,
    isLoading,
    fetchSuggestions,
    handleSuggestionClick
  };
} 