from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from backend.data.splitters.semantic_splitter import semantic_split
from backend.data.utils.keyword_extractor import extract_keywords
import os

# Cargar variables de entorno al inicio
load_dotenv(os.path.join(os.path.dirname(__file__), "../.env"))

# Ruta al documento de prueba
TEST_DOC = os.path.join(os.path.dirname(__file__), "raw/¿Qué es el aprendizaje profundo_ - IBM.pdf")

def add_keywords_to_chunks(chunks):
    """Agrega keywords como metadata a cada chunk."""
    print("\nExtrayendo keywords para cada chunk...")
    for i, chunk in enumerate(chunks, 1):
        print(f"Procesando chunk {i}/{len(chunks)}...")
        try:
            # Extraer keywords y limitar a 10 antes de asignarlas
            raw_keywords = extract_keywords(chunk.page_content)
            # Asegurarnos de que no haya más de 10 keywords
            keywords = raw_keywords[:10] if raw_keywords else []
            chunk.metadata['keywords'] = keywords
        except Exception as e:
            print(f"Error al extraer keywords del chunk {i}: {str(e)}")
            chunk.metadata['keywords'] = []
    return chunks

def print_chunk_info(chunk, i, total):
    print(f"\n{'='*80}")
    print(f"CHUNK {i}/{total}")
    print(f"{'='*80}")
    
    # Mostrar keywords primero para mejor visibilidad
    print("\nKEYWORDS:")
    if 'keywords' in chunk.metadata:
        print(", ".join(chunk.metadata['keywords']))
    
    # Mostrar otros metadatos
    print("\nOTROS METADATOS:")
    for key, value in chunk.metadata.items():
        if key != 'keywords':
            print(f"{key}: {value}")
    
    # Mostrar contenido del chunk
    print("\nCONTENIDO:")
    print("-" * 40)
    print(chunk.page_content)
    print("-" * 40)
    print(f"Longitud del chunk: {len(chunk.page_content)} caracteres")

def test_chunking():
    print(f"Loading test document: {TEST_DOC}")
    loader = PyPDFLoader(TEST_DOC)
    docs = loader.load()
    print(f"Document loaded: {len(docs)} pages\n")

    print("Applying semantic chunking...")
    chunks = semantic_split(docs)
    print(f"Chunks generated: {len(chunks)}")
    
    # Agregar keywords a los chunks
    chunks = add_keywords_to_chunks(chunks)

    # Visualización interactiva de chunks
    current_chunk = 0
    total_chunks = len(chunks)

    while True:
        if current_chunk < total_chunks:
            print_chunk_info(chunks[current_chunk], current_chunk + 1, total_chunks)
            
            action = input("\n[Enter] Siguiente chunk, [B] Chunk anterior, [Q] Salir: ").lower()
            
            if action == 'q':
                break
            elif action == 'b' and current_chunk > 0:
                current_chunk -= 1
            elif action == '':
                current_chunk += 1
        else:
            print("\nNo hay más chunks para mostrar.")
            if input("\nPresiona [B] para ver el chunk anterior o cualquier otra tecla para salir: ").lower() == 'b':
                current_chunk -= 1
            else:
                break

if __name__ == "__main__":
    test_chunking() 