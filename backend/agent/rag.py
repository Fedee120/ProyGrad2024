from langchain_openai import OpenAIEmbeddings
from langchain_milvus import Milvus
from uuid import uuid4
from langchain_core.messages import BaseMessage
import os
from pydantic import BaseModel, Field
from typing import List
from pymilvus import connections
import time
from .llms.rag_response_generator import RAGResponseGenerator
from .llms.rag_query_analyzer import RAGQueryAnalyzer
from langchain_core.documents import Document
from langsmith import traceable

class SearchResult(BaseModel):
    """Result from a single search query"""
    query: str = Field(description="The query that produced these results")
    documents: List[Document] = Field(description="Retrieved documents for this query")

class RAG():
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        
        retries = 3
        while retries > 0:
            try:
                self.vector_store = Milvus(
                    embedding_function=self.embeddings,
                    connection_args={"uri": os.getenv("MILVUS_STANDALONE_URL")},
                    collection_name="real_collection",
                    search_params={"ef": 40}
                )
                
                self.retriever = self.vector_store.as_retriever(
                    search_type="mmr", 
                    search_kwargs={
                        "k": 4,  # número de resultados finales
                        "fetch_k": 20,  # número de resultados iniciales de donde MMR seleccionará
                    }
                )
                break
            except Exception as e:
                retries -= 1
                if retries == 0:
                    raise e
                time.sleep(2) 
        
        self.rag_response_generator = RAGResponseGenerator()
        self.rag_query_analyzer = RAGQueryAnalyzer()
        
        self.max_retries = 3

    def add_documents(self, documents: list, ids: list = None):
        if ids is None:
            ids = [str(uuid4()) for _ in range(len(documents))]
        self.vector_store.add_documents(documents=documents, ids=ids)

    def delete_documents(self, ids: list):
        self.vector_store.delete(ids=ids)

    def delete_all_documents(self):
        try:
            # Get the primary key field name
            pk_field = self.vector_store.col.schema.primary_field.name
            # Query for all documents
            results = self.vector_store.col.query(
                expr=f"{pk_field} != ''", 
                output_fields=[pk_field]
            )
        
            # Extract IDs from results
            all_ids = []
            for result in results:
                all_ids.append(str(result[pk_field]))
            
            if all_ids:
                self.vector_store.delete(ids=all_ids)
        except Exception as e:
            print(f"Error deleting documents: {e}")

    def similarity_search(self, query: str, k: int = 2, filter: dict = None):
        results = self.vector_store.similarity_search(query, k=k, filter=filter)
        return results

    def _format_search_results(self, results: List[SearchResult]) -> str:
        formatted = []
        for result in results:
            for doc in result.documents:
                metadata_str = f"---- Context METADATA ----\n{str({**doc.metadata, 'source': os.path.basename(doc.metadata.get('source', ''))} if doc.metadata else {})}"
                content_str = f"---- Context Start ----\n{doc.page_content}\n---- Context End ----"
                formatted.append(f"{metadata_str}\n{content_str}")
        return "\n\n".join(formatted)

    @traceable(run_type="retriever")
    def retrieve(self, query):
        return self.retriever.invoke(query)

    @traceable
    def generate_answer(self, question: str, history: List[BaseMessage] = None):
        query_analysis = self.rag_query_analyzer.analyze(question, history)

        search_results = []
        for query in query_analysis.queries:
            docs = self.retrieve(query)
            search_results.append(SearchResult(
                query=query,
                documents=docs
            ))
        formatted_results = self._format_search_results(search_results)
        
        return self.rag_response_generator.generate_response(
            question=query_analysis.updated_query,
            search_results=formatted_results
        )
