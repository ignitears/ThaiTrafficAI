import json
import os
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

def create_index():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    # Point to your newly formatted database
    json_path = os.path.join(base_dir, "rag_database.json")
    faiss_path = os.path.join(base_dir, "vector_index.faiss")
    
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    # Combine the source page and the content for better contextual embeddings
    texts = [f"อ้างอิงจาก {item['source']}: {item['content']}" for item in data]
    
    # Load the multilingual model
    model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    
    print("Generating vector embeddings... this might take a moment.")
    embeddings = model.encode(texts, show_progress_bar=True)
    
    # Build and save the FAISS index
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(embeddings).astype("float32"))
    
    faiss.write_index(index, faiss_path)
    print(f"Success! FAISS vector index saved to {faiss_path}")

if __name__ == "__main__":
    create_index()