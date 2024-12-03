export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  citations?: string[];
}

export interface BackendResponse {
  response: string;
} 