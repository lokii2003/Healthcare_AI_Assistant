"""
llm.py — Ollama Mistral LLM wrapper with healthcare-safe prompting.
"""

from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate

from app.config import settings
from app.utils import setup_logger

logger = setup_logger("llm")


# ── Healthcare System Prompt ────────────────────────────────────────────────
SYSTEM_PROMPT = """You are a professional Healthcare AI Assistant. Follow these rules strictly:

1. Answer ONLY from the provided context below. Do not use any external knowledge.
2. If the answer is not found in the context, say: "I could not find this information in the provided documents."
3. NEVER guess, assume, or hallucinate information.
4. NEVER provide medical diagnoses, prescribe medications, or give unsafe medical advice.
5. Use a professional, concise, and empathetic tone.
6. Cite the source topic when available.
7. Keep answers clear and well-structured.

DISCLAIMER: This assistant is for informational and appointment-support purposes only and not a replacement for professional medical advice. Always consult a qualified healthcare provider for medical decisions.

Context:
{context}

Question: {question}

Answer:"""


RAG_PROMPT = PromptTemplate(
    input_variables=["context", "question"],
    template=SYSTEM_PROMPT,
)


def get_llm() -> OllamaLLM:
    """
    Return an OllamaLLM instance configured for Mistral.
    """
    logger.info("Connecting to Ollama at %s with model '%s'",
                settings.OLLAMA_BASE_URL, settings.OLLAMA_MODEL)
    try:
        llm = OllamaLLM(
            model=settings.OLLAMA_MODEL,
            base_url=settings.OLLAMA_BASE_URL,
            temperature=0.1,        # low temperature for factual answers
            num_predict=512,
        )
        return llm
    except Exception as exc:
        logger.error("Failed to connect to Ollama: %s", exc)
        raise ConnectionError(
            f"Cannot connect to Ollama at {settings.OLLAMA_BASE_URL}. "
            "Ensure Ollama is running and the mistral model is pulled: "
            "`ollama pull mistral`"
        ) from exc


def generate_answer(context: str, question: str) -> str:
    """
    Generate a grounded answer using Ollama Mistral given context and question.

    Parameters
    ----------
    context : str
        Retrieved document chunks concatenated.
    question : str
        User's question.

    Returns
    -------
    str
        The LLM-generated answer.
    """
    llm = get_llm()
    prompt = RAG_PROMPT.format(context=context, question=question)

    try:
        answer = llm.invoke(prompt)
        logger.info("LLM generated answer for question: %.60s…", question)
        return answer.strip()
    except Exception as exc:
        logger.error("LLM generation failed: %s", exc)
        raise RuntimeError(
            "Failed to generate answer. Ensure Ollama is running with the "
            "mistral model: `ollama serve` and `ollama pull mistral`"
        ) from exc
