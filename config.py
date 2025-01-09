import os
import threading




class Config:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(Config, cls).__new__(cls)
                cls.QDRANT_HOST = cls._get_env("QDRANT_HOST")
                cls.QDRANT_API_KEY = cls._get_env("QDRANT_API_KEY")
                cls.QDRANT_COLLECTION_NAME = cls._get_env("QDRANT_COLLECTION_NAME")

                cls.OPENAI_API_KEY = cls._get_env("OPENAI_API_KEY")
                cls.MD_OPENAI_KEY = cls._get_env("MD_OPENAI_KEY")
                cls.gpt_4o_mini = cls._get_env("GPT_4O_MINI")

                cls.DISCORD_API_KEY = cls._get_env("DISCORD_API_KEY")
                cls.BOT_TESTING_CHANNEL_ID = cls._get_env("BOT_TESTING_CHANNEL_ID")
                cls.USER_ID = cls._get_env("USER_ID")

        return cls._instance

    @staticmethod
    def _get_env(var_name):
        value = os.getenv(var_name)
        if value is None:
            raise ValueError(f"Environment variable {var_name} is required but not set.")
        return value
