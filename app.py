import streamlit as st
import fitz  # PyMuPDF
import re
import pandas as pd
import os

# Function to extract metadata
def extract_metadata_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()

    # Normalize text
    text = text.replace("\n", " ")  # Fixed line

    metadata = {"Filename": pdf_path}

    # Title (first line)
    doc = fitz.open(pdf_path)
    first_page_text = doc[0].get_text("text").split("\n")
    doc.close()
    metadata["Title"] = first_page_text[0] if first_page_text else "Not found"

    # Authors (second line)
    metadata["Authors"] = first_page_text[1] if len(first_page_text) > 1 else "Not found"

    # DOI
    doi_match = re.search(r"\b10\.\d{4,9}/[-._;()/:A-Z0-9]+", text, re.I)
    metadata["DOI"] = doi_match.group(0) if doi_match else "Not found"

    # Publisher
    publisher_match = re.search(r"(Elsevier|Springer|IEEE|Wiley|ACM|Taylor & Francis|Nature|Science|AMS)", text, re.I)
    metadata["Publisher"] = publisher_match.group(0) if publisher_match else "Not found"

    # Volume
    volume_match = re.search(r"Vol\.?\s*(\d+)", text, re.I)
    metadata["Volume"] = volume_match.group(1) if volume_match else "Not found"

    # Issue
    issue_match = re.search(r"No\.?\s*(\d+)", text, re.I)
    metadata["Issue"] = issue_match.group(1) if issue_match else "Not found"

    # Pages
    pages_match = re.search(r"(\d+)\s*[-–]\s*(\d+)", text)
    metadata["Pages"] = pages_match.group(0) if pages_match else "Not found"

    # Year
    year_match = re.search(r"\b(19\d{2}|20\d{2}|2025)\b", text)
    metadata["Year"] = year_match.group(0) if year_match else "Not found"

    # Publication Date
    pub_date_match = re.search(r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}", text, re.I)
    metadata["Publication Date"] = pub_date_match.group(0) if pub_date_match else "Not found"

    return metadata

# Streamlit interface
st.title("PDF Metadata Extractor")

# Upload multiple PDFs
uploaded_files = st.file_uploader("Choose PDFs", accept_multiple_files=True, type=["pdf"])

if uploaded_files:
    all_metadata = []
    for uploaded_file in uploaded_files:
        file_path = os.path.join("uploads", uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        metadata = extract_metadata_from_pdf(file_path)
        all_metadata.append(metadata)

    # Convert to DataFrame
    df = pd.DataFrame(all_metadata)

    # Show the extracted data
    st.write(df)

    # Download button for the Excel file
    excel_filename = "metadata_output.xlsx"
    df.to_excel(excel_filename, index=False)
    st.download_button("Download Excel File", data=open(excel_filename, 'rb').read(), file_name=excel_filename)
