export interface Feedback {
  email: string;
  threadId: string;
  messageId: string | null;
  appVersion: string;
  comment: string;
  timestamp: Date;
} 