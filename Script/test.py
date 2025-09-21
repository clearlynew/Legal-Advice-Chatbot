import json
import csv
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import OllamaLLM
from langchain.chains import RetrievalQA

testing_dataset="C:\Legal Advice Chatbot\Data\Testing Dataset\IndicLegalQA Dataset_10K_Revised.json"
# --- Load FAISS vectorstore ---
hf_embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vectordb = FAISS.load_local("vectorstore", hf_embeddings, allow_dangerous_deserialization=True)

# --- Initialize Ollama + QA chain ---
llm = OllamaLLM(model="llama3.2")
qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=vectordb.as_retriever(), chain_type="stuff")

# --- Load testing dataset ---
with open(testing_dataset, "r", encoding="utf-8") as f:
    test_data = json.load(f)

total_score = 0
num_questions = len(test_data)

# --- Open CSV to log results ---
with open("test_results.csv", "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=["question", "ground_truth", "answer", "score"])
    writer.writeheader()

    for entry in test_data:
        question = entry["question"]
        ground_truth = entry["answer"]

        # Run query through QA chain
        result = qa_chain.invoke({"query": question})
        answer = result["result"]

        # Compute simple word-overlap score
        gt_words = set(ground_truth.lower().split())
        answer_words = set(answer.lower().split())
        score = len(gt_words & answer_words) / max(len(gt_words), 1)

        total_score += score

        writer.writerow({
            "question": question,
            "ground_truth": ground_truth,
            "answer": answer,
            "score": round(score, 2)
        })

        print(f"Question: {question} | Score: {score:.2f}")

# --- Compute and print overall score ---
overall_score = total_score / max(num_questions, 1)
print("\n==============================")
print(f"✅ Overall Score: {overall_score*100:.2f}%")
print("==============================")
