from notion_api import fetch_all_pages
from langchain_text_splitters import RecursiveCharacterTextSplitter

def ingest_notion():
    pages = fetch_all_pages()
    documents = []

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100
    )

    for page in pages:
        chunks = splitter.split_text(page["content"])
        for chunk in chunks:
            documents.append({
                "text": chunk,
                "metadata": {
                    "page_id": page["id"],
                    "title": page["title"]
                }
            })

    return documents
