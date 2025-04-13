from langchain.schema import AIMessage, HumanMessage
from typing import List, Dict

def create_chat_history(chat_history: List[Dict[str, str]]) -> List[AIMessage | HumanMessage]:
    """Convert chat history data to message objects."""
    messages = []
    for msg in chat_history:
        if msg["role"] == "human":
            messages.append(HumanMessage(content=msg["content"]))
        else:
            messages.append(AIMessage(content=msg["content"]))
    return messages

def format_chat_history_from_messages(messages: List[AIMessage | HumanMessage]) -> str:
    """
    Convert a list of AIMessage and HumanMessage objects into a readable chat history format.

    Args:
        messages (List[AIMessage | HumanMessage]): A list of message objects representing the conversation.

    Returns:
        str: A formatted string where each message is prefixed with its role ("Human" or "Assistant") for better readability.
    """   
    formatted = []
    for msg in messages:
        role = "Human" if isinstance(msg, HumanMessage) else "Assistant"
        formatted.append(f"  {role}: {msg.content}")
    return "\n".join(formatted)

def format_chat_history_from_dict(chat_history: List[Dict[str, str]]) -> str:
    """
    Convert a chat history stored as a list of dictionaries into a readable format.

    Args:
        chat_history (List[Dict[str, str]]): A list of dictionaries where each dictionary contains "role" and "content".

    Returns:
        str: A formatted string where each message is prefixed with "User" or "Assistant" for clarity.
    """
    formatted_history = []
    for message in chat_history:
        role = "User" if message["role"] == "human" else "Assistant"
        formatted_history.append(f"  {role}: {message['content']}")
    
    return "\n".join(formatted_history)