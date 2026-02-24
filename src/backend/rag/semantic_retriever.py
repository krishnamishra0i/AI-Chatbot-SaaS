"""
Semantic Retriever

Attempts to use sentence-transformers for dense embeddings and cosine similarity.
If sentence-transformers is not available, falls back to a TF-IDF vectorizer.

Provides an optional LLM re-ranker hook to let the LLM rescore top candidates.
"""
from pathlib import Path
from typing import List, Dict, Optional
import json
import logging

import numpy as np

logger = logging.getLogger(__name__)


class SemanticRetriever:
    def __init__(self, qa_file_path: Optional[str] = None, model_name: str = "all-MiniLM-L6-v2"):
        self.qa_data: List[Dict] = []
        self.is_loaded = False
        self.model_name = model_name
        # Tunable parameters
        self.top_k_default = 5
        self.similarity_threshold = 0.05
        self.llm_weight = 0.7
        self.sem_weight = 0.3
        self.tfidf_max_features = 5000

        self._use_sentence_transformers = False
        self._embedder = None
        self._vectorizer = None
        self._embeddings = None

        if not qa_file_path:
            project_root = Path(__file__).parent.parent.parent.parent
            qa_file_path = str(project_root / "data" / "creditor_academy_qa.json")

        self.load_qa_data(qa_file_path)

        # Try to initialize embedder
        try:
            from sentence_transformers import SentenceTransformer

            self._embedder = SentenceTransformer(self.model_name)
            self._use_sentence_transformers = True
            logger.info(f"✅ Using SentenceTransformer model: {self.model_name}")
        except Exception as e:
            logger.warning("⚠️ sentence-transformers not available, falling back to TF-IDF vectorizer. Install with: pip install sentence-transformers")
            self._use_sentence_transformers = False

    def load_qa_data(self, filepath: str):
        try:
            p = Path(filepath)
            if not p.exists():
                logger.warning(f"Q&A file not found: {p}")
                return

            with open(p, 'r', encoding='utf-8') as f:
                self.qa_data = json.load(f)

            self.is_loaded = True
            logger.info(f"Loaded {len(self.qa_data)} Q&A pairs for semantic retriever")
        except Exception as e:
            logger.error(f"Failed to load QA data: {e}")

    def build_index(self):
        """Build embeddings / vector index for the loaded QA data."""
        if not self.is_loaded or not self.qa_data:
            logger.warning("No QA data loaded, cannot build index")
            return

        texts = [f"{qa.get('question','')}\n{qa.get('answer','')}" for qa in self.qa_data]

        if self._use_sentence_transformers and self._embedder is not None:
            try:
                self._embeddings = self._embedder.encode(texts, convert_to_numpy=True, show_progress_bar=False)
                logger.info("Built dense embeddings for QA data")
                return
            except Exception as e:
                logger.warning(f"Failed to encode with sentence-transformers: {e}")

        # Fallback: TF-IDF
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            self._vectorizer = TfidfVectorizer(max_features=self.tfidf_max_features)
            self._embeddings = self._vectorizer.fit_transform(texts)
            logger.info("Built TF-IDF index for QA data (fallback)")
        except Exception as e:
            logger.error(f"Failed to build fallback TF-IDF index: {e}")

    def _query_vector(self, query: str):
        if self._use_sentence_transformers and self._embedder is not None:
            return self._embedder.encode([query], convert_to_numpy=True)[0]

        if self._vectorizer is not None:
            return self._vectorizer.transform([query])

        raise RuntimeError("No embedding or vectorizer available. Call build_index() first and ensure dependencies are installed.")

    def retrieve(self, query: str, top_k: int = 5) -> List[Dict]:
        """Retrieve top_k semantically similar Q&A items.

        Returns list of dicts: {"id": ..., "question": ..., "answer": ..., "score": ...}
        """
        if not self.is_loaded:
            return []

        if self._embeddings is None:
            self.build_index()

        try:
            q_vec = self._query_vector(query)

            # Compute similarity
            if self._use_sentence_transformers and isinstance(self._embeddings, np.ndarray):
                # dense numpy arrays
                emb = self._embeddings
                q_vec = q_vec.reshape(1, -1)
                sims = (emb @ q_vec.T).squeeze() / (
                    (np.linalg.norm(emb, axis=1) * np.linalg.norm(q_vec)) + 1e-10
                )
                scores = sims.tolist()
            else:
                # sparse matrix from TF-IDF
                from sklearn.metrics.pairwise import cosine_similarity

                sims = cosine_similarity(q_vec, self._embeddings).squeeze()
                scores = sims.tolist()

            # Pair up with QA entries
            scored = []
            for idx, score in enumerate(scores):
                qa = self.qa_data[idx]
                scored.append({
                    "id": qa.get("id", idx),
                    "question": qa.get("question"),
                    "answer": qa.get("answer"),
                    "score": float(score)
                })

            # Sort and return top_k
            scored.sort(key=lambda x: x["score"], reverse=True)
            return scored[:top_k]

        except Exception as e:
            logger.error(f"Semantic retrieval error: {e}")
            return []

    def rerank_with_llm(self, llm_interface, query: str, candidates: List[Dict]) -> List[Dict]:
        """Optional: re-rank candidates using LLM-based relevance scoring.

        The llm_interface should provide a `score_relevance(prompt)` or `generate(prompt)` method.
        This function will attempt to ask the LLM to score each candidate on a 0-100 relevance scale.
        If no suitable LLM method is available, returns the original candidates.
        """
        if not candidates:
            return candidates

        if llm_interface is None:
            return candidates

        scores = []
        for cand in candidates:
            try:
                prompt = (
                    f"Question: {query}\n\n"
                    f"Candidate answer (from KB):\n{cand['question']}\n{cand['answer']}\n\n"
                    "On a scale from 0 to 100, how relevant is the candidate answer to the question?"
                )

                # Prefer a scoring API if available
                if hasattr(llm_interface, 'score_relevance'):
                    val = llm_interface.score_relevance(prompt)
                else:
                    # Fallback to generate and extract number
                    resp = llm_interface.generate(prompt)
                    # try to parse leading number
                    import re

                    m = re.search(r"(\d{1,3})", resp)
                    val = int(m.group(1)) if m else 0

                scores.append(max(0, min(100, int(val))))
            except Exception as e:
                logger.warning(f"LLM rerank failed for candidate: {e}")
                scores.append(0)

        # Attach llm scores and combine (weighted) with semantic score
        for i, c in enumerate(candidates):
            llm_score = scores[i]
            sem_score = c.get('score', 0.0)
            # Normalize semantic score roughly to 0-100
            sem_norm = min(100, max(0, int(sem_score * 100))) if isinstance(sem_score, (int, float)) else 0
            # Weighted average using configured weights
            combined = (self.llm_weight * llm_score) + (self.sem_weight * sem_norm)
            c['llm_score'] = llm_score
            c['combined_score'] = combined

        candidates.sort(key=lambda x: x.get('combined_score', 0), reverse=True)
        return candidates

    # --- New tunable helpers ---
    def get_params(self) -> Dict:
        return {
            'top_k_default': self.top_k_default,
            'similarity_threshold': self.similarity_threshold,
            'llm_weight': self.llm_weight,
            'sem_weight': self.sem_weight,
            'tfidf_max_features': self.tfidf_max_features,
            'use_sentence_transformers': self._use_sentence_transformers,
            'model_name': self.model_name
        }

    def update_params(self, **kwargs):
        """Update retriever tunable parameters. If TF-IDF size changes, rebuild index."""
        rebuild = False
        for k, v in kwargs.items():
            if hasattr(self, k):
                setattr(self, k, v)
                if k == 'tfidf_max_features':
                    rebuild = True
            else:
                # Allow updating internal flags by known names
                if k == 'use_sentence_transformers':
                    self._use_sentence_transformers = bool(v)
                elif k == 'model_name' and isinstance(v, str):
                    self.model_name = v
                    rebuild = True

        if rebuild:
            try:
                # Clear existing index and rebuild
                self._embeddings = None
                self._vectorizer = None
                self.build_index()
            except Exception as e:
                logger.warning(f"Failed to rebuild index after param update: {e}")

    def get_stats(self) -> Dict:
        return {
            'total_qa_pairs': len(self.qa_data or []),
            'has_index': self._embeddings is not None,
            'use_sentence_transformers': self._use_sentence_transformers
        }

    def validate(self, sample_size: int = 200, top_k: Optional[int] = None) -> Dict:
        """Quick validation over a sample of QA pairs. Computes recall@1/3/5.

        Returns a dict with recall metrics.
        """
        if not self.is_loaded:
            return {'error': 'no data loaded'}

        if top_k is None:
            top_k = self.top_k_default

        import random
        ids = list(range(len(self.qa_data)))
        if sample_size < len(ids):
            ids = random.sample(ids, sample_size)

        hits_at_1 = 0
        hits_at_3 = 0
        hits_at_5 = 0

        for idx in ids:
            qa = self.qa_data[idx]
            q = qa.get('question') or ''
            gold_id = qa.get('id', idx)
            candidates = self.retrieve(q, top_k=top_k)
            cand_ids = [c.get('id') for c in candidates]
            if not cand_ids:
                continue
            if gold_id == cand_ids[0]:
                hits_at_1 += 1
            if gold_id in cand_ids[:3]:
                hits_at_3 += 1
            if gold_id in cand_ids[:5]:
                hits_at_5 += 1

        n = len(ids)
        return {
            'sample_size': n,
            'recall@1': hits_at_1 / n if n else 0.0,
            'recall@3': hits_at_3 / n if n else 0.0,
            'recall@5': hits_at_5 / n if n else 0.0
        }


__all__ = ["SemanticRetriever"]
