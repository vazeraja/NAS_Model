from langchain_huggingface import HuggingFaceEmbeddings
from transformers import AutoModel


class EmbeddingManager:
    def __init__(self, model_name):
        self.__embedding_model_name = model_name  # Private attribute
        self.embedding_model = self.create_model()
        self.embedding_dim = self.embed_dim()

    def model_name(self):
        return self.__embedding_model_name

    def auto_model(self):
        return AutoModel.from_pretrained(self.model_name())

    def embed_dim(self):
        model = self.auto_model()
        return model.config.hidden_size

    def create_model(self):
        return HuggingFaceEmbeddings(
            model_name=self.model_name(),
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': False}
        )
