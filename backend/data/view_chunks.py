from dotenv import load_dotenv
from agent.rag import RAG

# Cargar variables de entorno
load_dotenv()

def print_chunk_info(chunk, i, total):
    print(f"\n{'='*80}")
    print(f"CHUNK {i}/{total}")
    print(f"{'='*80}")
    
    # Mostrar keywords primero para mejor visibilidad
    print("\nKEYWORDS:")
    if 'keywords' in chunk.metadata:
        print(", ".join(chunk.metadata['keywords']))
    else:
        print("No hay keywords disponibles")
    
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

def view_chunks():
    # Inicializar RAG
    rag = RAG()
    
    # Obtener todos los documentos usando similarity_search con una query genérica
    print("Recuperando chunks de la base de datos...")
    try:
        # Usamos una query genérica y un k alto para obtener todos los documentos
        chunks = rag.similarity_search("", k=1000)
        total_chunks = len(chunks)
        print(f"Total de chunks encontrados: {total_chunks}")
        
        if total_chunks == 0:
            print("No hay chunks almacenados en la base de datos.")
            return
        
        # Visualización interactiva de chunks
        current_chunk = 0

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
    except Exception as e:
        print(f"Error al recuperar los chunks: {str(e)}")

if __name__ == "__main__":
    view_chunks() 