# rag.py

import os
import time
from uuid import uuid4
from typing import Optional

from pymilvus import connections

from langchain_openai import OpenAIEmbeddings
from langchain_milvus import Milvus
from langchain.schema import BaseMessage, Document

from pydantic import BaseModel, Field

from agent.steps.query_analyzer import analyze_query

from langsmith import traceable

from rags.IRAG import IRAG
from agent.steps.generate_step import GenerateStep
from agent.steps.format_results import FormatResultsStep, SearchResult


class SearchResult(BaseModel):
    """Resultado de una sola consulta de búsqueda."""
    query: str = Field(description="La consulta que generó estos resultados")
    documents: list[Document] = Field(description="Documentos recuperados para esta consulta")


class RAG(IRAG):
    def __init__(
        self,
        URI: str,
        COLLECTION_NAME: str,
        search_kwargs: dict,
        search_type: str,
        embeddings_model_name: str,
    ):
        """
        :param URI: URI de conexión a Milvus (por ejemplo "milvus://localhost:19530").
        :param COLLECTION_NAME: Nombre de la colección en Milvus.
        :param search_kwargs: Diccionario con los argumentos de búsqueda (k, etc.).
        :param search_type: Tipo de búsqueda (por ej. "mmr", "similarity").
        :param embeddings_model_name: Nombre del modelo de embeddings de OpenAI (ej. "text-embedding-ada-002").
        """
        self.uri = URI  # Lo guardamos para poder reconectar en _safe_search
        self.collection_name = COLLECTION_NAME
        self.search_kwargs = search_kwargs

        # 1. Inicializar embeddings
        self.embeddings = OpenAIEmbeddings(model=embeddings_model_name)
        
        # 2. Crear el vectorstore con Milvus
        self.vector_store = Milvus(
            embedding_function=self.embeddings,
            connection_args={"uri": self.uri},
            collection_name=self.collection_name,
        )
        
        # 3. Configurar el retriever
        self.retriever = self.vector_store.as_retriever(
            search_type=search_type,
            search_kwargs=self.search_kwargs
        )
        
        # 4. Inicializar LLMs auxiliares
        self.analyzer_llm = analyze_query
        self.generate_step = GenerateStep()
        self.format_step = FormatResultsStep()
        
        # 5. Parámetro para reintentos de búsqueda
        self.max_retries = 3

    @traceable(run_type="retriever")
    def _safe_search(self, query: str) -> list[Document]:
        """
        Realiza la búsqueda en Milvus con reintentos automáticos en caso de error.
        """
        for attempt in range(self.max_retries):
            try:
                return self.retriever.invoke(query)
            except Exception as e:
                if attempt == self.max_retries - 1:
                    # Si llega al último intento, relanzamos la excepción
                    raise e
                print(f"[RAG::_safe_search] Búsqueda falló, intento {attempt + 1}/{self.max_retries}. Reintentando conexión...")
                try:
                    connections.disconnect("default")
                except Exception as disconnect_error:
                    print(f"Error al desconectar: {disconnect_error}")
                time.sleep(1)
                # Volver a conectar
                try:
                    connections.connect(uri=self.uri, alias="default")
                except Exception as connect_error:
                    print(f"Error al reconectar: {connect_error}")

    def add_documents(self, documents: list[Document], ids: Optional[list[str]] = None):
        """
        Agrega documentos al vectorstore (Milvus).
        :param documents: Lista de objetos Document.
        :param ids: Lista de IDs para los documentos. Genera UUIDs si no se proveen.
        """
        if ids is None:
            ids = [str(uuid4()) for _ in documents]
        self.vector_store.add_documents(documents=documents, ids=ids)

    def delete_documents(self, ids: list[str]):
        """Elimina documentos en Milvus por ID."""
        self.vector_store.delete(ids=ids)

    def delete_all_documents(self):
        """
        Elimina todos los documentos en la colección actual de Milvus.
        Se basa en la clave primaria de la colección.
        """
        try:
            pk_field = self.vector_store.col.schema.primary_field.name
            results = self.vector_store.col.query(
                expr=f"{pk_field} != ''", 
                output_fields=[pk_field]
            )
            all_ids = [str(result[pk_field]) for result in results]
            if all_ids:
                self.vector_store.delete(ids=all_ids)
        except Exception as e:
            print(f"[RAG::delete_all_documents] Error: {e}")

    def similarity_search(self, query: str, k: int = 2, filter: dict = None) -> list[Document]:
        """
        Provee un acceso directo a la búsqueda por similitud.
        :param query: Texto de la consulta.
        :param k: Cantidad de documentos a retornar.
        :param filter: Filtros adicionales para la búsqueda.
        """
        return self.vector_store.similarity_search(query, k=k, filter=filter)

    @traceable
    def generate_answer(self, question: str, history: list[BaseMessage] = None) -> tuple[str, dict]:
        """
        Realiza:
         1. Análisis de la query (QueryAnalyzer).
         2. Búsqueda en Milvus para cada subquery generada.
         3. Formateo de resultados.
         4. Generación de contexto final con ContextGenerator (o tu LLM).
         5. Retorna la respuesta final en texto y los documentos relevantes.
        """
        # 1. Obtener subqueries o query refinada
        query_analysis = self.analyzer_llm(question)

        # 2. Para cada subquery, realizar búsqueda segura (_safe_search)
        search_results = []
        queries = [question] if isinstance(query_analysis, str) else query_analysis.queries
        for query in queries:
            docs = self._safe_search(query)
            search_results.append(SearchResult(query=query, documents=docs))

        # 3. Dar formato a los resultados usando el módulo format_results
        formatter = FormatResultsStep()
        formatted_results = formatter.format_search_results(search_results)
        
        # 4. Generar la respuesta usando la info recuperada
        final_answer = self.generate_step.run(
            question=question,
            context=formatted_results
        )

        # 5. Preparar diccionario con documentos relevantes
        relevant_docs = {
            "queries": queries,
            "documents": [
                {
                    "query": result.query,
                    "docs": [
                        {
                            "content": doc.page_content,
                            "metadata": doc.metadata
                        } for doc in result.documents
                    ]
                } for result in search_results
            ]
        }
        print(relevant_docs)
        
        return final_answer, relevant_docs
    
if __name__ == "__main__":
    rag = RAG(
        URI=os.getenv("MILVUS_STANDALONE_URL"), 
        COLLECTION_NAME="real_collection", 
        search_kwargs={"k": 4, "fetch_k": 20, "ef": 100}, 
        search_type="mmr", 
        embeddings_model_name="text-embedding-3-small"
    )
    print(rag.generate_answer("¿Que es la IA?"))
