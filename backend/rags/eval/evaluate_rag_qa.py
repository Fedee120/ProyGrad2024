# faithfullness: the degree to which the answer is derived from the context.
# answer_relevance: It's how relevant the answer is to the question.
# context_precision: Signal to noise ratio in the context.
# context_recall: How much of the context is relevant.
from rags.eval.metrics.groundedness import is_grounded
from rags.eval.metrics.faithfulness import is_faithfull
from rags.eval.metrics.answer_relevancy import is_relevant
from rags.eval.metrics.context_relevancy import count_relevant

def process_sample_metrics(sample, verbose=False):
    question = sample["question"]
    if verbose:
        print("Question: ", question)
    ground_truth = sample["ground_truth"]
    answer = rag.generate_answer(question)

    faithfull = False
    grounded = False
    relevant = False

    relevant_docs = count_relevant(question, [doc.page_content for doc in answer.get("context")])
    if verbose:
        print("Context relevancy: ", relevant_docs)

    # Compute answer relevancy
    if is_relevant(question, answer.get("answer")).is_relevant:
        if verbose:
            print("Relevant")
        relevant = True
    else:
        if verbose:
            print("Not relevant")
    
    # Compute faithfulness
    if is_faithfull(question, answer.get("context"), answer.get("answer")).is_faithful:
        if verbose:
            print("Faithful")
        faithfull = True
    else:
        if verbose:
            print("Not faithful")
    
    # Compute groundedness
    if is_grounded(question, answer.get("answer"), ground_truth).is_grounded:
        if verbose:
            print("Grounded")
        grounded = True
    else:
        if verbose:
            print("Not grounded")

    return faithfull, grounded, relevant, relevant_docs


if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    from rags.openai.rag import RAG
    import json
    from concurrent.futures import ThreadPoolExecutor

    load_dotenv()

    rag = RAG(URI=os.getenv("MILVUS_STANDALONE_URL"), COLLECTION_NAME="real_collection", search_kwargs={"k": 10}, search_type="mmr", llm_model_name="gpt-4o", embeddings_model_name="text-embedding-3-small")

    current_dir = os.path.dirname(os.path.abspath(__file__))
    dataset_path = os.path.join(current_dir, "datasets", "QA_dataset.json")

    with open(dataset_path, encoding="utf-8") as f:
        dataset = json.load(f)
        total = len(dataset)
        
        with ThreadPoolExecutor(max_workers=1) as executor:
            results = list(executor.map(lambda sample: process_sample_metrics(sample, verbose=True), dataset))
        
        # Separate the results for faithfulness and groundedness
        faithful_results = [result[0] for result in results]
        grounded_results = [result[1] for result in results]
        relevant_results = [result[2] for result in results]
        context_relevancy_results = [result[3] for result in results]
        
        # Calculate metrics
        faithfulness_score = sum(faithful_results) / total
        groundedness_score = sum(grounded_results) / total
        relevancy_score = sum(relevant_results) / total
        context_relevancy_score = sum(context_relevancy_results) / total
        
        print(f"Faithfulness: {faithfulness_score}")
        print(f"Groundedness: {groundedness_score}")
        print(f"Relevancy: {relevancy_score}")
        print(f"Context Relevancy: {context_relevancy_score}")
