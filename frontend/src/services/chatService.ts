import { BACKEND_URL } from '../constants';

export const chatService = {
  async checkStatus(token: string) {
    try {
      const response = await fetch(`${BACKEND_URL}/check_status`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      if (!response.ok) {
        const errorBody = await response.text();
        throw new Error(`HTTP error! status: ${response.status}, body: ${errorBody}`);
      }
      return true;
    } catch (error) {
      throw this.handleError(error);
    }
  },

  async sendMessage(message: string, userId: string, token: string): Promise<string> {
    try {
      const response = await fetch(`${BACKEND_URL}/invoke_agent`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({ message, userId }),
      });

      if (!response.ok) {
        const errorBody = await response.text();
        throw new Error(`HTTP error! status: ${response.status}, body: ${errorBody}`);
      }
      const data = await response.json();
      return data.response;
    } catch (error) {
      throw this.handleError(error);
    }
  },

  handleError(error: unknown): Error {
    if (error instanceof Error) {
        if (error.name === 'TypeError' && 
        (error.message.includes('CORS') || 
            error.message.includes('Failed to fetch') ||
            error.message.includes('Load failed') ||
            error.message.includes('Network request failed'))) {
        return new Error('CORS error: Unable to connect to backend. Please check CORS configuration.');
        }
        return error;
    }
    return new Error(`Unknown error: ${JSON.stringify(error)}`);
  }
}; 