import asyncio
from dotenv import load_dotenv

from langchain_qdrant import QdrantVectorStore

import discord
from discord.ext import commands as discord_commands
from commands import Commands
from embedding_data import EmbeddingData
from qdrant_manager import QdrantManager
from config import Config
from utilities import Utilities

load_dotenv()

# Define the intents
intents = discord.Intents.default()
intents.messages = True  # Allows the bot to read messages
intents.message_content = True  # Required to access message content in recent versions

# Initialize the bot with command prefix and intents
bot = discord_commands.Bot(command_prefix="!", intents=intents)

BOT_TESTING_CHANNEL_ID = 1299034004472860703
USER_ID = 1113335861623402567

config = Config()
embedding_data = EmbeddingData(config, "sentence-transformers/all-mpnet-base-v2")


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    await QdrantManager.initialize_qdrant(bot, BOT_TESTING_CHANNEL_ID, USER_ID, config, embedding_data)

    await bot.get_channel(BOT_TESTING_CHANNEL_ID).send(f"Qdrant Initialized {config.COLLECTIONS_INITIALIZED}")


async def main():
    try:
        await bot.add_cog(Commands(bot, config, embedding_data))
        await bot.start(config.DISCORD_API_KEY)
    except (asyncio.CancelledError, KeyboardInterrupt):
        print("Bot is shutting down...")
    finally:
        await bot.close()

    # # Try to initialize Qdrant and proceed with setup if successful

    #
    # # Everything inside here runs only if Qdrant initialization is successful

    #
    # embedding_model_creator = EmbeddingModelCreator("sentence-transformers/all-mpnet-base-v2")
    # embed_dim = embedding_model_creator.embed_dim()
    # embedding_model = embedding_model_creator.model()
    #
    # vector_store = QdrantVectorStore(
    #     client=QdrantManager.client,
    #     collection_name=config.QDRANT_COLLECTION_NAME,
    #     embedding=embedding_model
    # )
    #
    # await embed_documents(vector_store)
    #
    # retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 6})
    # llm = ChatOpenAI(model="gpt-4o-mini", api_key=config.OPENAI_API_KEY)
    #
    # system_prompt = (
    #     "You are an assistant for question-answering tasks. "
    #     "Use the following pieces of retrieved context to answer "
    #     "the question. If you don't know the answer, say that you "
    #     "don't know. Use three sentences maximum and keep the "
    #     "answer concise."
    #     "\n\n"
    #     "{context}"
    # )
    # prompt = ChatPromptTemplate.from_messages(
    #     [
    #         ("system", system_prompt),
    #         ("human", "{input}"),
    #     ]
    # )
    #
    # question_answer_chain = create_stuff_documents_chain(llm, prompt)
    # rag_chain = create_retrieval_chain(retriever, question_answer_chain)
    #
    # query = "How does Alchian define the cost of an action? What example does he give to support this definition?"
    # response = (rag_chain.invoke({"input": query}))
    # print(response["answer"])


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Program interrupted by user.")
