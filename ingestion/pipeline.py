from loaders.loader_manager import load_source
from ingestion.chunker import split_documents
from ingestion.vector_store import create_vector_store


def run_ingestion(source_type, source):
    # 1. Load source
    documents = load_source(source_type, source)
    print(f"Loaded documents: {len(documents)}")

    # 2. Split into chunks
    chunks = split_documents(documents)
    print(f"Created chunks: {len(chunks)}")

    # 3. Create embeddings and store in ChromaDB
    vector_store = create_vector_store(chunks)

    print("Documents stored in ChromaDB successfully!")

    return vector_store