import asyncio
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance

from config import Config
from services.embedding_service import EmbeddingService
from utils.utils import Utils

load_dotenv()

config = Config()
embedding_service = EmbeddingService("sentence-transformers/all-mpnet-base-v2")

client = QdrantClient(url=config.QDRANT_HOST, api_key=config.QDRANT_API_KEY)
vectors_config = VectorParams(size=embedding_service.embed_dim(), distance=Distance.COSINE)


async def main():
    collection_deleted = False
    collection_created = False
    collection_exists = await check_collection_exists()

    collection_deleted = await Utils.confirm_and_run(
        delete_collection,
        prompt="Do you want to delete the collection from Qdrant?"
    )

    if collection_deleted:
        collection_created = await Utils.confirm_and_run(
            create_collection,
            prompt="Do you want to create a Qdrant collection?"
        )

async def create_collection():
    existing_collections = client.get_collections().collections
    if config.QDRANT_COLLECTION_NAME not in [col.name for col in existing_collections]:
        client.create_collection(
            collection_name=config.QDRANT_COLLECTION_NAME,
            vectors_config=vectors_config,
        )
        print(f"Collection '{config.QDRANT_COLLECTION_NAME}' created.")
    else:
        print(f"Collection '{config.QDRANT_COLLECTION_NAME}' already exists.")

async def delete_collection():
    existing_collections = client.get_collections().collections
    if config.QDRANT_COLLECTION_NAME in [col.name for col in existing_collections]:
        client.delete_collection(config.QDRANT_COLLECTION_NAME)
        print(f"Collection with name {config.QDRANT_COLLECTION_NAME} has been deleted")
    print(f"Collection '{config.QDRANT_COLLECTION_NAME}' does not exist.")

async def check_collection_exists() -> bool:
    existing_collections = client.get_collections().collections
    return config.QDRANT_COLLECTION_NAME in [col.name for col in existing_collections]

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Program interrupted by user.")

