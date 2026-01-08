import argparse
import json
import os
from dotenv import load_dotenv
from upstash_vector import Index, Vector
from chunk_markdown import chunk_markdown_file, gather_markdown_files

load_dotenv(override=True)


def load_chunks_from_markdown(input_path: str = "data", max_chars: int = 700, overlap: int = 100):
    """Lit les fichiers Markdown et génère les chunks en mémoire (sans JSON intermédiaire)."""
    files = gather_markdown_files(input_path)
    if not files:
        print(f"❌ Aucun fichier .md trouvé dans: {input_path}")
        return []
    all_chunks = []
    for path in files:
        file_chunks = chunk_markdown_file(path, max_chars=max_chars, overlap=overlap)
        all_chunks.extend(file_chunks)
    return all_chunks


def index_chunks_to_upstash(chunks, batch_size=100):
    """Indexe les chunks dans Upstash Vector par batch."""
    # Initialiser l'index Upstash
    index = Index(
        url=os.getenv("UPSTASH_VECTOR_REST_URL"),
        token=os.getenv("UPSTASH_VECTOR_REST_TOKEN")
    )
    
    print(f"Indexation de {len(chunks)} chunks dans Upstash...")
    
    # Créer les vecteurs
    vectors = [
        Vector(
            id=chunk["id"],
            data=chunk["text"],
            metadata=chunk["metadata"]
        )
        for chunk in chunks
    ]
    
    # Indexer par batch pour éviter les timeouts
    total_indexed = 0
    for i in range(0, len(vectors), batch_size):
        batch = vectors[i:i + batch_size]
        result = index.upsert(vectors=batch)
        total_indexed += len(batch)
        print(f"  Batch {i//batch_size + 1}: {len(batch)} vecteurs indexés (total: {total_indexed}/{len(vectors)})")
    
    print(f"\n✓ Indexation terminée: {len(vectors)} vecteurs dans Upstash")
    return len(vectors)


def test_search(query: str = "compétences en Python"):
    """Teste une recherche dans l'index."""
    index = Index(
        url=os.getenv("UPSTASH_VECTOR_REST_URL"),
        token=os.getenv("UPSTASH_VECTOR_REST_TOKEN")
    )
    
    print(f"\nTest de recherche: '{query}'")
    results = index.query(
        data=query,
        top_k=3,
        include_metadata=True,
        include_data=True
    )
    
    print(f"\nRésultats trouvés: {len(results)}")
    for i, result in enumerate(results, 1):
        print(f"\n--- Résultat {i} (score: {result.score:.4f}) ---")
        print(f"ID: {result.id}")
        print(f"Source: {result.metadata.get('source', 'N/A')}")
        print(f"Section: {result.metadata.get('section_path', 'N/A')}")
        if result.data:
            text_preview = result.data[:200] if len(result.data) > 200 else result.data
            print(f"Texte: {text_preview}...")
        else:
            print(f"Texte: [Non disponible]")


def main():
    # CLI args
    parser = argparse.ArgumentParser(description="Indexer directement les fichiers Markdown dans Upstash (sans JSONL)")
    parser.add_argument("--input", default="data", help="Dossier ou fichier Markdown à indexer (défaut: data)")
    parser.add_argument("--max_chars", type=int, default=700, help="Taille max par chunk (défaut: 700)")
    parser.add_argument("--overlap", type=int, default=100, help="Chevauchement entre chunks (défaut: 100)")
    parser.add_argument("--batch_size", type=int, default=100, help="Taille des batchs pour upsert (défaut: 100)")
    parser.add_argument("--query", default="compétences en Python", help="Requête de test après indexation")
    args = parser.parse_args()

    # Vérifier les variables d'environnement
    if not os.getenv("UPSTASH_VECTOR_REST_URL"):
        print("❌ UPSTASH_VECTOR_REST_URL non défini dans .env")
        return
    if not os.getenv("UPSTASH_VECTOR_REST_TOKEN"):
        print("❌ UPSTASH_VECTOR_REST_TOKEN non défini dans .env")
        return

    # Générer les chunks depuis Markdown
    chunks = load_chunks_from_markdown(args.input, max_chars=args.max_chars, overlap=args.overlap)
    print(f"✓ {len(chunks)} chunks générés depuis {args.input}")

    if not chunks:
        return

    # Indexer dans Upstash
    index_chunks_to_upstash(chunks, batch_size=args.batch_size)

    # Test de recherche
    test_search(args.query)


if __name__ == "__main__":
    main()
