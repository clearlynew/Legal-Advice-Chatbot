import os
import fitz  # PyMuPDF

data_root = r'C:\Legal Advice Chatbot\Data\Indian Legal Documents LuRA'

def chunk_text(text, max_length=1000):
    words = text.split()
    for i in range(0, len(words), max_length):
        yield ' '.join(words[i:i+max_length])

def extract_text_pymupdf(pdf_path):
    text = ""
    doc = fitz.open(pdf_path)
    for page in doc:
        text += page.get_text()
    return text

def preprocess_pdfs(root_folder):
    for root, dirs, files in os.walk(root_folder):
        for file in files:
            if file.lower().endswith('.pdf'):
                pdf_file = os.path.join(root, file)
                print(f"Extracting text from: {pdf_file}")
                pdf_text = extract_text_pymupdf(pdf_file)

                base_name = os.path.splitext(file)[0]
                # Save chunks in same folder as txt files
                for idx, chunk in enumerate(chunk_text(pdf_text, max_length=1000)):
                    chunk_file = os.path.join(root, f"{base_name}_chunk{idx+1}.txt")
                    with open(chunk_file, 'w', encoding='utf-8') as f:
                        f.write(chunk)
                print(f"Saved chunks for {file}\n{'-'*50}")

if __name__ == "__main__":
    preprocess_pdfs(data_root)
