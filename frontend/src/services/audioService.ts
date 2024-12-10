import { BACKEND_URL } from '../constants';

export const audioService = {
  async transcribeAudio(audioBlob: Blob): Promise<string> {
    try {
      const formData = new FormData();
      formData.append('audio_file', audioBlob, 'audio.webm');

      const response = await fetch(`${BACKEND_URL}/transcribe-audio`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Error del servidor: ${response.status} - ${errorText}`);
      }

      const data = await response.json();
      
      if (data.text) {
        return data.text;
      } else if (data.error) {
        throw new Error(data.error);
      } else {
        throw new Error('No se pudo transcribir el audio');
      }
    } catch (error) {
      console.error('Error sending audio:', error);
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
        return new Error('Servidor no responde, asegúrate de que esté funcionando y la configuración CORS sea correcta.');
      }
      return error;
    }
    return new Error(`Error desconocido: ${JSON.stringify(error)}`);
  }
}; 