export const generateThreadId = (): string => {
  return `thread_${Date.now()}_${Math.random().toString(36).substring(2, 15)}`;
}; 