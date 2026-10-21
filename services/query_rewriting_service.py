from services.llm_service import LLMService


class QueryRewritingService:

    def __init__(self):
        self.llm_service = LLMService()

    def rewrite(self, question: str, conversation: list):

        if not conversation:
            return question

        history = ""

        for message in conversation[-6:]:
            history += (
                f"{message['role']}: "
                f"{message['content']}\n"
            )

        prompt = f"""
You are a query rewriting system for a customer
support RAG application.

Rewrite the user's latest question into a clear,
standalone search query.

Use the conversation history to understand references
such as "it", "that", "this", or "where".

Do not answer the question.
Return ONLY the rewritten search query.

Conversation history:
{history}

Latest user question:
{question}

Rewritten search query:
"""

        rewritten_query = self.llm_service.generate(prompt)

        return rewritten_query.strip()