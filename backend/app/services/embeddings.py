from app.core.config import settings
from sentence_transformers import SentenceTransformer

model = SentenceTransformer(settings.embedding_model)

class EmbeddingsService:

    @staticmethod
    def embed_text(text: str) -> list[float]:
        embedding = model.encode(text,convert_to_numpy=True,normalize_embeddings=True)
        return embedding.tolist()