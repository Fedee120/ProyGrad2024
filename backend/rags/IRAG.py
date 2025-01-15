from abc import ABC, abstractmethod
from typing import List
from langchain_core.messages import BaseMessage

class IRAG(ABC):
    @abstractmethod
    def add_documents(self, documents: list, ids: list = None):
        pass

    @abstractmethod
    def delete_documents(self, ids: list):
        pass

    @abstractmethod
    def similarity_search(self, query: str, k: int = 2, filter: dict = None):
        pass

    @abstractmethod
    def generate_answer(self, question: str, history: List[BaseMessage]):
        pass
