from rag.notion_ingest import ingest_notion
from rag.vector_store import build_vector_store

def main():
    documents = ingest_notion()
    build_vector_store(documents)
    print("✅ RAG index built")

if __name__ == "__main__":
    main()
