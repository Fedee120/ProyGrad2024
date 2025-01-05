### Router

from typing import Literal, List, Dict

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from pydantic import BaseModel, Field

import os
from dotenv import load_dotenv

load_dotenv()

# Data model
class RouteQuery(BaseModel):
    """Route a user query to the most relevant datasource."""

    datasource: Literal["vectorstore", "no_data"] = Field(
        ...,
        description="Given a user question choose to route it to web search or say that there is no data.",
    )


# LLM with function call
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
structured_llm_router = llm.with_structured_output(RouteQuery)

# Prompt
system = """You are an expert at routing a user question to a vectorstore or web search.
The vectorstore contains documents related to AI, education, pedagogy, etc.
Use the vectorstore for:
1. Direct questions about AI, their functionality, implementation, or use cases
2. Questions about how to use AI in education, pedagogy, etc.
3. Questions about the world of AI, how it works, etc.

Use no_data for:
1. Questions completely unrelated to AI, education, pedagogy, etc.
2. Personal questions or greetings that don't lead to these topics
3. Questions about other technical topics not related to the above
4. Questions about previous messages or conversation history

"""

route_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        ("human", """Conversation History:
{history}

Current Question: {question}"""),
    ]
)

def format_history(messages: List[Dict]) -> str:
    """Format message history into a readable string."""
    formatted = []
    for msg in messages:
        role = "User" if msg["user"] == "user" else "Assistant"
        formatted.append(f"{role}: {msg['message']}")
    return "\n".join(formatted) if formatted else "No previous conversation"

def route_with_history(question: str, message_history: List[Dict]) -> RouteQuery:
    """Route question considering conversation history."""
    print("DEBUG - Entrando a route_with_history")
    print(f"DEBUG - Question: {question}")
    print(f"DEBUG - Message History: {message_history}")
    
    formatted_history = format_history(message_history)
    print(f"DEBUG - Formatted History: {formatted_history}")
    
    try:
        chain = route_prompt | structured_llm_router
        print("DEBUG - Chain creado exitosamente")
        
        result = chain.invoke({
            "question": question,
            "history": formatted_history
        })
        print(f"DEBUG - Resultado: {result}")
        return result
    except Exception as e:
        print(f"DEBUG - Error en route_with_history: {str(e)}")
        raise

question_router = route_with_history