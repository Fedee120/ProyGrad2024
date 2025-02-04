import { collection, addDoc } from "firebase/firestore";
import { firestoreDB } from "../firebase";
import { Feedback } from "../types/feedback";
import { getAuth } from "firebase/auth";

export const feedbackService = {
  async submitFeedback(feedback: Omit<Feedback, 'timestamp'>) {
    try {
      const feedbacksCollection = collection(firestoreDB, 'feedbacks');
      await addDoc(feedbacksCollection, {
        ...feedback,
        timestamp: new Date()
      });
    } catch (error) {
      console.error('Error submitting feedback:', error);
      if (error instanceof Error) {
        throw new Error(`Error al enviar feedback: ${error.message}`);
      }
      throw new Error('Error al enviar feedback');
    }
  }
}; 