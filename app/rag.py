"""
rag.py — Retrieval-Augmented Generation pipeline.

Retrieves relevant chunks from ChromaDB, builds a context window,
and calls Ollama Mistral to generate a grounded answer.
"""

from app.embeddings import get_retriever
from app.llm import generate_answer
from app.utils import setup_logger

logger = setup_logger("rag")

FALLBACK_ANSWER = (
    "I could not find this information in the provided documents. "
    "Please try rephrasing your question or ask about a different health topic."
)


def ask_rag(question: str) -> dict:
    """
    Full RAG pipeline: retrieve → build context → generate answer.

    Parameters
    ----------
    question : str
        The user's healthcare question.

    Returns
    -------
    dict
        {"answer": str, "sources": list[str]}
    """
    try:
        retriever = get_retriever()
        docs = retriever.invoke(question)
    except FileNotFoundError:
        logger.warning("Vector store not found — returning fallback.")
        return {
            "answer": "The knowledge base has not been ingested yet. "
                      "Please trigger ingestion first (POST /ingest).",
            "sources": [],
        }
    except Exception as exc:
        logger.error("Retrieval failed: %s", exc)
        return {"answer": FALLBACK_ANSWER, "sources": []}

    if not docs:
        logger.info("No relevant documents found for: %.60s", question)
        return {"answer": FALLBACK_ANSWER, "sources": []}

    # Build context from retrieved chunks
    context_parts = []
    sources = set()
    for i, doc in enumerate(docs, 1):
        context_parts.append(f"[Chunk {i}]\n{doc.page_content}")
        # Extract source filename from metadata
        src = doc.metadata.get("source", "")
        if src:
            # Get just the filename
            src_name = src.split("/")[-1].split("\\")[-1]
            sources.add(src_name)

    context = "\n\n".join(context_parts)
    logger.info("Retrieved %d chunks for question: %.60s", len(docs), question)

    # Generate answer using LLM
    try:
        answer = generate_answer(context=context, question=question)
    except Exception as exc:
        logger.error("LLM generation failed: %s", exc)
        return {
            "answer": "I'm having trouble connecting to the language model. "
                      "Please ensure Ollama is running with the mistral model.",
            "sources": list(sources),
        }

    return {
        "answer": answer,
        "sources": sorted(sources),
    }
