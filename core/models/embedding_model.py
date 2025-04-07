from sentence_transformers import SentenceTransformer
from RAG.config import Config

def get_embedding_model():
    model = SentenceTransformer(Config.EMBEDDING_MODEL_PATH)
    return model