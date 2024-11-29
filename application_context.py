import discord
from discord.ext import commands

from chat_manager import ChatManager
from config import Config
from services.embedding_service import EmbeddingService
from services.llm_service import LLMService


from services.qdrant_service import QdrantService


class ApplicationContext:
    def __init__(self):
        self.config = Config()
        self.embedding_service = EmbeddingService("sentence-transformers/all-mpnet-base-v2")
        self.qdrant_service = QdrantService(self.config, self.embedding_service)
        self.llm_service = LLMService(self.config, self.qdrant_service.vector_store)

        self.chat_manager = ChatManager(self.llm_service)
        self.bot = self.initialize_discord_bot()

    @staticmethod
    def initialize_discord_bot():
        # Define the intents
        intents = discord.Intents.default()
        intents.messages = True  # Allows the bot to read messages
        intents.message_content = True  # Required to access message content in recent versions

        # Initialize the bot with command prefix and intents
        bot = commands.Bot(command_prefix="!", intents=intents)
        return bot
