import os
from dotenv import load_dotenv
from graph import app
from langsmith import Client
from langchain.callbacks.tracers.langchain import wait_for_all_tracers
from checkpointer import MongoDBCheckpointer
import uuid  # Añadido para generar thread_id

# Cargar variables de entorno
load_dotenv()

# Configurar LangSmith client
client = Client()

# Inicializar el checkpointer
checkpointer = MongoDBCheckpointer()

def run_graph(question: str, thread_id: str, debug: bool = False):
    """
    Ejecuta el grafo de RAG adaptativo con una pregunta.
    
    Args:
        thread_id (str): Identificador del hilo de conversación
        question (str): Pregunta del usuario
        debug (bool): Si es True, muestra información adicional de debug
    
    Returns:
        tuple: (respuesta generada, lista de documentos útiles)
    """
    # Guardar la pregunta del usuario
    checkpointer.save_message(thread_id=thread_id, user="user", message=question)
    
    # Entrada para el grafo
    inputs = {
        "question": question,
        "thread_id": thread_id
    }
    
    try:
        # Ejecutar el grafo
        response = ""
        useful_docs = []
        for output in app.stream(inputs):
            for key, value in output.items():
                if debug:
                    print(f"\nNodo: {key}")
                    if "documents" in value:
                        print(f"Documentos recuperados: {len(value['documents'])}")
                    if "generation" in value:
                        print("Generación completada")
                
                if key == "generate" and "generation" in value:
                    response = value["generation"]
                    useful_docs = value.get("useful_docs", [])
                elif key == "no_data" and "generation" in value:
                    response = value["generation"]
        
        # Guardar la respuesta generada con los documentos útiles
        checkpointer.save_message(thread_id=thread_id, user="bot", message=response, useful_docs=useful_docs)
        
        # Esperar a que se completen todas las trazas
        wait_for_all_tracers()
        return response, useful_docs
    except Exception as e:
        print(f"Error durante la ejecución: {e}")
        wait_for_all_tracers()
        raise

if __name__ == "__main__":
    # Ejemplo de uso
    thread_id = str(uuid.uuid4())
    question = "Hola, mi nombre es Federico"
    response, useful_docs = run_graph(question, thread_id)
    print(f"Respuesta: {response}")
    print(f"Historial: {checkpointer.get_history(thread_id)}")

    # followup pregunta
    question = "¿Que rol tiene la IA en la educacion?"
    response, useful_docs = run_graph(question, thread_id)
    print(f"Respuesta: {response}")
    print(f"Historial: {checkpointer.get_history(thread_id)}")

    # pregunta de que paises pregunte
    question = "¿Cual es mi nombre?"
    response, useful_docs = run_graph(question, thread_id)
    print(f"Respuesta: {response}")
    print(f"Historial: {checkpointer.get_history(thread_id)}")

