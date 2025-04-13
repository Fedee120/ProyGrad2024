export interface Citation {
  text: string;      // Texto completo de la cita en formato APA
  source: string;    // Nombre del archivo fuente
  title?: string;    // Título del documento
  author?: string;   // Autor del documento
  year?: string;     // Año de publicación
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'error';
  content: string;
  timestamp: string;
  citations?: Citation[];
}

export interface BackendResponse {
  response: string;
  citations: Citation[];
} 