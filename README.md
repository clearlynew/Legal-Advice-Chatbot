# Legali - AI Legal Assistant ⚖️

Legali is an AI-powered legal assistant that lets users ask legal questions and upload relevant documents (PDFs, TXT files, and images). This project is a **template and showcase** designed to demonstrate the code structure and workflow of such an application. It's a starting point for building your own legal AI chatbot.

***Note: Large datasets and vector store files are excluded from this repository to keep it lightweight.***

---

## ✨ Features

* **AI-Powered Chat:** An interactive chat interface for legal queries.
* **Multi-Session Support:** Manages multiple, independent chat sessions.
* **File Uploads:** Supports PDFs, TXT files, and images for context.
* **Modular Design:** Easily swap out the LLM, embedding model, or file-processing logic to suit your needs.

---

## 📁 Project Structure
```
Legali/
├─ app.py                 # Main Streamlit application
├─ requirements.txt       # Python dependencies
├─ Script/
│   ├─ load.py            # Document loading and text extraction
│   ├─ preprocess.py      # Text cleaning and preparation
│   ├─ query.py           # Processes queries and interacts with the AI
│   ├─ test.py            # Example usage of the modules
│   └─ vectorstore/       # Placeholder for your vector store files (excluded)
├─ Data/                  # Sample PDF/text files for testing
├─ .gitignore             # Git ignore file for large files
└─ README.md              # This file
```

## ⚙️ How It Works

* `app.py`: This is the Streamlit interface. It handles user input, manages file uploads, and maintains chat history. It sends the user's question and relevant document context to the underlying AI model.
* `Script/load.py`: This script is responsible for loading documents and extracting their text. It uses **PyPDF2** and optionally **Tesseract** for OCR. You can modify it to support additional file formats.
* `Script/preprocess.py`: This module handles text cleaning and preparation, such as sanitization or splitting the text into smaller chunks for embedding.
* `Script/query.py`: This is where the magic happens. It takes the processed text and the user's question and sends them to the AI model. The current template uses `LLMChain` from **LangChain**, but you can easily replace it with any other LLM integration.

---

## 🚀 Installation & Usage (Template Only)

This repository is a template, so it won't be fully functional out of the box. You'll need to add your own data and vector store. Follow these steps to set up the project locally.

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/](https://github.com/)<your_username>/LegaliApp.git
    cd LegaliApp
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    # For Windows
    python -m venv venv
    venv\Scripts\activate

    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the app (with dummy data):**
    ```bash
    streamlit run app.py
    ```
    ⚠️ **Note:** The app will not fully function without a large vector store and a rich dataset. This repository is intended as a starting point for you to build upon.

---

## 🛠️ How to Customize

* **Change the LLM:** Replace the placeholder LLM (`ChatGroq`) in `Script/query.py` with your preferred model (e.g., OpenAI, Gemini, etc.).
* **Add Your Data:** Populate `Script/vectorstore/` with your own embeddings and vector store files.
* **Expand File Support:** Modify `Script/load.py` to handle additional file types or improve the existing extraction logic.
* **Demonstrate Functionality:** Place small, sample PDFs or text files in the `Data/` directory to showcase the app's file processing capabilities.

---

## ✨ Features

* **Intelligent Document Processing:** Legali can process a variety of document types (PDFs, TXT files) and images, extracting text to provide legal context for your questions. This includes an optional Optical Character Recognition (OCR) capability for image-based documents.
* **Dynamic Chat Management:** The application supports multiple chat sessions. You can start a new conversation at any time or seamlessly continue a previous chat within the same session to maintain context.
* **AI-Powered Legal Assistance:** At its core, Legali is an AI assistant designed to answer legal queries based on its knowledge and the documents you provide.
* **Highly Modular Architecture:** The codebase is designed for flexibility. You can easily swap out the core components, such as the Large Language Model (LLM), embedding model, or document processing logic, to suit your specific needs.

---

## ⚠️ Notes & Limitations

* **Local Dependencies:** OCR and PDF/image extraction require `Tesseract` and `Poppler` to be installed on your local machine.
* **Scalability:** This template is designed for demonstration purposes, not for production-level, high-traffic deployments.
* **Excluded Files:** Large vector store and data files are excluded to keep the repository size manageable.
