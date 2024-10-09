from langchain_openai import OpenAIEmbeddings
from langchain_milvus import Milvus
from uuid import uuid4
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import HumanMessage
from rags.IRAG import IRAG

class RAG(IRAG):
    def __init__(
        self,
        URI: str,
        COLLECTION_NAME: str,
        search_kwargs: dict,
        search_type: str,
        llm_model_name: str,
        embeddings_model_name: str,
    ):
        self.embeddings = OpenAIEmbeddings(model=embeddings_model_name)
        self.vector_store = Milvus(
            embedding_function=self.embeddings,
            connection_args={"uri": URI},
            collection_name=COLLECTION_NAME,
        )
        self.retriever = self.vector_store.as_retriever(
            search_type=search_type, search_kwargs=search_kwargs
        )
        self.llm = ChatOpenAI(model=llm_model_name)
        self.prompt_template = """You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know. Do not add information that does not come from the context.
                        Question: {question}
                        Context: {context}
                        Answer:"""
        self.prompt = PromptTemplate(
            input_variables=["context", "question"],
            template=self.prompt_template,
        )

    def add_documents(self, documents: list, ids: list = None):
        if ids is None:
            ids = [str(uuid4()) for _ in range(len(documents))]
        self.vector_store.add_documents(documents=documents, ids=ids)

    def delete_documents(self, ids: list):
        self.vector_store.delete(ids=ids)

    def similarity_search(self, query: str, k: int = 2, filter: dict = None):
        results = self.vector_store.similarity_search(query, k=k, filter=filter)
        return results

    def generate_answer(self, question: str):
        docs = self.retriever.invoke(question)
        context = "\n\n".join(doc.page_content for doc in docs)
        prompt_text = self.prompt.format(context=context, question=question)
        messages = [HumanMessage(content=prompt_text)]
        response = self.llm.invoke(messages)
        output = {
            "answer": response.content,
            "context": docs
        }
        return output
