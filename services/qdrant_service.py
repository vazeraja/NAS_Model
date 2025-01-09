from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance
from langchain_qdrant import QdrantVectorStore
import requests
from tempfile import NamedTemporaryFile
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader


class QdrantService:
    def __init__(self, config, embedding_service, force_recreate_collection = False):
        self.config = config
        self.embedding_service = embedding_service

        self.client = QdrantClient(url=self.config.QDRANT_HOST, api_key=self.config.QDRANT_API_KEY)
        self.vectors_config = VectorParams(size=self.embedding_service.embed_dim(), distance=Distance.COSINE)

        if force_recreate_collection:
            self.client.delete_collection(self.config.QDRANT_COLLECTION_NAME)

        if not self.client.collection_exists(config.QDRANT_COLLECTION_NAME):
            self.client.create_collection(config.QDRANT_COLLECTION_NAME, vectors_config=self.vectors_config)

        self.vector_store = QdrantVectorStore(
            client=self.client,
            collection_name=self.config.QDRANT_COLLECTION_NAME,
            embedding=self.embedding_service.model(),
        )

    @staticmethod
    async def embed_documents(pdf_urls):

        if not pdf_urls:
            raise FileNotFoundError("No PDF URLs provided")

        text_splitter = CharacterTextSplitter(
            separator="\n",
            chunk_size=1000,
            chunk_overlap=300,
            length_function=len
        )

        all_chunks = []
        for pdf_url in pdf_urls:
            response = requests.get(pdf_url)

            if response.status_code == 200:
                with NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
                    temp_pdf.write(response.content)
                    temp_pdf_path = temp_pdf.name

                loader = PyPDFLoader(temp_pdf_path)
                documents = loader.load()

                # Split document into chunks
                chunked_docs = text_splitter.split_documents(documents)

                # Add metadata to each chunk
                for chunk in chunked_docs:
                    chunk.metadata = {
                        "source": pdf_url,  # Include the filename as a metadata attribute
                    }

                # # Add the chunks to the vector store
                # self.vector_store.add_documents(chunked_docs)
                # all_chunks.extend(chunked_docs)
                #
                # print(f"Processed {pdf_url}: {len(chunked_docs)} chunks")
                # os.remove(temp_pdf_path)
            else:
                print(f"Failed to retrieve PDF. Status code: {response.status_code}")

        print("\n--- Document Chunks Information ---")
        print(f"Total number of chunks: {len(all_chunks)}")
        print(f"Sample chunk from {all_chunks[0].metadata['source']}:\n{all_chunks[0].text}\n")
