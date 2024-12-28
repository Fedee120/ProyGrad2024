# IRAG.py
from abc import ABC, abstractmethod
from typing import List
from langchain.schema import BaseMessage

class IRAG(ABC):
    @abstractmethod
    def generate_answer(self, question: str, history: List[BaseMessage] = None):
        """
        Genera la respuesta final a partir de una pregunta y un historial opcional.
        """
        pass
