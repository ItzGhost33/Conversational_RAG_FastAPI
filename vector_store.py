import os
import json
import pandas as pd
import json
import pandas as pd
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document


embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

DATA_FOLDER = "data"
CHUNK_SIZE = 100
CHUNK_OVERLAP = 20
OUTPUT_JSON = "chunked_data.json"
INDEX_FOLDER = "faiss_index"

EMBEDDING_MODEL = "all-MiniLM-L6-v2"
VECTOR_DIM = 384


all_docs = []
json_data = []

for file in os.listdir(DATA_FOLDER):
    if file.endswith(".csv"):
        file_path = os.path.join(DATA_FOLDER, file)
        df = pd.read_csv(file_path)

        for idx, row in df.iterrows():
            raw_text = row.get("Sentence", "") or row.get("text", "") or row.get("segment", "")
            if not isinstance(raw_text, str):
                continue
            raw_text = raw_text.strip()
            if not raw_text:
                continue

            all_docs.append(Document(page_content=raw_text, metadata={}))

            json_data.append({
                "text": raw_text,
                "source": f"{file} row {idx+1}"
            })

with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
    json.dump(json_data, f, indent=2)



# Build FAISS index with raw text only
vectorstore = FAISS.from_documents(all_docs, embedding_model)
vectorstore.save_local(INDEX_FOLDER)

print(f"✅ FAISS index built from {len(all_docs)} raw texts (no metadata).")
print(f"📁 JSON with text + source saved at: {OUTPUT_JSON}")
print(f"💾 FAISS index saved to: {INDEX_FOLDER}")