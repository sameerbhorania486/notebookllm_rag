from langchain_chroma import Chroma
from ingestion.embedding import create_embeddings

CHROMA_PATH = "chroma_db"


def create_vector_store(documents):

    embeddings = create_embeddings()

    for document in documents:

        if "source_id" not in document.metadata:
            document.metadata["source_id"] = "default"

        if "source_type" not in document.metadata:
            document.metadata["source_type"] = "unknown"

    vector_store = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=CHROMA_PATH
    )

    return vector_store


def load_vector_store():

    embeddings = create_embeddings()

    vector_store = Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=embeddings
    )

    return vector_store