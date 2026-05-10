"""
embeddings.py — ChromaDB document ingestion and retrieval.

Loads TXT healthcare files, splits into chunks, generates embeddings
with sentence-transformers, and persists them in ChromaDB.
"""

from pathlib import Path

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

from app.config import TXT_DATA_DIR, VECTOR_STORE_DIR, settings
from app.utils import setup_logger

logger = setup_logger("embeddings")

# Module-level cache for the vector store so we don't reload on every request
_vectorstore: Chroma | None = None

COLLECTION_NAME = "healthcare_docs"


def _get_embedding_function() -> HuggingFaceEmbeddings:
    """Return the HuggingFace embedding model."""
    logger.info("Loading embedding model: %s", settings.EMBEDDING_MODEL)
    return HuggingFaceEmbeddings(
        model_name=settings.EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )


def ingest_all_documents() -> int:
    """
    Full ingestion pipeline:
    1. Load all .txt files from TXT_DATA_DIR
    2. Split into chunks
    3. Generate embeddings
    4. Persist in ChromaDB

    Returns
    -------
    int
        Number of chunks indexed.
    """
    global _vectorstore

    txt_files = list(TXT_DATA_DIR.rglob("*.txt"))
    if not txt_files:
        raise FileNotFoundError(
            f"No .txt files found in {TXT_DATA_DIR}. "
            "Run XML conversion first (POST /ingest)."
        )

    logger.info("Loading %d TXT files from %s", len(txt_files), TXT_DATA_DIR)

    # Load documents
    loader = DirectoryLoader(
        str(TXT_DATA_DIR),
        rglob="*.txt",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"},
        show_progress=True,
    )
    documents = loader.load()
    logger.info("Loaded %d documents.", len(documents))

    # Split into chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_documents(documents)
    logger.info("Split into %d chunks (size=%d, overlap=%d).",
                len(chunks), settings.CHUNK_SIZE, settings.CHUNK_OVERLAP)

    # Generate embeddings and store in ChromaDB
    embedding_fn = _get_embedding_function()

    _vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embedding_fn,
        collection_name=COLLECTION_NAME,
        persist_directory=str(VECTOR_STORE_DIR),
    )

    logger.info("ChromaDB persisted to %s — %d chunks indexed.",
                VECTOR_STORE_DIR, len(chunks))
    return len(chunks)


def get_vectorstore() -> Chroma:
    """
    Return the ChromaDB vector store, loading from disk if necessary.
    """
    global _vectorstore

    if _vectorstore is not None:
        return _vectorstore

    # Try loading from persisted directory
    if not VECTOR_STORE_DIR.exists() or not any(VECTOR_STORE_DIR.iterdir()):
        raise FileNotFoundError(
            "Vector store not found. Run ingestion first (POST /ingest)."
        )

    embedding_fn = _get_embedding_function()
    _vectorstore = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embedding_fn,
        persist_directory=str(VECTOR_STORE_DIR),
    )
    logger.info("Loaded ChromaDB from %s", VECTOR_STORE_DIR)
    return _vectorstore


def get_retriever(k: int | None = None):
    """
    Return a LangChain retriever backed by ChromaDB.

    Parameters
    ----------
    k : int, optional
        Number of documents to retrieve.  Defaults to config RETRIEVER_K.
    """
    vs = get_vectorstore()
    top_k = k or settings.RETRIEVER_K
    return vs.as_retriever(search_type="similarity", search_kwargs={"k": top_k})
