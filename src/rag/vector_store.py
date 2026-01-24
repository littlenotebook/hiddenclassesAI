# src/rag/vector_store.py

import os
import faiss
import numpy as np
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

# Create OpenRouter client
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENROUTER_API_KEY"]
)

INDEX_FILE = "rag_index.faiss"
METADATA_FILE = "rag_index_meta.npy"

# Helper: get embeddings from OpenRouter
def embed_texts(texts, model="text-embedding-3-small"):
    response = client.embeddings.create(
        model=model,
        input=texts
    )
    return [d.embedding for d in response.data]

# Build vector store from documents
def build_vector_store(documents):
    texts = [d["text"] for d in documents]
    metadatas = [d["metadata"] for d in documents]

    print(f"Embedding {len(texts)} documents...")
    vectors = embed_texts(texts)

    dim = len(vectors[0])
    index = faiss.IndexFlatL2(dim)
    index.add(np.array(vectors).astype("float32"))

    # Save index & metadata
    faiss.write_index(index, INDEX_FILE)
    np.save(METADATA_FILE, metadatas)

    print(f"✅ RAG index built with {len(texts)} vectors")
    return index, metadatas

# Load vector store
def load_vector_store():
    index = faiss.read_index(INDEX_FILE)
    metadatas = np.load(METADATA_FILE, allow_pickle=True)
    return index, metadatas

# Retrieve top-k similar documents
def similarity_search(query, k=5, model="text-embedding-3-small"):
    index, metadatas = load_vector_store()
    query_vec = np.array(embed_texts([query], model=model)).astype("float32")
    distances, ids = index.search(query_vec, k)
    results = [metadatas[i] for i in ids[0]]
    return results
