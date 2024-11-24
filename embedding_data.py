from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient, models
from transformers import AutoModel
from qdrant_manager import QdrantManager


class EmbeddingData:
    def __init__(self, config, model_name):
        self.__embedding_model_name = model_name  # Private attribute
        self.embedding_model = self.model()
        self.embedding_dim = self.embed_dim()
        self.config = config

    def model_name(self):
        return self.__embedding_model_name

    def auto_model(self):
        return AutoModel.from_pretrained(self.model_name())

    def embed_dim(self):
        model = self.auto_model()
        return model.config.hidden_size

    def model(self):
        return HuggingFaceEmbeddings(
            model_name=self.model_name(),
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': False}
        )

    def vectors_config(self):
        vectors_config = models.VectorParams(size=self.embed_dim(), distance=models.Distance.COSINE)
        return vectors_config

    def vector_store(self):
        vector_store = QdrantVectorStore(
            client=QdrantManager.client,
            collection_name=self.config.QDRANT_COLLECTION_NAME,
            embedding=self.model()
        )
        return vector_store
