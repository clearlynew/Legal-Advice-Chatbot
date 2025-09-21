import os
import json
from tqdm import tqdm
from langchain_community.document_loaders import TextLoader
from langchain.schema import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.llms import Ollama 
from langchain.chains import RetrievalQA

# --- Configuration ---
data_dir = r"C:\Legal Advice Chatbot\Data\Training_Data"
save_docs_path = "loaded_docs.json"
embedding_model_name = "sentence-transformers/all-MiniLM-L6-v2"
llama_model_name = "llama3.2"  # Replace with your Ollama model name

# --- Step 1: Load documents ---
documents = []
files = [f for f in os.listdir(data_dir) if f.endswith(".txt")]
for filename in tqdm(files, desc="Loading text chunks"):
    loader = TextLoader(os.path.join(data_dir, filename), encoding="utf-8")
    documents.extend(loader.load())

# --- Step 2: Save loaded documents for backup ---
docs_serializable = [{"page_content": doc.page_content, "metadata": doc.metadata} for doc in documents]
with open(save_docs_path, "w", encoding="utf-8") as f:
    json.dump(docs_serializable, f, ensure_ascii=False)
print(f"Saved {len(documents)} documents to {save_docs_path}")

# --- Step 3: Reload documents from JSON ---
with open(save_docs_path, "r", encoding="utf-8") as f:
    loaded_data = json.load(f)
documents = [Document(page_content=d["page_content"], metadata=d.get("metadata", {})) for d in loaded_data]

# --- Step 4: Initialize embeddings ---
hf_embeddings = HuggingFaceEmbeddings(model_name=embedding_model_name)

# --- Step 5: Create and save FAISS vector store ---
texts = [doc.page_content for doc in documents]
vectordb = FAISS.from_texts(texts, hf_embeddings)
vectordb.save_local("vectorstore", serialize=True)
print("Vector store created and saved (JSON-safe).")

# --- Step 6: Load vector store and create retriever ---
hf_embeddings = HuggingFaceEmbeddings(model_name=embedding_model_name)  # Reload to ensure consistency
vectordb = FAISS.load_local("vectorstore", hf_embeddings, serialize=True)
retriever = vectordb.as_retriever()

# --- Step 7: Initialize Ollama LLaMA model ---
llm = Ollama(model=llama_model_name)

# --- Step 8: Create RetrievalQA chain ---
qa_chain = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=retriever)

# --- Step 9: Query the chain ---
query = "Explain the principle of natural justice."
answer = qa_chain.run(query)
print("Query:", query)
print("Answer:", answer)
