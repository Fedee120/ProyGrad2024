from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_milvus import Milvus
from uuid import uuid4
from langchain_core.messages import BaseMessage
from langchain_core.prompts import PromptTemplate
from rags.IRAG import IRAG
import os
from pydantic import BaseModel, Field
from typing import List
from pymilvus import connections
import time
from llms.context_generator import ContextGenerator
from llms.query_analyzer import QueryAnalyzer
from langchain_core.documents import Document
from langsmith import traceable

class SearchResult(BaseModel):
    """Result from a single search query"""
    query: str = Field(description="The query that produced these results")
    documents: List[Document] = Field(description="Retrieved documents for this query")

class RAG(IRAG):
    def __init__(
        self,
        URI: str,
        COLLECTION_NAME: str,
        search_kwargs: dict,
        search_type: str,
        embeddings_model_name: str,
    ):
        self.embeddings = OpenAIEmbeddings(model=embeddings_model_name)
        
        self.vector_store = Milvus(
            embedding_function=self.embeddings,
            connection_args={"uri": URI},
            collection_name=COLLECTION_NAME,
        )
        
        self.retriever = self.vector_store.as_retriever(
            search_type=search_type, search_kwargs=search_kwargs
        )
        
        self.context_llm = ContextGenerator()
        self.analyzer_llm = QueryAnalyzer()
        
        self.max_retries = 3

    @traceable(run_type="retriever")
    def _safe_search(self, query):
        for attempt in range(self.max_retries):
            try:
                return self.retriever.invoke(query)
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise e
                print(f"Search failed, attempt {attempt + 1}/{self.max_retries}. Reconnecting...")
                try:
                    connections.disconnect("default")
                except Exception as disconnect_error:
                    print(f"Error during disconnect: {disconnect_error}")
                time.sleep(1)
                try:
                    connections.connect(uri=self.uri, alias="default")
                except Exception as connect_error:
                    print(f"Error during connect: {connect_error}")

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

    @traceable
    def generate_answer(self, question: str, history: List[BaseMessage] = None):
        query_analysis = self.analyzer_llm.analyze(question, history)

        search_results = []
        for query in query_analysis.queries:
            docs = self._safe_search(query)
            search_results.append(SearchResult(
                query=query,
                documents=docs
            ))
        formatted_results = self._format_search_results(search_results)
        
        return self.context_llm.generate_context(
            question=query_analysis.updated_query,
            search_results=formatted_results
        )
