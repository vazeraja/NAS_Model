from langchain_openai import ChatOpenAI
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

import requests
import os



class LLMService:
    def __init__(self, config, vector_store):
        self.retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 6})
        self.llm = ChatOpenAI(model=config.gpt_4o_mini, api_key=config.OPENAI_API_KEY)
        self.system_prompt = (
            "You are an assistant for question-answering tasks. "
            "Use the following pieces of retrieved context to answer "
            "the question. If you don't know the answer, say that you "
            "don't know. Use three sentences maximum and keep the "
            "answer concise."
            "\n\n"
            "{context}"
        )

    def _create_rag_chain(self):
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", self.system_prompt),
                ("human", "{input}"),
            ]
        )
        question_answer_chain = create_stuff_documents_chain(self.llm, prompt)
        return create_retrieval_chain(self.retriever, question_answer_chain)

    async def query_llm(self, query: str) -> dict:
        try:
            rag_chain = self._create_rag_chain()
            response = rag_chain.invoke({"input": query})
            return response
        except Exception as e:
            # logging.error(f"Error in LLMService.query_llm: {e}")
            return {"answer": "I'm sorry, something went wrong while processing your request."}



