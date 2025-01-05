from typing import List, Dict
from typing_extensions import TypedDict
from init_db import load_db
from langsmith import traceable
from checkpointer import MongoDBCheckpointer
import os

from states.router import question_router
from states.retrieval_grader import retrieval_grader
from states.re_writer import question_rewriter
from states.generate import rag_chain
from states.hallucination_grader import hallucination_grader
from states.answer_grader import answer_grader
from states.no_data_response import no_data_chain

from langgraph.types import Send
from langgraph.graph import END, StateGraph, START

import operator
from typing import Annotated

from langchain.schema import Document

# Initialize retriever
retriever = load_db()

# Inicializar el checkpointer
checkpointer = MongoDBCheckpointer()

class GradeState(TypedDict):
    """
    Represents the partial state for grading a single document.
    """
    question: str
    document: str  # Contenido de la página
    # Ya no necesitamos 'grade' de entrada,
    # lo establecerá la función grade_document.

class GraphState(TypedDict):
    """
    Represents the state of our graph.
    """
    question: str
    generation: str
    documents: Annotated[List[Document], operator.add]
    results: Annotated[List[dict], operator.add]
    thread_id: str
    message_history: List[Dict]
    useful_docs: List[str]

@traceable(name="fetch_history")
def fetch_history(state: GraphState, **kwargs):
    """
    Recupera el historial de mensajes y lo añade al estado.
    El historial se formatea para mantener consistencia en el formato
    a lo largo de toda la aplicación.
    """
    print("---FETCH HISTORY---")
    thread_id = state["thread_id"]
    raw_history = checkpointer.get_history(thread_id=thread_id)
    
    # Formatear el historial
    formatted_history = []
    for msg in raw_history:
        formatted_msg = {
            "user": msg["user"],
            "message": msg["message"],
            "timestamp": msg["timestamp"]
        }
        formatted_history.append(formatted_msg)
    
    return {"message_history": formatted_history}

@traceable(name="retrieve")
def retrieve(state: GraphState, **kwargs):
    """
    Retrieve documents

    Args:
        state (GraphState): The current graph state

    Returns:
        dict: New key 'documents' that contains retrieved documents
    """
    print("---RETRIEVE---")
    question = state["question"]

    # Retrieval
    documents = retriever.invoke(question)
    return {"documents": documents, "question": question}

@traceable(name="generate")
def generate(state: GraphState, **kwargs):
    """
    Generate an answer from the LLM given question and relevant documents.

    Args:
        state (GraphState): The current graph state

    Returns:
        dict: New key 'generation' that contains LLM generation
    """
    print("---GENERATE---")
    question = state["question"]
    documents = state["documents"]
    message_history = state.get("message_history", [])
    useful_docs = state.get("useful_docs", [])

    # RAG generation
    generation = rag_chain.invoke({"context": documents, "question": question})
    return {
        "documents": documents, 
        "question": question, 
        "generation": generation,
        "message_history": message_history,
        "thread_id": state["thread_id"],
        "useful_docs": useful_docs,
        "next": "grade_generation"
    }


@traceable(name="map_grade_document")
def map_grade_document(state: GraphState):
    """
    Mapea la función de calificación a través de todos los documentos usando el patrón map-reduce.

    Retornamos una lista de Send(...) para que LangGraph ejecute 
    'grade_document' una vez por cada documento.
    """
    print("---MAP GRADE DOCUMENT---")
    return [
        Send(
            "grade_document",
            {
                "question": state["question"],
                "document": doc.page_content,
            }
        )
        for doc in state["documents"]
    ]
@traceable(name="grade_document")
def grade_document(state: GradeState, **kwargs):
    print("---CHECK DOCUMENT RELEVANCE TO QUESTION---")
    question = state["question"]
    document = state["document"]

    score = retrieval_grader.invoke({
        "document": document,
        "question": question 
    })
    
    if score.binary_score == "yes":
        print("---GRADE: DOCUMENT RELEVANT---")
        # <--- Cambio: devolvemos results como lista
        return {
            "results": [{
                "document": document,
                "grade": True
            }]
        }
    else:
        print("---GRADE: DOCUMENT NOT RELEVANT---") 
        return {
            "results": [{
                "document": document,
                "grade": False
            }]
        }


@traceable(name="transform_query")
def transform_query(state: GraphState, **kwargs):
    """
    Transforma la consulta para producir una mejor pregunta (re-writer).
    """
    print("---TRANSFORM QUERY---")
    question = state["question"]
    documents = state["documents"]

    # Re-write question
    better_question = question_rewriter.invoke({"question": question})
    return {
        "documents": documents, 
        "question": better_question,
        "message_history": state.get("message_history", []),
        "thread_id": state["thread_id"],
        "next": "retrieve"
    }

@traceable(name="no_data")
def no_data(state: GraphState, **kwargs):
    """
    Este nodo se ejecuta cuando la pregunta está fuera del dominio.
    Genera una respuesta empática explicando por qué no podemos responder.
    """
    print("---NO DATA---")
    question = state["question"]

    # Generar respuesta empática
    generation = no_data_chain.invoke({"question": question, "history": state.get("message_history", [])}).content
    
    return {
        "documents": [], 
        "question": question, 
        "generation": generation,
        "message_history": state.get("message_history", []),
        "thread_id": state["thread_id"],
        "next": END
    }

@traceable(name="grade_generation")
def grade_generation_v_documents_and_question(state: GraphState, **kwargs):
    """
    Determina si la generación está fundamentada en el contenido de los documentos
    y responde la pregunta.

    Retorna la "decisión" a LangGraph indicando el próximo paso.
    """
    print("---CHECK HALLUCINATIONS---")
    question = state["question"]
    documents = state["documents"]
    generation = state["generation"]

    score = hallucination_grader.invoke(
        {"documents": documents, "generation": generation}
    )
    grade = score.binary_score

    # Mantener el estado actual
    result = {
        "question": question,
        "documents": documents,
        "generation": generation,
        "results": state.get("results", []),
        "thread_id": state["thread_id"],
        "message_history": state.get("message_history", []),
        "useful_docs": state.get("useful_docs", [])
    }

    # Check hallucination
    if grade == "yes":
        print("---DECISION: GENERATION IS GROUNDED IN DOCUMENTS---")
        # Check question-answering
        print("---GRADE GENERATION vs QUESTION---")
        score = answer_grader.invoke({"question": question, "generation": generation})
        grade = score.binary_score
        if grade == "yes":
            print("---DECISION: GENERATION ADDRESSES QUESTION---")
            result["next"] = "useful"
        else:
            print("---DECISION: GENERATION DOES NOT ADDRESS QUESTION---")
            result["next"] = "not_useful"
    else:
        print("---DECISION: GENERATION IS NOT GROUNDED IN DOCUMENTS, RE-TRY---")
        result["next"] = "not_supported"
    
    return result

@traceable(name="join_results")
def join_results(state: GraphState, **kwargs):
    print("---JOIN RESULTS---")
    
    # Primero obtenemos los documentos relevantes
    relevant_docs = [
        Document(page_content=res["document"])
        for res in state.get("results", [])
        if res.get("grade", False)
    ]
    
    # Extraemos los nombres de archivos de los documentos originales que corresponden a los relevantes
    relevant_content = {doc.page_content for doc in relevant_docs}
    useful_docs_set = set()
    for doc in state.get("documents", []):
        if doc.page_content in relevant_content:
            source = doc.metadata.get('source', '') or doc.metadata.get('file_path', '')
            if source:
                useful_docs_set.add(source)
    
    next_node = "transform_query" if not relevant_docs else "generate"
    print(f"---DECISION: {next_node.upper()}---")
    
    return {
        "documents": relevant_docs,
        "question": state["question"],
        "message_history": state.get("message_history", []),
        "thread_id": state["thread_id"],
        "useful_docs": list(useful_docs_set),  # Convertimos el set a lista para el estado
        "next": next_node
    }


@traceable(name="route_question")
def route_question(state: GraphState, **kwargs):
    """
    Route question to either RAG (vectorstore) or no_data.
    """
    print("---ROUTE QUESTION---")
    print(f"DEBUG - Estado recibido: {state}")
    question = state["question"]
    message_history = state.get("message_history", [])
    print(f"DEBUG - Llamando a question_router con question={question}, history={message_history}")
    try:
        source = question_router(question, message_history)
        print(f"DEBUG - Resultado de question_router: {source}")
        
        # Mantener el estado actual y solo actualizar el 'next'
        result = {
            "question": state["question"],
            "documents": state.get("documents", []),
            "results": state.get("results", []),
            "thread_id": state["thread_id"],
            "message_history": message_history,
            "useful_docs": state.get("useful_docs", [])
        }
        
        if source.datasource == "no_data":
            print("---ROUTE QUESTION TO NO DATA---")
            result["next"] = "no_data"
        elif source.datasource == "vectorstore":
            print("---ROUTE QUESTION TO RAG---")
            result["next"] = "retrieve"
            
        return result
    except Exception as e:
        print(f"DEBUG - Error en route_question: {str(e)}")
        raise

#
# Construimos el flujo de estados (StateGraph)
#
workflow = StateGraph(GraphState)

# Definición de nodos
workflow.add_node("no_data", no_data)
workflow.add_node("retrieve", retrieve)
workflow.add_node("fetch_history", fetch_history)
workflow.add_node("grade_document", grade_document)
workflow.add_node("join_results", join_results)
workflow.add_node("generate", generate)
workflow.add_node("transform_query", transform_query)
workflow.add_node("route_question", route_question)
workflow.add_node("grade_generation", grade_generation_v_documents_and_question)

# Definición de transiciones (“edges”) entre nodos
#
# 1) Comienzo: Ejecutar 'fetch_history' primero
workflow.add_edge(START, "fetch_history")

# Transiciones condicionales desde route_question
workflow.add_conditional_edges(
    "route_question",
    lambda s: s["next"],
    {
        "no_data": "no_data",
        "retrieve": "retrieve",
    },
)

# Transición de 'fetch_history' a 'route_question'
workflow.add_edge("fetch_history", "route_question")

# Transición de 'retrieve' a 'map_grade_document'
workflow.add_conditional_edges(
    "retrieve",
    map_grade_document,  # Función que hace el "Send" a grade_document
    {"grade_document": "grade_document"},
    # Quita el map_type y aggregator si tu versión no lo soporta
)
# Luego, para 'grade_document', simplemente haz:
workflow.add_edge("grade_document", "join_results")

# 3) No necesitamos edge directo de "grade_document" -> "join_results" 
#    porque ya lo especificamos con map_type=MapType.MAP_REDUCE (arriba).
#    Si lo dejas, puede duplicar llamadas.

# 4) 'join_results' decide el siguiente paso
workflow.add_conditional_edges(
    "join_results",
    lambda s: s["next"],  # Usar la clave 'next' para decidir
    {
        "transform_query": "transform_query",
        "generate": "generate",
    },
)

# 5) 'transform_query' -> 'retrieve' para reintentar con la pregunta mejorada
workflow.add_conditional_edges(
    "transform_query",
    lambda s: s["next"],
    {
        "retrieve": "retrieve"
    }
)

# 6) Cuando 'generate' termina, chequeamos al final si la respuesta fue útil
workflow.add_conditional_edges(
    "grade_generation",
    lambda s: s["next"],
    {
        "not_supported": "generate",
        "useful": END,
        "not_useful": "transform_query",
    },
)

# Añadir la transición directa de generate a grade_generation
workflow.add_edge("generate", "grade_generation")

# Añadir transición condicional para no_data
workflow.add_conditional_edges(
    "no_data",
    lambda s: s["next"],
    {
        END: END
    }
)

# Finalmente, compilamos la app.
app = workflow.compile()