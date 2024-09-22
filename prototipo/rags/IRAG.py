from abc import ABC, abstractmethod
from langchain_core.documents import Document

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
    def generate_answer(self, question: str):
        pass
