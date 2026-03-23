"""
Semantic History Search utility.
Uses sentence-transformers (all-MiniLM-L6-v2) to embed queries
and numpy cosine similarity for ranking — no external vector DB required.
"""
from typing import List, Dict, Any
import numpy as np
from app.utils.logger import get_logger

logger = get_logger("intelrouter.utils.vector_search")

_model = None


def _get_model():
    """Lazy-load the sentence transformer model (downloads ~80 MB on first use)."""
    global _model
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer
            logger.info("📦 Loading sentence-transformer model (MiniLM)...")
            _model = SentenceTransformer("all-MiniLM-L6-v2")
            logger.info("✅ Sentence-transformer model loaded")
        except ImportError:
            logger.warning("⚠️  sentence-transformers not installed. pip install sentence-transformers")
            raise
    return _model


def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Compute cosine similarity between two vectors."""
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(a, b) / (norm_a * norm_b))


def semantic_search(search_query: str, history: List[Dict[str, Any]], top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Find the most semantically similar past queries to the search_query.

    Args:
        search_query: The user's search string.
        history: List of query dicts with at least a 'query_text' key.
        top_k: Number of results to return.

    Returns:
        Top-k ranked query dicts with an extra 'similarity_score' field.
    """
    # Filter to records that have query text
    valid = [q for q in history if q.get("query_text")]
    if not valid:
        return []

    model = _get_model()

    # Embed all texts
    texts = [q["query_text"] for q in valid]
    try:
        all_embeddings = model.encode(texts, convert_to_numpy=True)
        search_embedding = model.encode([search_query], convert_to_numpy=True)[0]
    except Exception as e:
        logger.error(f"❌ Embedding error: {e}")
        return []

    # Compute similarities
    scored = []
    for i, q in enumerate(valid):
        score = _cosine_similarity(search_embedding, all_embeddings[i])
        scored.append({**q, "similarity_score": round(score, 4)})

    # Sort by similarity descending and return top_k
    scored.sort(key=lambda x: x["similarity_score"], reverse=True)
    results = scored[:top_k]
    logger.info(f"🔍 Semantic search complete | Query: '{search_query[:30]}...' | Top match score: {results[0]['similarity_score'] if results else 0:.4f}")
    return results
