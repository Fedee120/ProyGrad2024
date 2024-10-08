# Faithfullness evaluation of the RAG: It's how factually accurate the responses are.
# answer_relevance: It's how relevant the answer is to the question.
# context_precision: Signal to noise ratio in the context.
# context_recall: How much of the context is relevant.

from rags.openai.rag import RAG
import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
from metrics.groundedness import is_grounded
from metrics.faithfulness import is_faithfull
from metrics.answer_relevancy import is_relevant
from metrics.context_relevancy import count_relevant

load_dotenv()

LOAD = False

rag = RAG(URI="http://localhost:19530", COLLECTION_NAME="real_collection", search_kwargs={"k": 10}, search_type="mmr", llm_model_name="gpt-4o", embeddings_model_name="text-embedding-3-small")

# load the pdfs

samples = "../data/raw/"
pdfs = [f for f in os.listdir(samples) if f.endswith(".pdf")]
paths = [os.path.join(samples, f) for f in pdfs]

def get_docs(path):
    loader = PyPDFLoader(path)
    return loader.load()

if LOAD:
    print("extracting documents")
    docs = []
    for path in paths:
        docs += get_docs(path)
    print("Extracted docs: ",len(docs))
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(docs)
    rag.add_documents(splits)
    print("Added docs to collection")


import json
from concurrent.futures import ThreadPoolExecutor
from time import sleep

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

    # Compute relevancy
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

with open("eval/datasets/QA_dataset.json", encoding="utf-8") as f:
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

