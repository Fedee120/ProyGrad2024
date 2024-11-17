from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_milvus import Milvus
from uuid import uuid4
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import HumanMessage
from rags.IRAG import IRAG
import os
from pydantic import BaseModel, Field
from typing import List

# Define the schema for structured output
class ContextItem(BaseModel):
    """A piece of context used to answer the question"""
    content: str = Field(description="The content of the context")
    source: str = Field(description="The name of the source that the context was retrieved from")

class QAResponse(BaseModel):
    """Response format for question answering"""
    answer: str = Field(description="The answer to the question based on the provided context")
    context: List[ContextItem] = Field(description="List of context pieces that were actually used to form the answer, if it was not used do not return it")
    
class RAG(IRAG):
    def __init__(
        self,
        URI: str,
        COLLECTION_NAME: str,
        search_kwargs: dict,
        search_type: str,
        llm_model_name: str,
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
            model=llm_model_name,
            temperature=0
        ).with_structured_output(QAResponse)
        
        self.prompt_template = """You are an assistant for question-answering tasks. 
        Use the following pieces of retrieved context to answer the question. 
        Do not add information that does not come from the context.
        If you don't have information or don't use any context pieces, just say "No information found".
        
        Question: {question}
        Context: {context}
        
        Respond with your answer and the specific context pieces you used, and remember to include only the context pieces that you actually used to form your answer and to respond only with the context."""

        self.prompt = PromptTemplate(
            input_variables=["context", "question"],
            template=self.prompt_template,
        )

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

    def generate_answer(self, question: str):
        print("\n" + "="*50 + "\n")
        print(f"Processing question: {question}")
        print("\n" + "="*50 + "\n")

        docs = self.retriever.invoke(question)
        print(f"Retrieved {len(docs)} documents")
        print("\n" + "="*50 + "\n")
        
        context_parts = []
        for i, doc in enumerate(docs, 1):
            metadata_str = f"---- Context {i} METADATA ----\n{str({**doc.metadata, 'source': os.path.basename(doc.metadata.get('source', ''))} if doc.metadata else {})}"
            content_str = f"---- Context {i} Start ----\n{doc.page_content}\n---- Context {i} End ----"
            context_parts.append(f"{metadata_str}\n{content_str}")
            print(f"Document {i}:")
            print(metadata_str)
            print(content_str)
            print("\n" + "="*50 + "\n")
            
        context = "\n\n".join(context_parts)
        prompt_text = self.prompt.format(context=context, question=question)
        print("Generated prompt:")
        print(prompt_text)
        print("\n" + "="*50 + "\n")
        
        # The response will automatically be structured according to QAResponse schema
        response = self.llm.invoke([HumanMessage(content=prompt_text)])
        print("LLM Response:")
        print(response)
        print("\n" + "="*50 + "\n")
        return response
