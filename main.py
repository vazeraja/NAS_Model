import os
import asyncio
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain import hub
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

from langchain_qdrant import QdrantVectorStore

from EmbeddingModelCreator import EmbeddingModelCreator
from QdrantManager import QdrantManager
from Config import Config
from Utilities import Utilities

load_dotenv()


async def main():
    config = Config()

    # Try to initialize Qdrant and proceed with setup if successful
    if not await QdrantManager.initialize_qdrant():
        print("Failed to initialize Qdrant")
        return

    # Everything inside here runs only if Qdrant initialization is successful
    print("Qdrant initialized successfully")

    embedding_model_creator = EmbeddingModelCreator("sentence-transformers/all-mpnet-base-v2")
    embed_dim = embedding_model_creator.embed_dim()
    embedding_model = embedding_model_creator.model()

    vector_store = QdrantVectorStore(
        client=QdrantManager.client,
        collection_name=config.QDRANT_COLLECTION_NAME,
        embedding=embedding_model
    )

    await embed_documents(vector_store)

    retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 6})
    llm = ChatOpenAI(model="gpt-4o-mini", api_key=config.OPENAI_API_KEY)

    system_prompt = (
        "You are an assistant for question-answering tasks. "
        "Use the following pieces of retrieved context to answer "
        "the question. If you don't know the answer, say that you "
        "don't know. Use three sentences maximum and keep the "
        "answer concise."
        "\n\n"
        "{context}"
    )
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("human", "{input}"),
        ]
    )

    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    rag_chain = create_retrieval_chain(retriever, question_answer_chain)

    query = "How does Alchian define the cost of an action? What example does he give to support this definition?"
    response = (rag_chain.invoke({"input": query}))
    print(response["answer"])


async def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


async def embed_documents(vector_store):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, "books", "Alchian_UniversalEconomics1674.pdf")
    db_dir = os.path.join(current_dir, "db")
    # Check if the text file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(
            f"The file {file_path} does not exist. Please check the path."
        )
    loader = PyPDFLoader(file_path)
    documents = loader.load()
    chunked_docs = await get_chunks(documents)
    vector_store.add_documents(chunked_docs)
    print("\n--- Document Chunks Information ---")
    print(f"Number of document chunks: {len(chunked_docs)}")
    print(f"Sample chunk:\n{chunked_docs[345]}\n")


async def get_chunks(text):
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    docs = text_splitter.split_documents(text)

    return docs


if __name__ == "__main__":
    asyncio.run(main())
