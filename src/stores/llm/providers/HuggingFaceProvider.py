from sentence_transformers import SentenceTransformer

class HuggingFaceProvider:
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)
        self.embedding_size = self.model.get_sentence_embedding_dimension()

    def embed_text(self, text: str):
        return self.model.encode(text).tolist()
    