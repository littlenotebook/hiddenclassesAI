from rag.vector_store import similarity_search

def retrieve_context(query, k=5):
    """
    Return concatenated top-k most relevant Notion chunks.
    """
    docs = similarity_search(query, k=k)
    combined_text = "\n\n".join([doc.get("text", "") for doc in docs])
    return combined_text
