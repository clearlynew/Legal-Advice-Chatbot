from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaLLM
from langchain.chains import RetrievalQA

# --- Config ---
embedding_model_name = "sentence-transformers/all-MiniLM-L6-v2"
llama_model_name = "llama3.2"

# --- Step 1: Reload embeddings ---
hf_embeddings = HuggingFaceEmbeddings(model_name=embedding_model_name)

# --- Step 2: Load FAISS vectorstore ---
vectordb = FAISS.load_local(
    "vectorstore",
    hf_embeddings,
    allow_dangerous_deserialization=True
)
retriever = vectordb.as_retriever()

# --- Step 3: Initialize OllamaLLM ---
llm = OllamaLLM(model=llama_model_name)

# --- Step 4: Create RetrievalQA chain ---
qa_chain = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=retriever)

# --- Step 5: Query ---
query = "Will I go to jail if I don't pay taxes?"
result = qa_chain.invoke({"query": query})

print("Query:", query)
print("Answer:", result["result"])
