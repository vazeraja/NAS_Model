import os

class Config:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls.QDRANT_HOST = os.getenv("QDRANT_HOST")
            cls.QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
            cls.QDRANT_COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME")
            cls.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
            cls.DISCORD_API_KEY = os.getenv("DISCORD_API_KEY")
        return cls._instance
