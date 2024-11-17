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
from .query_analyzer import QueryAnalyzer
from langchain_core.documents import Document

# Define the schema for structured output
class ContextItem(BaseModel):
    """A piece of context used to answer the question"""
    content: str = Field(description="The content of the context")
    source: str = Field(description="The name of the source that the context was retrieved from")

class QAResponse(BaseModel):
    """Response format for question answering"""
    answer: str = Field(description="The answer to the question based on the provided context")
    context: List[ContextItem] = Field(description="List of context pieces that were actually used to form the answer, if it was not used do not return it")
    
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
        
        # Initialize LLM with structured output
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0
        ).with_structured_output(QAResponse)
        
        self.query_analyzer = QueryAnalyzer()
        
        # Update prompt to handle multiple search results
        self.prompt_template = """You are an assistant for question-answering tasks.
        Below you will find multiple search results for different aspects of the user's question.
        Use these search results to provide a comprehensive answer.
        
        Question: {question}
        Context: {search_results}
        
        Remember:
        - Only use information from the provided search results
        - If search results don't contain relevant information, say "No information found"
        - Be clear about which parts of your answer come from which search results
        - Maintain accuracy while being helpful
        """

        self.prompt = PromptTemplate(
            input_variables=["search_results", "question"],
            template=self.prompt_template,
        )

        self.max_retries = 3

    def _safe_search(self, query):
        for attempt in range(self.max_retries):
            try:
                return self.retriever.invoke(query)
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise e
                print(f"Search failed, attempt {attempt + 1}/{self.max_retries}. Reconnecting...")
                connections.disconnect()
                time.sleep(1)
                connections.connect(uri=self.uri)

    def add_documents(self, documents: list, ids: list = None):
        if ids is None:
            ids = [str(uuid4()) for _ in range(len(documents))]
        self.vector_store.add_documents(documents=documents, ids=ids)

    def delete_documents(self, ids: list):
        self.vector_store.delete(ids=ids)

    def delete_all_documents(self):
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
                print(f"Document:")
                print(metadata_str)
                print(content_str)
                print("\n" + "="*50 + "\n")
        return "\n\n".join(formatted)

    def generate_answer(self, question: str, history: List[BaseMessage] = None):
        print("\n" + "="*50 + "\n")
        print(f"Processing question: {question}")
        
        # 1. Get optimized search queries
        query_analysis = self.query_analyzer.analyze_query(question, history)
        print(f"\nQuery analysis: {query_analysis}")
        
        # 2. Perform searches for each query
        search_results = []
        for query in query_analysis.queries:
            docs = self._safe_search(query)
            search_results.append(SearchResult(
                query=query,
                documents=docs
            ))
        
        # 3. Format results
        formatted_results = self._format_search_results(search_results)
        print(f"\nFormatted search results:\n{formatted_results}")
        
        # The response will automatically be structured according to QAResponse schema
        response = self.llm.invoke(
            self.prompt.format(
                question=query_analysis.updated_query, 
                search_results=formatted_results
            )
        )
        print("LLM Response:")
        print(response)
        print("\n" + "="*50 + "\n")
        return response
