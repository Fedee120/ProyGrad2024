from langchain_openai import OpenAIEmbeddings
from langchain_milvus import Milvus
from langchain_core.documents import Document
from uuid import uuid4
from langchain_groq import ChatGroq
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
        # Initialize embeddings
        self.embeddings = OpenAIEmbeddings(model=embeddings_model_name)

        # Connect to Milvus vector store
        self.vector_store = Milvus(
            embedding_function=self.embeddings,
            connection_args={"uri": URI},
            collection_name=COLLECTION_NAME,
        )

        # Create retriever
        self.retriever = self.vector_store.as_retriever(
            search_type=search_type, search_kwargs=search_kwargs
        )

        # Initialize LLM
        self.llm = ChatGroq(model=llm_model_name)

        # Set prompt template
        self.prompt_template = """You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the answer concise.
                                Question: {question}
                                Context: {context}
                                Answer:"""

        self.prompt = PromptTemplate(
            input_variables=["context", "question"],
            template=self.prompt_template,
        )

    def add_documents(self, documents: list, ids: list = None):
        """
        Add documents to the vector store.

        :param documents: List of Document objects to add.
        :param ids: Optional list of IDs for the documents.
        """
        if ids is None:
            ids = [str(uuid4()) for _ in range(len(documents))]
        self.vector_store.add_documents(documents=documents, ids=ids)

    def delete_documents(self, ids: list):
        """
        Delete documents from the vector store by IDs.

        :param ids: List of document IDs to delete.
        """
        self.vector_store.delete(ids=ids)

    def similarity_search(self, query: str, k: int = 2, filter: dict = None):
        """
        Perform a similarity search on the vector store.

        :param query: The query string.
        :param k: Number of top results to return.
        :param filter: Optional filter criteria.
        :return: List of Document objects that are similar to the query.
        """
        results = self.vector_store.similarity_search(query, k=k, filter=filter)
        return results

    def generate_answer(self, question: str):
        """
        Generate an answer to the question using retrieved documents and the LLM.

        :param question: The question string.
        :return: The generated answer string.
        """
        # Retrieve relevant documents
        docs = self.retriever.invoke(question)

        # Format the context from retrieved documents
        context = "\n\n".join(doc.page_content for doc in docs)

        # Prepare the prompt with context and question
        prompt_text = self.prompt.format(context=context, question=question)

        # Generate answer using the LLM
        messages = [HumanMessage(content=prompt_text)]
        response = self.llm.invoke(messages)
        output = {
            "answer": response.content,
            "context": docs
        }
        return output
    
if __name__ == "__main__":
    import time
    from dotenv import load_dotenv
    import os
    
    load_dotenv()

    # Initialize the RAG class
    time_connect = time.time()
    rag = RAG(
        URI=os.getenv("MILVUS_STANDALONE_URL"),
        COLLECTION_NAME="test_collection",
        search_kwargs={"k": 2},
        search_type="similarity",
        llm_model_name="llama-3.1-70b-versatile",
        embeddings_model_name="text-embedding-3-small",
    )
    print(f"Connected in {time.time() - time_connect:.2f} seconds")
    # Create some sample documents
    documents = [
        Document(page_content="The Eiffel Tower is located in Paris.", metadata={"source": "fact"}),
        Document(page_content="Python is a popular programming language.", metadata={"source": "fact"}),
    ]

    # Add documents to the vector store
    rag.add_documents(documents)

    time_search = time.time()
    # Perform a similarity search
    results = rag.similarity_search("Where is the Eiffel Tower?", k=1)
    for res in results:
        print(f"Content: {res.page_content}, Metadata: {res.metadata}")
    
    print(f"Search completed in {time.time() - time_search:.2f} seconds")
    
    time_answer = time.time()
    # Generate an answer to a question
    answer = rag.generate_answer("What is Python?")
    print(f"Answer: {answer}")
    print(f"Answer generated in {time.time() - time_answer:.2f} seconds")
