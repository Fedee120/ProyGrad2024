from typing import List
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
import os
from dotenv import load_dotenv

load_dotenv()

class SuggestionsResponse(BaseModel):
    suggestions: List[str] = Field(
        description="Lista de 3 sugerencias de preguntas cortas (máximo 8 palabras) para continuar la conversación"
    )

class SuggestionsGenerator:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.7
        )
        self.parser = PydanticOutputParser(pydantic_object=SuggestionsResponse)

    def generate_suggestions(self, history: List[dict]) -> List[str]:
        """
        Genera sugerencias de preguntas basadas en el historial de la conversación.
        
        Args:
            history: Lista de mensajes en formato {role: str, content: str}
            
        Returns:
            List[str]: Lista de sugerencias de preguntas
        """
        formatted_history = self._format_history_messages(history)
        
        prompt = f"""Basado en la siguiente conversación, genera 3 preguntas cortas y concisas 
        (máximo 8 palabras cada una) que ayuden a profundizar el tema o explorar aspectos relacionados. 
        Las preguntas deben ser naturales y fáciles de entender. Prioriza los mensajes más recientes.
        Las preguntas que generes seran utilizadas como input de usuario para el modelo de lenguaje, continuando la conversación. 
        Por lo tanto, debes escribirlas como si fueras un usuario interesado en el tema.
        Historial de la conversación:
        {formatted_history}

        Formato de salida esperado:
        {self.parser.get_format_instructions()}
        """
        
        chain = self.llm.with_structured_output(SuggestionsResponse)
        response = chain.invoke(prompt)
        
        return response.suggestions

    def _format_history_messages(self, history: List[dict]) -> List[BaseMessage]:
        """Convierte el historial de chat en una lista de mensajes."""
        if not history:
            return []
        
        formatted_messages = []
        for msg in history:
            if msg["role"] == "user":
                formatted_messages.append(HumanMessage(content=msg["content"]))
            else:
                formatted_messages.append(AIMessage(content=msg["content"]))
        
        return formatted_messages 
    
if __name__ == "__main__":
    generator = SuggestionsGenerator()
    history = [
        {"role": "user", "content": "Hola, ¿cómo estás?"},
        {"role": "assistant", "content": "Estoy bien, gracias por preguntar. Soy un agente de IA que te puede ayudar con preguntas sobre inteligencia artificial enfocada en la educación."}
    ]
    suggestions = generator.generate_suggestions(history)
    print(suggestions)
