from typing import List
from langchain_core.messages import BaseMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langsmith import traceable
import os
from dotenv import load_dotenv

load_dotenv()

class GenerateStep:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0
        )
        
        system_prompt = """Eres un asistente experto que genera respuestas precisas y útiles.
        Utiliza el contexto proporcionado y el historial de la conversación para generar una respuesta
        que sea:
        1. Relevante a la pregunta
        2. Basada en la información del contexto
        3. Coherente con el historial de la conversación
        4. Clara y bien estructurada
        
        Si el contexto no contiene información relevante, admítelo honestamente."""
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="history"),
            ("human", "Contexto:\n{context}\n\nPregunta: {question}")
        ])

    @traceable
    def run(self, question: str, context: str, history: List[BaseMessage] = None) -> str:
        """
        Genera una respuesta final basada en la pregunta, el contexto y el historial.
        
        Args:
            question: La pregunta del usuario
            context: El contexto relevante recuperado
            history: Historial de la conversación
            
        Returns:
            str: Respuesta generada
        """
        if history is None:
            history = []
            
        response = self.llm.invoke(
            self.prompt.format(
                question=question,
                context=context,
                history=history
            )
        )
        
        return response.content


if __name__ == "__main__":
    generator = GenerateStep()
    question = "¿Cuál es la capital de Francia?"
    context = "La capital de Francia es París."
    history = []
    response = generator.run(question, context, history)
    print(response)

