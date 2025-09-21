Legali - Legal Advice Chatbot (Template/Showcase)

Legali is an AI-powered legal assistant that allows users to ask legal questions and optionally upload documents (PDF, TXT, images).

Note: This repo is a template/showcase. Large datasets and vectorstore files are excluded. It demonstrates code structure and workflow.

Features

AI-powered chat interface for legal questions

Handles multiple chat sessions

File upload support (PDF, TXT, images) with text extraction (OCR optional)

Modular code: easy to replace LLM, embeddings, or file-processing logic

File Structure
Legali/
├─ app.py                 # Main Streamlit app
├─ requirements.txt       # Python dependencies
├─ Script/
│   ├─ load.py            # Load and preprocess documents
│   ├─ preprocess.py      # Text cleaning & preparation
│   ├─ query.py           # Query processing and AI invocation
│   ├─ test.py            # Example usage of modules
│   └─ vectorstore/       # Vectorstore files (excluded due to size)
├─ Data/                  # Example / placeholder files (small)
├─ .gitignore             # Ignores large files & environment configs
└─ README.md              # This file

How the Code Works

app.py – Streamlit interface

Handles user input and file uploads

Maintains chat sessions

Sends user questions + context to LLM

Script/load.py – Loads and extracts text from PDF/TXT/Image

Uses PyPDF2 and optional OCR (Tesseract)

Can be modified for other formats

Script/preprocess.py – Cleans & preprocesses text

Sanitization, splitting, or embedding prep

Script/query.py – Sends processed text + questions to AI

Uses LLMChain (LangChain) in this template

Easily replaceable with other LLMs

Script/test.py – Demonstrates module usage and example workflow

Installation & Usage (Template Only)
# Clone the repo
git clone https://github.com/<username>/LegaliApp.git
cd LegaliApp

# Create virtual environment
python -m venv venv
# Activate it
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the app (optional, dummy data only)
streamlit run app.py


⚠️ The app won’t fully run without large vectorstore/data files. This repo is meant as a starting point for your own implementation.

How to Customize

Replace ChatGroq with any LLM you have access to

Replace Script/vectorstore/* with your own embeddings/vectorstore

Modify Script/load.py to support additional file types

Add sample small PDFs or text files in Data/ to demonstrate functionality

Notes / Limitations

OCR and PDF/image extraction require Tesseract & Poppler installed locally

Large files are excluded to keep repo lightweight

Designed as a template, not a fully runnable production app
