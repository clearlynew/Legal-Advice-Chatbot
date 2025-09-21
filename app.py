import streamlit as st
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_groq import ChatGroq
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from pdf2image import convert_from_bytes
from dotenv import load_dotenv
import re
import os
from PIL import Image
import pytesseract
import PyPDF2
import platform

# =======================
# Load .env
# =======================
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
GROQ_TEMPERATURE = float(os.getenv("GROQ_TEMPERATURE", 0.1))
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
TESSERACT_PATH = os.getenv("TESSERACT_PATH")
POPPLER_PATH = os.getenv("POPPLER_PATH")

# =======================
# Configure Tesseract Path
# =======================
try:
    if TESSERACT_PATH:
        pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
    else:
        if platform.system() == "Windows":
            pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        elif platform.system() == "Darwin":  # macOS
            pytesseract.pytesseract.tesseract_cmd = '/usr/local/bin/tesseract'
        else:  # Linux
            pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'
except Exception as e:
    print(f"Warning: Could not set Tesseract path: {e}")

# =======================
# Session State Setup
# =======================
def init_session_state():
    if 'chat_sessions' not in st.session_state:
        st.session_state.chat_sessions = []
    if 'current_session_id' not in st.session_state:
        st.session_state.current_session_id = None
    if 'qa_chain' not in st.session_state:
        st.session_state.qa_chain = None
    if 'llm' not in st.session_state:
        st.session_state.llm = None
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'is_processing' not in st.session_state:
        st.session_state.is_processing = False
    if 'input_key' not in st.session_state:
        st.session_state.input_key = 0
    if 'uploaded_file' not in st.session_state:
        st.session_state.uploaded_file = None
    if 'uploaded_text' not in st.session_state:
        st.session_state.uploaded_text = ""

# =======================
# File Processing
# =======================
def extract_text_from_pdf(pdf_file):
    try:
        pdf_file.seek(0)
        reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

        if not text.strip():
            # OCR fallback
            pdf_file.seek(0)
            images = convert_from_bytes(pdf_file.read(), poppler_path=POPPLER_PATH)
            ocr_text = ""
            for i, img in enumerate(images):
                page_text = pytesseract.image_to_string(img, config="--psm 6")
                if page_text.strip():
                    ocr_text += f"\n--- Page {i+1} ---\n{page_text}\n"
            return ocr_text.strip()

        return text.strip()
    except Exception as e:
        st.error(f"Error extracting text from PDF: {e}")
        return ""

def extract_text_from_image(image_file):
    try:
        image_file.seek(0)
        image = Image.open(image_file)

        if image.mode != 'RGB':
            image = image.convert('RGB')

        text = pytesseract.image_to_string(image, config='--psm 6')
        if not text.strip():
            st.warning("No text could be extracted from this image.")
            return ""
        return text.strip()
    except pytesseract.TesseractNotFoundError:
        st.error("❌ Tesseract OCR not found. Please install it first.")
        return ""
    except Exception as e:
        st.error(f"Error performing OCR: {e}")
        return ""

def extract_text_from_txt(txt_file):
    try:
        txt_file.seek(0)
        content = txt_file.read()
        if isinstance(content, bytes):
            text = content.decode('utf-8')
        else:
            text = str(content)
        return text.strip()
    except UnicodeDecodeError:
        try:
            txt_file.seek(0)
            content = txt_file.read()
            text = content.decode('latin-1')
            return text.strip()
        except Exception as e:
            st.error(f"Error decoding text file: {str(e)}")
            return ""
    except Exception as e:
        st.error(f"Error reading text file: {str(e)}")
        return ""

def process_uploaded_file(uploaded_file):
    if uploaded_file is None:
        return ""

    file_type = uploaded_file.type
    file_extension = uploaded_file.name.split('.')[-1].lower()
    st.info(f"Processing file: {uploaded_file.name} (Type: {file_type})")

    extracted_text = ""
    if file_type == "application/pdf" or file_extension == "pdf":
        st.info("Extracting text from PDF...")
        extracted_text = extract_text_from_pdf(uploaded_file)
    elif file_type.startswith("image/") or file_extension in ["png", "jpg", "jpeg", "bmp", "gif", "tiff"]:
        st.info("Performing OCR on image...")
        extracted_text = extract_text_from_image(uploaded_file)
    elif file_type == "text/plain" or file_extension == "txt":
        st.info("Reading text file...")
        extracted_text = extract_text_from_txt(uploaded_file)
    else:
        st.warning(f"Unsupported file type: {file_type}")
        return ""

    if extracted_text:
        st.success(f"Extracted {len(extracted_text)} characters from {uploaded_file.name}")
    else:
        st.error(f"Failed to extract text from {uploaded_file.name}")

    return extracted_text

# =======================
# QA Chain Setup
# =======================
@st.cache_resource
def setup_qa_chain():
    try:
        llm = ChatGroq(
            model=GROQ_MODEL,
            api_key=GROQ_API_KEY,
            temperature=GROQ_TEMPERATURE
        )

        prompt_template = """You are a legal AI assistant.
Use the following legal documents and context to answer the question.
If the information is not available in the provided context, say so clearly.

Context:
{context}

Question:
{question}

Answer:"""

        prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
        qa_chain = LLMChain(llm=llm, prompt=prompt, output_key="result")
        return qa_chain, llm
    except Exception as e:
        st.error(f"Error setting up QA chain: {str(e)}")
        return None, None

# =======================
# Text Sanitization
# =======================
def sanitize_text(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    text = re.sub(r'`(.*?)`', r'\1', text)
    return text

# =======================
# Main App
# =======================
def main():
    st.set_page_config(page_title="Legali - Legal Advice Chatbot", layout="wide")
    init_session_state()

    if st.session_state.qa_chain is None:
        with st.spinner("Initializing Legal AI Assistant..."):
            qa_chain, llm = setup_qa_chain()
            if qa_chain:
                st.session_state.qa_chain, st.session_state.llm = qa_chain, llm
            else:
                st.error("Failed to initialize AI assistant.")
                st.stop()

    # -------------------
    # Sidebar
    # -------------------
    with st.sidebar:
        st.title("🏛️ Legali Options")
        sessions = st.session_state.chat_sessions
        session_labels = [f"Chat {i+1}" for i in range(len(sessions))] + ["New Chat"]
        selected = st.radio(
            "Your Chats",
            options=session_labels,
            index=len(sessions) if st.session_state.current_session_id is None else st.session_state.current_session_id
        )
        if st.session_state.current_session_id is not None and st.session_state.messages:
            st.session_state.chat_sessions[st.session_state.current_session_id] = st.session_state.messages.copy()

        if selected == "New Chat":
            st.session_state.current_session_id = len(sessions)
            st.session_state.chat_sessions.append([])
            st.session_state.messages = []
        else:
            session_index = session_labels.index(selected)
            st.session_state.current_session_id = session_index
            if session_index < len(st.session_state.chat_sessions):
                st.session_state.messages = st.session_state.chat_sessions[session_index].copy()
            else:
                st.session_state.messages = []

        st.markdown("---")
        st.markdown("### 📁 File Upload")
        uploaded_file = st.file_uploader(
            "Upload a document or image",
            type=["pdf", "txt", "png", "jpg", "jpeg", "bmp", "gif", "tiff"],
            key=f"sidebar_uploader_{st.session_state.input_key}",
            disabled=st.session_state.is_processing,
        )

        if uploaded_file is not None:
            st.session_state.uploaded_file = uploaded_file
            st.session_state.uploaded_text = process_uploaded_file(uploaded_file)
            st.success(f"📎 {uploaded_file.name} uploaded successfully")

        if st.session_state.uploaded_file is not None:
            if st.button("Clear File", key=f"clear_file_{st.session_state.input_key}"):
                st.session_state.uploaded_file = None
                st.session_state.uploaded_text = ""
                st.session_state.input_key += 1
                st.rerun()

        st.markdown("---")
        st.markdown("### ℹ️ About")
        st.info("Legali is your AI legal assistant. Upload a file or ask a legal question.")

    # -------------------
    # Chat Area
    # -------------------
    st.title("🏛️ Legali - Legal Advice Chatbot")
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            if msg["role"] == "user" and "file_info" in msg:
                st.caption(f"📎 Attached: {msg['file_info']}")
            st.markdown(msg["content"])

    user_input = st.chat_input("Ask your legal question...")

    if user_input and not st.session_state.is_processing:
        st.session_state.is_processing = True
        uploaded_content = ""
        file_info = ""

        if st.session_state.uploaded_file and st.session_state.uploaded_text:
            extracted_text = st.session_state.uploaded_text
            max_chars = 2000
            if len(extracted_text) > max_chars:
                uploaded_content = f"\n\nContent from {st.session_state.uploaded_file.name}:\n{extracted_text[:max_chars]}...\n[Content truncated]"
            else:
                uploaded_content = f"\n\nContent from {st.session_state.uploaded_file.name}:\n{extracted_text}"
            file_info = st.session_state.uploaded_file.name

        user_message = {"role": "user", "content": user_input.strip()}
        if file_info:
            user_message["file_info"] = file_info
        st.session_state.messages.append(user_message)

        with st.chat_message("user"):
            if file_info:
                st.caption(f"📎 Attached: {file_info}")
            st.markdown(user_input.strip())

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    context_to_use = uploaded_content if uploaded_content.strip() else ""
                    result = st.session_state.qa_chain.invoke({
                        "question": user_input.strip(),
                        "context": context_to_use
                    })
                    response = result.get("result", "I couldn't generate a response.")
                    clean_response = sanitize_text(response)
                    if file_info:
                        clean_response = f"*[Analyzed with uploaded file: {file_info}]*\n\n{clean_response}"

                    st.markdown(clean_response)
                    assistant_message = {"role": "assistant", "content": clean_response}
                    st.session_state.messages.append(assistant_message)

                    if st.session_state.current_session_id is not None:
                        st.session_state.chat_sessions[st.session_state.current_session_id] = st.session_state.messages.copy()
                except Exception as e:
                    error_message = f"Error generating response: {e}"
                    st.error(error_message)
                    assistant_message = {"role": "assistant", "content": error_message}
                    st.session_state.messages.append(assistant_message)
                finally:
                    st.session_state.is_processing = False
                    if st.session_state.uploaded_file:
                        st.session_state.uploaded_file = None
                        st.session_state.uploaded_text = ""
                        st.session_state.input_key += 1
                    st.rerun()

if __name__ == "__main__":
    main()
