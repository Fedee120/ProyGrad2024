import { BACKEND_URL } from '../constants';

export const suggestionsService = {
  async getSuggestions(
    history: { role: string; content: string }[],
    token: string
  ): Promise<string[]> {
    try {
      const response = await fetch(`${BACKEND_URL}/generate_suggestions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({ history }),
      });

      if (!response.ok) {
        const errorBody = await response.text();
        throw new Error(`HTTP error! status: ${response.status}, body: ${errorBody}`);
      }

      const data = await response.json();
      return data.suggestions;
    } catch (error) {
      console.error('Error getting suggestions:', error);
      return [];
    }
  },
}; 