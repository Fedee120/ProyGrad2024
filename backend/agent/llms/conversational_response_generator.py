from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import BaseMessage
from typing import List
from langsmith import traceable

class ConversationalResponseGenerator:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.6
        )

        system_prompt_text = """
        You are a conversational assistant designed to help people who are curious about generative artificial intelligence. You should always follow the behaviors listed below.

        - Grounded responses always: Information related to the context will be provided to you so that responses are factual and backed up by sources.
        You should provide information only if it was obtained from the context. You should not provide any information that has not been obtained from the context, never, not even to correct the user if they are wrong. Do not add or infer information beyond what's in the context.
        If information is provided by the context, incorporate it naturally into your response.
        If no information is provided by the context and the user is expecting it, acknowledge it and say you cannot help with that question, suggest other resources and remind the user that you are available for any other question.

        - Conversational responses with random bursts of expansion as the conversation develops: Your responses should feel like a natural conversation, avoid lists or bullet points.
        You should avoid long responses that do not foster a back and forth dialog. From time to time, as the conversation develops and you see that the user is interested, expand a bit more. 
        A strategy that can be followed to foster the dialog is not to give all the information that was obtained, but to give it gradually, opening questions that the user may show interest in continuing by fostering curiosity and interest in related topics.

        ----------------------------------- Context Start -----------------------------------
        {context}
        ----------------------------------- Context End -----------------------------------
        """

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt_text),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{query}")
        ])

    @traceable
    def generate_response(
        self,
        query: str,
        context: str,
        history: List[BaseMessage]
    ) -> str:
        """Generate a response based on the query, context, and conversation history."""
        response = self.llm.invoke(
            self.prompt.format(
                query=query,
                context=context,
                history=history
            )
        )
        return response.content 