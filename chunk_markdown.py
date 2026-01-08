import argparse
import json
import os
import re
from typing import List, Dict, Tuple


HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)\s*$")


def parse_markdown_sections(text: str) -> List[Dict]:
    """Parse markdown into sections keyed by heading hierarchy.

    Returns a list of dicts with keys:
    - headings: List[Tuple[level, title]] (e.g., [(1, 'Profil'), (2, 'Identité')])
    - content: str (lines until next heading)
    """
    lines = text.splitlines()
    sections: List[Dict] = []
    current_headings: List[Tuple[int, str]] = []
    current_content: List[str] = []

    def flush_section():
        if current_content:
            sections.append({
                "headings": list(current_headings),
                "content": "\n".join(current_content).strip()
            })

    for line in lines:
        m = HEADING_RE.match(line)
        if m:
            # New heading encountered: finalize previous section
            flush_section()
            current_content = []
            hashes, title = m.groups()
            level = len(hashes)
            # Update heading stack
            # Pop any headings deeper or equal than this level
            while current_headings and current_headings[-1][0] >= level:
                current_headings.pop()
            current_headings.append((level, title.strip()))
        else:
            current_content.append(line)

    flush_section()
    # Remove empty content sections
    sections = [s for s in sections if s["content"]]
    return sections


def chunk_text(content: str, max_chars: int = 700, overlap: int = 100) -> List[str]:
    """Chunk content into pieces not exceeding max_chars. Optionally apply overlap.

    Splits primarily on paragraph boundaries (blank lines). If a single paragraph
    exceeds max_chars, further split on sentence boundaries.
    """
    # Split on paragraphs (blank line)
    paragraphs = re.split(r"\n\s*\n", content.strip())

    chunks: List[str] = []
    buffer: List[str] = []

    def push_buffer():
        if not buffer:
            return
        text = "\n\n".join(buffer).strip()
        if text:
            chunks.append(text)

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        # If single paragraph is too long, split by simple sentence boundaries
        if len(para) > max_chars:
            sentences = re.split(r"(?<=[\.!?])\s+", para)
            temp = []
            for sent in sentences:
                sent = sent.strip()
                if not sent:
                    continue
                tentative = (" ".join(temp + [sent])).strip()
                if len(tentative) <= max_chars:
                    temp.append(sent)
                else:
                    if temp:
                        buffer.append(" ".join(temp))
                        push_buffer()
                        # Apply overlap from previous chunk
                        if overlap > 0 and chunks:
                            tail = chunks[-1][-overlap:]
                            buffer = [tail]
                        else:
                            buffer = []
                        temp = [sent]
                    else:
                        # Sentence itself exceeds max_chars; hard split
                        hard = [sent[i:i+max_chars] for i in range(0, len(sent), max_chars)]
                        for piece in hard:
                            buffer.append(piece)
                            push_buffer()
                            if overlap > 0 and chunks:
                                tail = chunks[-1][-overlap:]
                                buffer = [tail]
                            else:
                                buffer = []
                        temp = []
            if temp:
                para_rebuilt = " ".join(temp)
                tentative = ("\n\n".join(buffer + [para_rebuilt])).strip()
                if len(tentative) <= max_chars:
                    buffer.append(para_rebuilt)
                else:
                    push_buffer()
                    if overlap > 0 and chunks:
                        tail = chunks[-1][-overlap:]
                        buffer = [tail, para_rebuilt]
                    else:
                        buffer = [para_rebuilt]
        else:
            tentative = ("\n\n".join(buffer + [para])).strip()
            if len(tentative) <= max_chars:
                buffer.append(para)
            else:
                push_buffer()
                # Apply overlap from previous chunk
                if overlap > 0 and chunks:
                    tail = chunks[-1][-overlap:]
                    buffer = [tail, para]
                else:
                    buffer = [para]

    push_buffer()
    return chunks


def chunk_markdown_file(path: str, max_chars: int = 700, overlap: int = 100) -> List[Dict]:
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    sections = parse_markdown_sections(text)
    output_chunks: List[Dict] = []
    base = os.path.basename(path)

    idx = 0
    for section in sections:
        chunks = chunk_text(section["content"], max_chars=max_chars, overlap=overlap)
        for c_i, c in enumerate(chunks):
            output_chunks.append({
                "id": f"{base}-{idx}",
                "text": c,
                "metadata": {
                    "source": base,
                    "section_path": " > ".join([h[1] for h in section["headings"]]),
                    "chunk_index": c_i,
                    "max_chars": max_chars,
                    "overlap": overlap,
                    "length": len(c),
                }
            })
            idx += 1

    # Annotate total chunks per source for convenience (not strictly necessary)
    total = len(output_chunks)
    for ch in output_chunks:
        ch["metadata"]["total_chunks_in_file"] = total

    return output_chunks


def gather_markdown_files(input_path: str) -> List[str]:
    if os.path.isfile(input_path):
        return [input_path]
    files: List[str] = []
    for name in os.listdir(input_path):
        if name.lower().endswith(".md"):
            files.append(os.path.join(input_path, name))
    return sorted(files)


def main():
    parser = argparse.ArgumentParser(description="Chunk Markdown files into JSONL output.")
    parser.add_argument("--input", default="data", help="Path to a markdown file or a folder containing .md files")
    parser.add_argument("--output", default=os.path.join("data", "chunks.jsonl"), help="Output JSONL file path")
    parser.add_argument("--max_chars", type=int, default=700, help="Max characters per chunk")
    parser.add_argument("--overlap", type=int, default=100, help="Character overlap between consecutive chunks")
    args = parser.parse_args()

    files = gather_markdown_files(args.input)
    if not files:
        print(f"Aucun fichier Markdown trouvé dans: {args.input}")
        return

    all_chunks: List[Dict] = []
    for path in files:
        chunks = chunk_markdown_file(path, max_chars=args.max_chars, overlap=args.overlap)
        all_chunks.extend(chunks)

    # Ensure output directory exists
    os.makedirs(os.path.dirname(args.output), exist_ok=True)

    with open(args.output, "w", encoding="utf-8") as out:
        for ch in all_chunks:
            out.write(json.dumps(ch, ensure_ascii=False) + "\n")

    print(f"Chunks écrits: {len(all_chunks)} -> {args.output}")


if __name__ == "__main__":
    main()
