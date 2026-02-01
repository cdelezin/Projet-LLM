from upstash_vector import Index
from chunk import get_chunks
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# import des informations d'identification
index = Index.from_env()

def index_chunks(chunks:list) -> str:
    """
    Indexe une liste de chunks dans Upstash Vector.
    Args: chunks: Liste des chunks avec structure {'source_file', 'index', 'text'}
    Returns:Message de confirmation
    """
    vectors_data = []
    
    for chunk in chunks:
        # Créer un ID unique pour chaque chunk
        chunk_id = f"{chunk['source_file']}-{chunk['index']}"
        
        # Ajouter le chunk à la liste 
        vectors_data.append({
            'id': chunk_id,
            'data': chunk['text'],
            'metadata': chunk
        })
    
    # Indexer les chunks
    index.upsert(vectors=vectors_data)
    
    return f"{len(chunks)} chunks indexés"

# Récupérer tous les chunks depuis les fichiers markdown
chunks = get_chunks()
result = index_chunks(chunks)
print(result)
