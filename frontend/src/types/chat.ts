export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'error';
  content: string;
  timestamp: string;
  citations?: string[];
}

export interface BackendResponse {
  response: string;
} 