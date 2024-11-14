import asyncio
from dotenv import load_dotenv

import discord
from discord.ext import commands

from langchain_openai import ChatOpenAI
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_qdrant import QdrantVectorStore

from embedding_model_creator import EmbeddingManager
from qdrant_manager import QdrantManager
from config import Config
from utilities import Utilities

load_dotenv()

# Define the intents
intents = discord.Intents.default()
intents.messages = True  # Allows the bot to read messages
intents.message_content = True  # Required to access message content in recent versions

# Initialize the bot with command prefix and intents
bot = discord.ext.commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

async def main():
    config = Config()
    client = QdrantManager.client
    embedding_manager = EmbeddingManager("sentence-transformers/all-mpnet-base-v2")


    try:
        await bot.load_extension("commands")
        await bot.start(config.DISCORD_API_KEY)
    except (asyncio.CancelledError, KeyboardInterrupt):
        print("Bot is shutting down...")
    finally:
        await bot.close()

    # # Try to initialize Qdrant and proceed with setup if successful
    # if not await QdrantManager.initialize_qdrant():
    #     print("Failed to initialize Qdrant")
    #     return
    #
    # # Everything inside here runs only if Qdrant initialization is successful
    # print("Qdrant initialized successfully")
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



async def embed_documents(vector_store):
    import os
    from langchain.text_splitter import CharacterTextSplitter
    from langchain_community.document_loaders import PyPDFLoader

    current_dir = os.path.dirname(os.path.abspath(__file__))
    books_dir = os.path.join(current_dir, "books")

    # List all PDF files in the directory
    pdf_files = [file for file in os.listdir(books_dir) if file.endswith(".pdf")]

    if not pdf_files:
        raise FileNotFoundError("No PDF files found in the 'books' directory.")

    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=300,
        length_function=len
    )

    all_chunks = []
    for pdf_file in pdf_files:
        file_path = os.path.join(books_dir, pdf_file)
        loader = PyPDFLoader(file_path)
        documents = loader.load()

        # Split document into chunks
        chunked_docs = text_splitter.split_documents(documents)

        # Add metadata to each chunk
        for chunk in chunked_docs:
            chunk.metadata = {
                "source": pdf_file,  # Include the filename as a metadata attribute
            }

        # Add the chunks to the vector store
        vector_store.add_documents(chunked_docs)
        all_chunks.extend(chunked_docs)

        print(f"Processed {pdf_file}: {len(chunked_docs)} chunks")

    print("\n--- Document Chunks Information ---")
    print(f"Total number of chunks: {len(all_chunks)}")
    print(f"Sample chunk from {all_chunks[0].metadata['source']}:\n{all_chunks[0].text}\n")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Program interrupted by user.")

