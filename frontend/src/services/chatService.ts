import { BACKEND_URL } from '../constants';

export const chatService = {
  async sendMessage(
    message: string, 
    userId: string, 
    token: string, 
    history: { role: string; content: string }[],
    threadId: string
  ): Promise<{id: string, timestamp: string, response: string, citations: string[]}> {
    try {
      const response = await fetch(`${BACKEND_URL}/invoke_agent`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({ message, userId, history, threadId }),
      });

      if (!response.ok) {
        const errorBody = await response.json();
        throw new Error(errorBody.detail || 'Ha ocurrido un error desconocido');
      }
      const data = await response.json();
      return {
        id: data.id,
        timestamp: data.timestamp,
        response: data.response,
        citations: data.citations || []
      };
    } catch (error) {
      throw this.handleError(error);
    }
  },

  handleError(error: unknown): Error {
    console.log(error);
    if (error instanceof Error) {
        if (error.name === 'TypeError' && 
        (error.message.includes('CORS') || 
            error.message.includes('Failed to fetch') ||
            error.message.includes('Load failed') ||
            error.message.includes('Network request failed'))) {
            return new Error('El servidor no está respondiendo.');
        }
        // Try to parse JSON error message if it exists
        try {
            if (error.message.includes('body:')) {
                const jsonStr = error.message.split('body:')[1].trim();
                const jsonError = JSON.parse(jsonStr);
                if (jsonError.detail) {
                    return new Error(jsonError.detail);
                }
            }
        } catch (_) {
            // If parsing fails, return original error
        }
        return error;
    }
    return new Error(`Error desconocido: ${JSON.stringify(error)}`);
  }
}; 