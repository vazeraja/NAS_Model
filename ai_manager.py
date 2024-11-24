from langchain_openai import ChatOpenAI
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_qdrant import QdrantVectorStore

import requests
import os
from io import BytesIO
from tempfile import NamedTemporaryFile


class AIManager:

    @staticmethod
    async def ask_bot(query, vector_store, config):
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

        response = (rag_chain.invoke({"input": query}))
        return response["answer"]

    @staticmethod
    async def embed_documents(pdf_urls, vector_store: QdrantVectorStore):
        import os
        from langchain.text_splitter import CharacterTextSplitter
        from langchain_community.document_loaders import PyPDFLoader

        # current_dir = os.path.dirname(os.path.abspath(__file__))
        # books_dir = os.path.join(current_dir, "books")
        #
        # # List all PDF files in the directory
        # pdf_files = [file for file in os.listdir(books_dir) if file.endswith(".pdf")]

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

                # Add the chunks to the vector store
                vector_store.add_documents(chunked_docs)
                all_chunks.extend(chunked_docs)

                print(f"Processed {pdf_url}: {len(chunked_docs)} chunks")
                os.remove(temp_pdf_path)
            else:
                print(f"Failed to retrieve PDF. Status code: {response.status_code}")


        print("\n--- Document Chunks Information ---")
        print(f"Total number of chunks: {len(all_chunks)}")
        print(f"Sample chunk from {all_chunks[0].metadata['source']}:\n{all_chunks[0].text}\n")