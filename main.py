import streamlit as st
from fpdf import FPDF
from pdf2docx import Converter
import io
import os
from docx import Document
import fitz  # PyMuPDF

# 📅 Responsive background with animation for all screen sizes
st.markdown(
    """
    <style>
    html, body, .stApp {
        height: 100%;
        margin: 0;
        padding: 0;
    }
    .stApp {
        background-image: url("https://images.unsplash.com/photo-1596495577886-d920f1fb7238?auto=format&fit=crop&w=1350&q=80");
        background-size: cover;
        background-repeat: no-repeat;
        background-position: center;
        background-attachment: scroll;
        animation: movebg 60s linear infinite;
    }
    @keyframes movebg {
        0%   { background-position: 50% 0%; }
        50%  { background-position: 50% 100%; }
        100% { background-position: 50% 0%; }
    }
    .slide-in {
        animation: slideIn 1s ease-out forwards;
        opacity: 0;
        font-size: 1.2rem;
        color: white;
        margin-top: 1rem;
        text-shadow: 1px 1px 3px black;
    }
    @keyframes slideIn {
        0%   { transform: translateX(-100%); opacity: 0; }
        100% { transform: translateX(0); opacity: 1; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# 🤖 Conversion Functions
def pdf_to_docx(uploaded_file):
    input_pdf_path = "temp_input.pdf"
    output_docx_path = "temp_output.docx"
    with open(input_pdf_path, "wb") as f:
        f.write(uploaded_file.read())
    cv = Converter(input_pdf_path)
    cv.convert(output_docx_path)
    cv.close()
    with open(output_docx_path, "rb") as f:
        docx_bytes = io.BytesIO(f.read())
        docx_bytes.seek(0)
    os.remove(input_pdf_path)
    os.remove(output_docx_path)
    return docx_bytes

def pdf_to_text(uploaded_file):
    text_output = ""
    pdf = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    for page in pdf:
        text_output += page.get_text()
    pdf.close()
    output_txt = io.BytesIO(text_output.encode("utf-8"))
    output_txt.seek(0)
    return output_txt

def docx_to_pdf(uploaded_file):
    doc = Document(uploaded_file)
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for para in doc.paragraphs:
        pdf.multi_cell(200, 10, txt=para.text)
    pdf_output_str = pdf.output(dest="S").encode("latin1")
    output_pdf = io.BytesIO(pdf_output_str)
    output_pdf.seek(0)
    return output_pdf

def text_to_pdf(uploaded_file):
    text = uploaded_file.read().decode("utf-8")
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for line in text.splitlines():
        pdf.cell(200, 10, txt=line, ln=True)
    pdf_output_str = pdf.output(dest="S").encode("latin1")
    output_pdf = io.BytesIO(pdf_output_str)
    output_pdf.seek(0)
    return output_pdf

# 🚀 App UI
st.title("ConvertX - File Converter")
uploaded_file = st.file_uploader("Upload your file:")

if uploaded_file:
    options = [".docx", ".pdf", ".txt"]
    select_file_format = st.selectbox("Convert to:", options)
    st.success("File uploaded successfully.")

    up_filename = uploaded_file.name
    up_file_extension = up_filename.split(".")[-1].lower()
    base_filename = os.path.splitext(up_filename)[0]

    if st.button("Convert"):
        out_file = None
        mime_type = None

        if up_file_extension == "txt" and select_file_format == ".pdf":
            out_file = text_to_pdf(uploaded_file)
            mime_type = "application/pdf"

        elif up_file_extension == "docx" and select_file_format == ".pdf":
            out_file = docx_to_pdf(uploaded_file)
            mime_type = "application/pdf"

        elif up_file_extension == "pdf" and select_file_format == ".txt":
            out_file = pdf_to_text(uploaded_file)
            mime_type = "text/plain"

        elif up_file_extension == "pdf" and select_file_format == ".docx":
            out_file = pdf_to_docx(uploaded_file)
            mime_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

        if out_file and mime_type:
            st.markdown(
                '<div class="slide-in">Your file is ready to download!</div>',
                unsafe_allow_html=True,
            )
            st.download_button(
                label=f"Download {base_filename}{select_file_format}",
                data=out_file,
                file_name=f"{base_filename}{select_file_format}",
                mime=mime_type,
            )
        else:
            st.warning("Conversion not supported yet.")
else:
    st.info("Upload a file to begin converting.")
