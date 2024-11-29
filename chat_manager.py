class ChatManager:
    def __init__(self, llm_service):
        self.llm_service = llm_service

    async def handle_query(self, query: str) -> str:
        if not query.strip():
            return "Your query is empty. Please provide a valid question."

        # Query the LLMService
        response = await self.llm_service.query_llm(query)
        return response.get("answer", "I'm sorry, I couldn't generate a response.")