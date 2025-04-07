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
            
            # Usar 'authors' en lugar de 'author' para ser consistente con el formato de metadatos
            authors = metadata.get('authors', ['Autor desconocido'])
            author_str = ", ".join(authors) if isinstance(authors, list) else authors
            
            creation_date = metadata.get('creationDate', None)
            # Intentar obtener el año directamente
            year = metadata.get('publication_year', None)
            if year is None and creation_date:
                year = extract_year_from_creation_date(creation_date)
            
            # Include all metadata in a structured way
            metadata_dict = {
                **metadata,
                'source': os.path.basename(metadata.get('source', '')),
                'title': title,
                'authors': authors,
                'year': year
            }
            
            metadata_str = f"---- Context METADATA ----\n{str(metadata_dict)}"
            content_str = f"---- Context Start ----\n{doc.page_content}\n---- Context End ----"
            formatted_results.append(f"{metadata_str}\n{content_str}")
        return formatted_results

class RAG():
    def __init__(self, collection_name: str = "knowledge_base_collection", k: int = 4):
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        
        # En Milvus/langchain-milvus actual no se pueden definir campos de metadatos explícitamente
        # a través del constructor, tendremos que asegurarnos de que los metadatos se guarden 
        # correctamente durante el proceso de add_documents
        
        retries = 3
        while retries > 0:
            try:
                self.vector_store = Milvus(
                    embedding_function=self.embeddings,
                    connection_args={"uri": os.getenv("MILVUS_STANDALONE_URL")},
                    collection_name=collection_name,
                    search_params={"ef": 40}
                )
                
                # Configurar el retriever para usar MMR sin búsqueda por file_path
                self.retriever = self.vector_store.as_retriever(
                    search_type="mmr", 
                    search_kwargs={
                        "k": k,  # número de resultados finales
                        "fetch_k": 20,  # número de resultados iniciales de donde MMR seleccionará
                        # Usar 'source' en lugar de 'file_path'
                        "filter_keys": ["source"]  # Especificar explícitamente que use 'source' para filtros
                    }
                )
                break
            except Exception as e:
                retries -= 1
                if retries == 0:
                    raise e
                print(f"Error al inicializar Milvus: {e}")
                time.sleep(2) 
        
        self.rag_response_generator = RAGResponseGenerator()
        self.rag_query_analyzer = RAGQueryAnalyzer()
        
        self.max_retries = 3

    def add_documents(self, documents: list, ids: list = None):
        if ids is None:
            ids = [str(uuid4()) for _ in range(len(documents))]
        
        # Añadir barra de progreso al añadir documentos
        print("Añadiendo documentos a la colección de vectores...")
        
        # Imprimir ejemplo de metadatos para verificar que existan antes de la inserción
        if documents:
            print("\nEJEMPLO DE METADATOS ANTES DE INSERCIÓN:")
            for key, value in documents[0].metadata.items():
                print(f"  {key}: {value}")
        
        # Verificar y corregir metadatos para asegurar compatibilidad con Milvus
        print("\nProcesando metadatos para compatibilidad con Milvus...")
        for doc in documents:
            # Asegurar que los metadatos existan
            if not hasattr(doc, 'metadata') or not doc.metadata:
                doc.metadata = {}
            
            # Crear un metadata_dict plano con todos los campos necesarios
            flat_metadata = {}
            
            # Procesar metadatos clave
            # 1. Título
            if 'title' in doc.metadata and doc.metadata['title']:
                flat_metadata['title'] = str(doc.metadata['title'])
            else:
                flat_metadata['title'] = 'Título desconocido'
                
            # 2. Autores
            if 'authors' in doc.metadata:
                if isinstance(doc.metadata['authors'], list):
                    flat_metadata['authors'] = ', '.join(str(a) for a in doc.metadata['authors'])
                else:
                    flat_metadata['authors'] = str(doc.metadata['authors'])
            else:
                flat_metadata['authors'] = 'Autor desconocido'
                
            # 3. Año de publicación
            if 'publication_year' in doc.metadata and doc.metadata['publication_year']:
                flat_metadata['publication_year'] = str(doc.metadata['publication_year'])
            else:
                flat_metadata['publication_year'] = 'Desconocido'
                
            # 4. Fuente/origen
            if 'source' in doc.metadata and doc.metadata['source']:
                flat_metadata['source'] = str(doc.metadata['source'])
                # Añadir file_path como alias de source para mantener compatibilidad
                flat_metadata['file_path'] = str(doc.metadata['source'])
            else:
                flat_metadata['source'] = 'Desconocido'
                flat_metadata['file_path'] = 'Desconocido'
                
            # 5. Página
            if 'page' in doc.metadata and doc.metadata['page']:
                flat_metadata['page'] = str(doc.metadata['page'])
            else:
                flat_metadata['page'] = '0'
                
            # 6. Total de páginas
            if 'total_pages' in doc.metadata and doc.metadata['total_pages']:
                flat_metadata['total_pages'] = str(doc.metadata['total_pages'])
            else:
                flat_metadata['total_pages'] = '0'
            
            # Reemplazar los metadatos originales con los planos
            doc.metadata = flat_metadata
            
            # Imprimir un ejemplo para diagnóstico
            if doc == documents[0]:
                print("\nMETADATOS PROCESADOS (EJEMPLO):")
                for key, value in doc.metadata.items():
                    print(f"  {key}: {value}")
        
        # Si hay muchos documentos, mejor procesarlos en lotes para mostrar el progreso
        batch_size = 50  # Ajustar según sea necesario
        
        # Calcular número de lotes
        num_batches = (len(documents) + batch_size - 1) // batch_size
        
        print("\nGuardando documentos en Milvus...")
        for i in tqdm(range(num_batches), desc="Añadiendo documentos", unit="batch"):
            # Calcular índices de inicio y fin para el lote actual
            start_idx = i * batch_size
            end_idx = min((i + 1) * batch_size, len(documents))
            
            # Obtener el lote actual de documentos e IDs
            docs_batch = documents[start_idx:end_idx]
            ids_batch = ids[start_idx:end_idx]
            
            # Añadir el lote a la base de vectores
            try:
                self.vector_store.add_documents(documents=docs_batch, ids=ids_batch)
            except Exception as e:
                print(f"Error al añadir lote {i+1}/{num_batches}: {e}")
                # Intentar imprimir los metadatos del primer documento del lote para diagnóstico
                if docs_batch:
                    print(f"Metadatos del primer documento del lote: {docs_batch[0].metadata}")
            
        # Verificar si se guardó correctamente
        print("\nVerificando almacenamiento en Milvus...")
        try:
            test_query = "test"
            results = self.similarity_search(test_query, k=1)
            if results:
                print("\nMETADATOS RECUPERADOS DE MILVUS:")
                for key, value in results[0].metadata.items():
                    print(f"  {key}: {value}")
                
                # Intentar imprimir el esquema de la colección
                try:
                    print("\nESQUEMA DE LA COLECCIÓN:")
                    schema_fields = self.vector_store.col.schema.fields
                    for field in schema_fields:
                        print(f"  {field.name}: {field.dtype}")
                except Exception as schema_error:
                    print(f"No se pudo obtener el esquema: {schema_error}")
            else:
                print("No se pudieron recuperar documentos de la base de datos.")
        except Exception as e:
            print(f"Error al verificar almacenamiento en Milvus: {e}")

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
        # Si hay un filtro y contiene 'file_path', convertirlo a 'source'
        if filter and 'file_path' in filter:
            filter['source'] = filter.pop('file_path')
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
