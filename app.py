# streamlit_app.py

import streamlit as st
import fitz  # PyMuPDF
import re
import pandas as pd
import zipfile
import io

st.title("PDF Metadata Extractor to Excel")

def extract_metadata_from_pdf(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()

    text = text.replace("\n", " ")
    metadata = {}

    doc = fitz.open(stream=file.getvalue(), filetype="pdf")
    first_page_text = doc[0].get_text("text").split("\n")
    doc.close()

    metadata["Title"] = first_page_text[0] if first_page_text else "Not found"
    metadata["Authors"] = first_page_text[1] if len(first_page_text) > 1 else "Not found"
    metadata["DOI"] = re.search(r"\b10\.\d{4,9}/[-._;()/:A-Z0-9]+", text, re.I)
    metadata["DOI"] = metadata["DOI"].group(0) if metadata["DOI"] else "Not found"
    metadata["Publisher"] = re.search(r"(Elsevier|Springer|IEEE|Wiley|ACM|Taylor & Francis|Nature|Science|AMS)", text, re.I)
    metadata["Publisher"] = metadata["Publisher"].group(0) if metadata["Publisher"] else "Not found"
    metadata["Volume"] = re.search(r"Vol\.?\s*(\d+)", text, re.I)
    metadata["Volume"] = metadata["Volume"].group(1) if metadata["Volume"] else "Not found"
    metadata["Issue"] = re.search(r"No\.?\s*(\d+)", text, re.I)
    metadata["Issue"] = metadata["Issue"].group(1) if metadata["Issue"] else "Not found"
    metadata["Pages"] = re.search(r"(\d+)\s*[-–]\s*(\d+)", text)
    metadata["Pages"] = metadata["Pages"].group(0) if metadata["Pages"] else "Not found"
    metadata["Year"] = re.search(r"\b(19\d{2}|20\d{2}|2025)\b", text)
    metadata["Year"] = metadata["Year"].group(0) if metadata["Year"] else "Not found"
    metadata["Publication Date"] = re.search(r"(January|February|...|December)\s+\d{4}", text, re.I)
    metadata["Publication Date"] = metadata["Publication Date"].group(0) if metadata["Publication Date"] else "Not found"

    return metadata

uploaded_files = st.file_uploader("Upload PDF files or ZIP", type=["pdf", "zip"], accept_multiple_files=True)

if uploaded_files:
    all_metadata = []

    for uploaded in uploaded_files:
        if uploaded.name.endswith(".zip"):
            with zipfile.ZipFile(uploaded, "r") as archive:
                for filename in archive.namelist():
                    if filename.endswith(".pdf"):
                        with archive.open(filename) as file:
                            metadata = extract_metadata_from_pdf(file)
                            metadata["Filename"] = filename
                            all_metadata.append(metadata)
        else:
            metadata = extract_metadata_from_pdf(uploaded)
            metadata["Filename"] = uploaded.name
            all_metadata.append(metadata)

    df = pd.DataFrame(all_metadata)
    st.dataframe(df)

    output = io.BytesIO()
    df.to_excel(output, index=False, engine='openpyxl')
    st.download_button("Download Excel Report", data=output.getvalue(), file_name="metadata_report.xlsx")
