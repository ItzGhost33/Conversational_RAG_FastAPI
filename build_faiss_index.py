import os
import csv
import json
import numpy as np
import faiss
import torch
from sentence_transformers import SentenceTransformer

# ---------------------------------------------------------------------------
# 1) Configuration
# ---------------------------------------------------------------------------

# 1A. Force single-threaded to reduce concurrency issues
torch.set_num_threads(1)
faiss.omp_set_num_threads(1)

# 1B. Use a smaller embedding model (fewer dimensions)
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
model = SentenceTransformer(EMBEDDING_MODEL)

# This model is 384-dim, not 768
VECTOR_DIM = 384

DATA_FOLDER = "data"             
INDEX_OUTPUT_FILE = "faiss_index.bin"
METADATA_OUTPUT_FILE = "docs_metadata.json"

# Adjust chunking to smaller pieces to reduce memory overhead
CHUNK_SIZE = 100
CHUNK_OVERLAP = 20

def chunk_text(text, chunk_size=100, overlap=20):
    """Split text into overlapping chunks of ~chunk_size words."""
    words = text.split()
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk_words = words[start:end]
        joined = " ".join(chunk_words).strip()
        if joined:
            yield joined
        start += (chunk_size - overlap)

docs_embeddings = []
docs_metadata = []
faiss_index = None

def process_csv_file(csv_path):
    """Reads a CSV, does chunking + embedding for each row."""
    import csv
    from pathlib import Path

    file_name = Path(csv_path).name
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row_id, row in enumerate(reader):
            # Attempt to read from common columns
            text_val = row.get("Sentence", "") or row.get("segment", "") or row.get("text", "")
            text_val = text_val.strip()
            if not text_val:
                continue

            # Overlapping chunking
            for chunk in chunk_text(text_val, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
                emb = model.encode(chunk)
                # Convert to float32 to reduce memory
                emb = emb.astype(np.float32)
                docs_embeddings.append(emb)
                docs_metadata.append({
                    "text": chunk,
                    "source": f"{file_name} row {row_id}"
                })

def main():
    # 1) Gather CSVs from data folder
    if not os.path.isdir(DATA_FOLDER):
        print(f"❌ Data folder '{DATA_FOLDER}' does not exist. Exiting.")
        return

    csv_files = [f for f in os.listdir(DATA_FOLDER) if f.endswith(".csv")]
    if not csv_files:
        print(f"❌ No CSV files found in '{DATA_FOLDER}'. Exiting.")
        return

    total_chunks = 0
    for csv_file in csv_files:
        csv_path = os.path.join(DATA_FOLDER, csv_file)
        print(f"Processing: {csv_file} ...")
        process_csv_file(csv_path)
        print(f"   -> Current total embeddings: {len(docs_embeddings)}")

    if not docs_embeddings:
        print("❌ No text found in any CSV. Exiting.")
        return

    # 2) Build FAISS index
    arr = np.array(docs_embeddings, dtype=np.float32)
    index = faiss.IndexFlatIP(VECTOR_DIM)  # inner product for dot-product sim
    index.add(arr)
    print(f"✅ Built FAISS index with {index.ntotal} vectors, dimension={VECTOR_DIM}.")

    # 3) Save the FAISS index
    faiss.write_index(index, INDEX_OUTPUT_FILE)
    print(f"✅ Saved FAISS index to '{INDEX_OUTPUT_FILE}'")

    # 4) Save metadata
    with open(METADATA_OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(docs_metadata, f, indent=2)
    print(f"✅ Saved metadata with {len(docs_metadata)} entries to '{METADATA_OUTPUT_FILE}'")

if __name__ == "__main__":
    main()
