import os
from utilities import Utilities
from qdrant_client import QdrantClient, models
import discord

class QdrantManager:
    client = None

    @staticmethod
    async def initialize_qdrant(bot, channel_id, user_id, config, embedding_manager):
        await QdrantManager.create_client()

        # Initialize flags with default values
        collection_deleted = False
        collection_created = False
        collection_exists = False  # Initialize to avoid potential reference issues

        # Confirm deletion of the collection
        collection_deleted = await Utilities.confirm_and_run(
            bot,
            channel_id,
            user_id,
            QdrantManager.delete_collection,
            prompt="Do you want to delete the collection from Qdrant?"
        )

        # Confirm creation of the collection only if deletion was confirmed
        if collection_deleted:
            collection_created = await Utilities.confirm_and_run(
                bot,
                channel_id,
                user_id,
                QdrantManager.create_collection(embedding_manager),
                prompt="Do you want to create a Qdrant collection?"
            )
        else:
            collection_exists = await QdrantManager.check_collection_exists()
            collection_created = False  # Assume creation didn't occur since it wasn't prompted

        # Decision-making based on results
        if collection_deleted and collection_created:
            config.COLLECTIONS_INITIALIZED = True
        elif collection_deleted and not collection_created:
            config.COLLECTIONS_INITIALIZED = False
        elif not collection_deleted:
            if collection_exists:
                config.COLLECTIONS_INITIALIZED = True
            else:
                config.COLLECTIONS_INITIALIZED = False

    @staticmethod
    async def create_client():
        # Check if the client already exists to avoid re-creation
        if QdrantManager.client is None:
            # Initialize the Qdrant client and store it in the class variable
            QdrantManager.client = QdrantClient(
                url=os.getenv("QDRANT_HOST"),
                api_key=os.getenv("QDRANT_API_KEY"),
            )
            print("Created Qdrant client")
        else:
            print("Qdrant client already exists.")
        return QdrantManager.client

    @staticmethod
    async def check_collection_exists():
        # Check if collection exists in Qdrant
        existing_collections = QdrantManager.client.get_collections().collections
        if os.getenv("QDRANT_COLLECTION_NAME") not in [col.name for col in existing_collections]:
            return False
        else:
            return True

    @staticmethod
    async def delete_collection():
        if QdrantManager.client:
            QdrantManager.client.delete_collection(os.getenv("QDRANT_COLLECTION_NAME"))
        else:
            print("Client not initialized.")

    @staticmethod
    async def create_collection(embedding_manager):
        if QdrantManager.client is None:
            print("Client not initialized.")
            return

        existing_collections = QdrantManager.client.get_collections().collections
        if os.getenv("QDRANT_COLLECTION_NAME") not in [col.name for col in existing_collections]:
            # Create collection only if it does not already exist
            QdrantManager.client.create_collection(
                collection_name=os.getenv("QDRANT_COLLECTION_NAME"),
                vectors_config=embedding_manager.vectors_config(),
            )
            print(f"Collection '{os.getenv('QDRANT_COLLECTION_NAME')}' created.")
        else:
            print(f"Collection '{os.getenv('QDRANT_COLLECTION_NAME')}' already exists.")
