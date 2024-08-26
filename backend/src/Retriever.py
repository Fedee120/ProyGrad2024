class Retriever:
    def __init__(self, milvus_handler):
        """
        Initializes the Retriever class with a MilvusHandler instance.
        
        :param milvus_handler: An instance of MilvusHandler for interacting with Milvus.
        """
        self.milvus_handler = milvus_handler

    def retrieve(self, query, top_k=5, nprobe=10):
        """
        Retrieves the most relevant results from the Milvus database based on the query.

        :param query: The query string to search for.
        :param top_k: The number of top results to retrieve.
        :param nprobe: The search granularity for Milvus.
        :return: A list of results with their metadata.
        """
        # Perform the search using MilvusHandler
        search_results = self.milvus_handler.search(query, top_k=top_k, nprobe=nprobe)

        # Extract the relevant information from the search results
        results = []
        if search_results and len(search_results[0]) > 0:
            for result in search_results[0]:
                result_data = {
                    "id": result.id,
                    "sentence": result.entity.get("sentence"),
                    "distance": result.distance
                }
                results.append(result_data)
        
        return results