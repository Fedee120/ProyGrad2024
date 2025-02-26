from langchain_openai import OpenAIEmbeddings
from langchain_milvus import Milvus
from uuid import uuid4
from langchain_core.messages import BaseMessage
import os
from pydantic import BaseModel, Field
from typing import List
import time
from .llms.rag_response_generator import RAGResponseGenerator, extract_year_from_creation_date
from .llms.rag_query_analyzer import RAGQueryAnalyzer
from langchain_core.documents import Document
from langsmith import traceable
from tqdm import tqdm

class SearchResult(BaseModel):
    """Result from a single search query"""
    query: str = Field(description="The query that produced these results")
    documents: List[Document] = Field(description="Retrieved documents for this query")

    def formatted(self) -> List[str]:
        formatted_results = []
        for doc in self.documents:
            # Extract metadata with defaults for missing values
            metadata = doc.metadata if doc.metadata else {}
            
            # Process citation-relevant metadata
            title = metadata.get('title', os.path.basename(metadata.get('source', 'Unknown Source')))
            author = metadata.get('author', 'Unknown Author')
            creation_date = metadata.get('creationDate', None)
            year = extract_year_from_creation_date(creation_date)
            
            # Include all metadata in a structured way
            metadata_dict = {
                **metadata,
                'source': os.path.basename(metadata.get('source', '')),
                'title': title,
                'author': author,
                'year': year
            }
            
            metadata_str = f"---- Context METADATA ----\n{str(metadata_dict)}"
            content_str = f"---- Context Start ----\n{doc.page_content}\n---- Context End ----"
            formatted_results.append(f"{metadata_str}\n{content_str}")
        return formatted_results

class RAG():
    def __init__(self, collection_name: str = "knowledge_base_collection", k: int = 4):
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        
        retries = 3
        while retries > 0:
            try:
                self.vector_store = Milvus(
                    embedding_function=self.embeddings,
                    connection_args={"uri": os.getenv("MILVUS_STANDALONE_URL")},
                    collection_name=collection_name,
                    search_params={"ef": 40}
                )
                
                self.retriever = self.vector_store.as_retriever(
                    search_type="mmr", 
                    search_kwargs={
                        "k": k,  # número de resultados finales
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
        
        # Añadir barra de progreso al añadir documentos
        print("Añadiendo documentos a la colección de vectores...")
        
        # Si hay muchos documentos, mejor procesarlos en lotes para mostrar el progreso
        batch_size = 50  # Ajustar según sea necesario
        
        # Calcular número de lotes
        num_batches = (len(documents) + batch_size - 1) // batch_size
        
        for i in tqdm(range(num_batches), desc="Añadiendo documentos", unit="batch"):
            # Calcular índices de inicio y fin para el lote actual
            start_idx = i * batch_size
            end_idx = min((i + 1) * batch_size, len(documents))
            
            # Obtener el lote actual de documentos e IDs
            docs_batch = documents[start_idx:end_idx]
            ids_batch = ids[start_idx:end_idx]
            
            # Añadir el lote a la base de vectores
            self.vector_store.add_documents(documents=docs_batch, ids=ids_batch)

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

    @traceable(run_type="retriever")
    def retrieve(self, query):
        return self.retriever.invoke(query)

    @traceable
    def generate_answer(self, question: str, history: List[BaseMessage] = None):
        query_analysis = self.rag_query_analyzer.analyze(question, history)

        search_results = []
        seen_pks = set()

        for query in query_analysis.queries:
            docs = self.retrieve(query)
            
            docs = [doc for doc in docs if doc.metadata['pk'] not in seen_pks]
            seen_pks.update(doc.metadata['pk'] for doc in docs)

            search_results.append(SearchResult(
                query=query,
                documents=docs
            ))
        formatted_results = []
        for result in search_results:
            formatted_results.extend(result.formatted())
        context_str = "\n\n".join(formatted_results)
        
        return self.rag_response_generator.generate_response(
            query=query_analysis.updated_query,
            search_results=context_str
        )
