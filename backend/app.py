from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from typing import List
import os
import hashlib

from backend.rag_chain import create_llm, create_rag_chain
from retrieval.retriever import create_retriever

from ingestion.chunker import split_documents
from ingestion.vector_store import (
    create_vector_store,
    load_vector_store
)

from loaders.web_loader import load_web
from loaders.youtube_loader import load_youtube
from loaders.text_loader import load_text
from loaders.csv_loader import load_csv
from loaders.pdf_loader import load_pdf


# =========================================================
# APP
# =========================================================

app = FastAPI(
    title="NotebookLLM RAG API",
    description="RAG backend for NotebookLLM-style application"
)


VECTOR_STORE = None


# =========================================================
# REQUEST MODELS
# =========================================================

class ChatRequest(BaseModel):
    question: str
    source_ids: List[str]


class IngestRequest(BaseModel):
    documents: List[str]


# =========================================================
# SOURCE ID
# =========================================================

def generate_source_id(source: str):

    return hashlib.md5(
        source.strip().encode()
    ).hexdigest()


# =========================================================
# STARTUP
# =========================================================

@app.on_event("startup")
def startup_event():

    global VECTOR_STORE

    if os.path.exists("chroma_db"):

        try:

            VECTOR_STORE = load_vector_store()

            print(
                "Existing Chroma database loaded successfully."
            )

        except Exception as e:

            VECTOR_STORE = None

            print(
                f"Chroma load error: {e}"
            )

    else:

        print(
            "No existing Chroma database found."
        )


# =========================================================
# ROOT
# =========================================================

@app.get("/")
def root():

    return {
        "message": "NotebookLLM RAG API is running"
    }


# =========================================================
# INGEST
# =========================================================

@app.post("/ingest")
def ingest(request: IngestRequest):

    global VECTOR_STORE

    if not request.documents:

        return {
            "error": "No documents provided."
        }

    all_docs = []
    source_ids = []

    for source in request.documents:

        source = source.strip()

        if not source:
            continue

        source_id = generate_source_id(
            source
        )

        source_ids.append(
            source_id
        )

        # -------------------------------------------------
        # YOUTUBE
        # -------------------------------------------------

        if (
            "youtube.com" in source
            or
            "youtu.be" in source
        ):

            documents = load_youtube(
                source
            )

            source_type = "youtube"

        # -------------------------------------------------
        # WEBSITE
        # -------------------------------------------------

        elif (
            source.startswith("http://")
            or
            source.startswith("https://")
        ):

            documents = load_web(
                source
            )

            source_type = "website"

        # -------------------------------------------------
        # PDF
        # -------------------------------------------------

        elif source.lower().endswith(".pdf"):

            documents = load_pdf(
                source
            )

            source_type = "pdf"

        # -------------------------------------------------
        # CSV
        # -------------------------------------------------

        elif source.lower().endswith(".csv"):

            documents = load_csv(
                source
            )

            source_type = "csv"

        # -------------------------------------------------
        # TXT
        # -------------------------------------------------

        elif source.lower().endswith(".txt"):

            documents = load_text(
                source
            )

            source_type = "text"

        else:

            raise ValueError(
                f"Unsupported source type: {source}"
            )

        # -------------------------------------------------
        # METADATA
        # -------------------------------------------------

        for doc in documents:

            doc.metadata["source_id"] = source_id
            doc.metadata["source_type"] = source_type
            doc.metadata["source_url"] = source

        all_docs.extend(
            documents
        )

    # =====================================================
    # CHECK
    # =====================================================

    if not all_docs:

        return {
            "error": "No documents could be loaded."
        }

    # =====================================================
    # CHUNKING
    # =====================================================

    chunks = split_documents(
        all_docs
    )

    # =====================================================
    # VECTOR STORE
    # =====================================================

    if VECTOR_STORE is None:

        VECTOR_STORE = create_vector_store(
            chunks
        )

    else:

        VECTOR_STORE.add_documents(
            chunks
        )

    # =====================================================
    # RESPONSE
    # =====================================================

    return {
        "message": "Documents successfully ingested",
        "chunks": len(chunks),
        "source_id": source_ids[0],
        "source_ids": source_ids
    }


# =========================================================
# FILE UPLOAD
# =========================================================

@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...)
):

    global VECTOR_STORE

    # -----------------------------------------------------
    # UPLOAD DIRECTORY
    # -----------------------------------------------------

    os.makedirs(
        "uploads",
        exist_ok=True
    )

    file_path = os.path.join(
        "uploads",
        file.filename
    )

    # -----------------------------------------------------
    # SAVE FILE
    # -----------------------------------------------------

    file_content = await file.read()

    with open(
        file_path,
        "wb"
    ) as buffer:

        buffer.write(
            file_content
        )

    # -----------------------------------------------------
    # SOURCE ID
    # -----------------------------------------------------

    source_id = generate_source_id(
        file.filename
    )

    # -----------------------------------------------------
    # LOAD FILE
    # -----------------------------------------------------

    if file.filename.lower().endswith(".pdf"):

        documents = load_pdf(
            file_path
        )

        source_type = "pdf"

    elif file.filename.lower().endswith(".txt"):

        documents = load_text(
            file_path
        )

        source_type = "text"

    elif file.filename.lower().endswith(".csv"):

        documents = load_csv(
            file_path
        )

        source_type = "csv"

    else:

        return {
            "error": "Unsupported file type"
        }

    # -----------------------------------------------------
    # METADATA
    # -----------------------------------------------------

    for doc in documents:

        doc.metadata["source_id"] = source_id
        doc.metadata["source_type"] = source_type
        doc.metadata["source_url"] = file.filename

    # -----------------------------------------------------
    # CHUNKING
    # -----------------------------------------------------

    chunks = split_documents(
        documents
    )

    # -----------------------------------------------------
    # VECTOR STORE
    # -----------------------------------------------------

    if VECTOR_STORE is None:

        VECTOR_STORE = create_vector_store(
            chunks
        )

    else:

        VECTOR_STORE.add_documents(
            chunks
        )

    # -----------------------------------------------------
    # RESPONSE
    # -----------------------------------------------------

    return {
        "message": "File successfully ingested",
        "filename": file.filename,
        "chunks": len(chunks),
        "source_id": source_id,
        "source_ids": [source_id]
    }


# =========================================================
# CHAT
# =========================================================

@app.post("/chat")
def chat(request: ChatRequest):

    global VECTOR_STORE

    # -----------------------------------------------------
    # CHECK VECTOR STORE
    # -----------------------------------------------------

    if VECTOR_STORE is None:

        return {
            "answer":
            "Please add a source before starting a chat."
        }

    # -----------------------------------------------------
    # CHECK SOURCE IDS
    # -----------------------------------------------------

    if not request.source_ids:

        return {
            "answer":
            "Please connect at least one source before starting a chat."
        }

    # -----------------------------------------------------
    # CREATE RETRIEVER
    # -----------------------------------------------------

    retriever = create_retriever(
        VECTOR_STORE,
        source_ids=request.source_ids,
        k=4
    )

    # -----------------------------------------------------
    # CREATE LLM
    # -----------------------------------------------------

    llm = create_llm()

    # -----------------------------------------------------
    # CREATE RAG CHAIN
    # -----------------------------------------------------

    rag_chain = create_rag_chain(
        retriever,
        llm
    )

    # -----------------------------------------------------
    # ASK QUESTION
    # -----------------------------------------------------

    answer = rag_chain(
        request.question
    )

    # -----------------------------------------------------
    # RESPONSE
    # -----------------------------------------------------

    return {
        "answer": answer,
        "source_ids": request.source_ids
    }