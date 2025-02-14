import os
import json
import pdfplumber
from transformers import pipeline

# Set folder path for PDFs
folder_path = "E:\python\SAVED_PDF"
output_json_path = "E:\python\LLM_PROJECT\ financials.json"

# Ensure output folder exists
os.makedirs(os.path.dirname(output_json_path), exist_ok=True)

# Load FinBERT model
nlp = pipeline("ner", model="ProsusAI/finbert", tokenizer="ProsusAI/finbert")

def extract_text_from_pdf(pdf_path):
    """Extracts text from a given PDF file."""
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            extracted_text = page.extract_text()
            if extracted_text:
                text += extracted_text + "\n"
    return text.strip()

def extract_entities(text):
    """Extracts named entities using FinBERT."""
    ner_results = nlp(text[:512])  # Process only first 512 tokens to avoid model errors

    structured_data = {"Revenue": "", "Expenses": "", "Profit": "", "Loss": "", "Other": []}

    for entity in ner_results:
        word = entity['word']
        label = entity['entity'].upper()

        if "REVENUE" in label:
            structured_data["Revenue"] = word
        elif "EXPENSE" in label:
            structured_data["Expenses"] = word
        elif "PROFIT" in label:
            structured_data["Profit"] = word
        elif "LOSS" in label:
            structured_data["Loss"] = word
        else:
            structured_data["Other"].append({label: word})

    return structured_data

def process_all_pdfs(folder_path):
    """Processes all PDFs in a folder and saves extracted data as JSON."""
    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"Folder '{folder_path}' does not exist!")

    financial_data = {}

    for filename in os.listdir(folder_path):
        if filename.lower().endswith(".pdf"):
            file_path = os.path.join(folder_path, filename)
            extracted_text = extract_text_from_pdf(file_path)
            if extracted_text:
                structured_data = extract_entities(extracted_text)
                financial_data[filename] = structured_data

    # Save extracted data as JSON
    with open(output_json_path, "w", encoding="utf-8") as json_file:
        json.dump(financial_data, json_file, indent=4)

    print(f"Financial data saved to {output_json_path}")

# Run the script
process_all_pdfs(folder_path)
