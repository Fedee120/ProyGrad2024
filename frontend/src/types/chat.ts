export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export interface BackendResponse {
  response: string;
} 