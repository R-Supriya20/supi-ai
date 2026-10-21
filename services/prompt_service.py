class PromptService:

    def create_prompt(
        self,
        question: str,
        retrieved_chunks: list,
        conversation: list
    ) -> str:

        context = "\n\n".join(
            chunk["text"]
            for chunk in retrieved_chunks
        )

        history = "\n".join(
            f"{message['role']}: {message['content']}"
            for message in conversation[-6:]
        )

        return f"""
You are a helpful AI customer support assistant.

Instructions:
1. Answer the user's question using your general knowledge.
2. Use the supplied document context when relevant.
3. If the context does not contain the answer, use general
   knowledge and clearly distinguish it from official policy.
4. Never invent company policies.
5. If uncertain, say so.

Conversation history:
{history if history else "No previous conversation."}

Document context:
{context if context else "No relevant documents found."}

User question:
{question}

Answer:
"""