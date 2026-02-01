from pathlib import Path


def get_chunks():
    """Lecture des fichiers .md du dossier 'data' et renvoie une liste de chunks sans boucle infinie."""
    all_chunks = []
    chemin_données = Path("data")

    for file in chemin_données.glob("*.md"):
        text = file.read_text(encoding="utf-8")
        file_chunks = [chunk.strip() for chunk in text.split("##") if chunk.strip()]

        for i, chunk in enumerate(file_chunks, 1):
            chunk_obj = {
                "source_file": file.stem,
                "index": i,
                "text": chunk
            }
            all_chunks.append(chunk_obj)
            print(f"Chunk {i} de {file.stem}:\n{chunk}\n")

    print("Nombre total de chunks créés :", len(all_chunks))
    return all_chunks


if __name__ == "__main__":
    get_chunks()