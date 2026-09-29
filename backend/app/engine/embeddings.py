import numpy as np
from typing import List, Optional

_model = None

def get_embedding_model():
    global _model
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer
            _model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        except Exception:
            _model = False
    return _model

def generate_embedding(text: str) -> List[float]:
    """
    Generates 384-dimensional vector embedding for text.
    Fallback to deterministic hash-based normalized vector if sentence-transformers is unavailable.
    """
    model = get_embedding_model()
    if model:
        try:
            vec = model.encode(text)
            return vec.tolist()
        except Exception:
            pass

    # Deterministic fallback 384-dim vector for low-memory execution
    np.random.seed(abs(hash(text)) % (2**32))
    vec = np.random.randn(384)
    vec = vec / np.linalg.norm(vec)
    return vec.tolist()

def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """
    Compute cosine similarity between two 384-dim vectors.
    """
    v1 = np.array(vec1)
    v2 = np.array(vec2)
    norm1 = np.linalg.norm(v1)
    norm2 = np.linalg.norm(v2)
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return float(np.dot(v1, v2) / (norm1 * norm2))
