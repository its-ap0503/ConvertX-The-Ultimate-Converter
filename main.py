import streamlit as st
import io
import os
from fpdf import FPDF
from pdf2docx import Converter
from docx import Document
import fitz  # PyMuPDF

# Background and size limit note
st.markdown("""
<style>
.stApp {
    background-image: url("https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=1400&q=80");
    background-size: cover;
    background-repeat: no-repeat;
    background-position: center;
    background-attachment: fixed;
    animation: movebg 60s linear infinite;
    min-height: 100vh;
}
@keyframes movebg {
    0%   { background-position: 50% 0%; }
    50%  { background-position: 50% 100%; }
    100% { background-position: 50% 0%; }
}
.custom-note {
    font-size: 15px;
    color: white;
    background: #00000088;
    padding: 10px 15px;
    border-radius: 10px;
    display: inline-block;
    margin-bottom: 10px;
    font-weight: 500;
}
</style>
<div class="custom-note">Note: Max upload size is 10 MB</div>
""", unsafe_allow_html=True)

def text_to_pdf(uploaded_file):
    text = uploaded_file.read().decode("utf-8")
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for line in text.splitlines():
        pdf.cell(200, 10, txt=line, ln=True)
    pdf_output = pdf.output(dest="S").encode("latin1")
    return io.BytesIO(pdf_output)

def docx_to_pdf(uploaded_file):
    doc = Document(uploaded_file)
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for para in doc.paragraphs:
        pdf.multi_cell(200, 10, txt=para.text)
    pdf_output = pdf.output(dest="S").encode("latin1")
    return io.BytesIO(pdf_output)

def pdf_to_text(uploaded_file):
    text_output = ""
    pdf = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    for page in pdf:
        text_output += page.get_text()
    return io.BytesIO(text_output.encode("utf-8"))

def pdf_to_docx(uploaded_file):
    input_pdf = "temp_input.pdf"
    output_docx = "temp_output.docx"
    with open(input_pdf, "wb") as f:
        f.write(uploaded_file.read())
    cv = Converter(input_pdf)
    cv.convert(output_docx)
    cv.close()
    with open(output_docx, "rb") as f:
        docx_bytes = io.BytesIO(f.read())
    os.remove(input_pdf)
    os.remove(output_docx)
    return docx_bytes

st.title("📂ConvertX - File Converter")
uploaded_file = st.file_uploader("Upload your file:", type=["pdf", "docx", "txt"])

if uploaded_file:
    if uploaded_file.size > 10 * 1024 * 1024:
        st.error("❌ File size exceeds 10MB limit.")
    else:
        options = [".pdf", ".docx", ".txt"]
        convert_to = st.selectbox("Convert to format:", options)
        st.success("File uploaded successfully.")
        filename = uploaded_file.name
        base = os.path.splitext(filename)[0]
        ext = os.path.splitext(filename)[1].lower()

        if st.button("Convert"):
            out_file, mime_type = None, None

            if ext == ".txt" and convert_to == ".pdf":
                out_file = text_to_pdf(uploaded_file)
                mime_type = "application/pdf"
            elif ext == ".docx" and convert_to == ".pdf":
                out_file = docx_to_pdf(uploaded_file)
                mime_type = "application/pdf"
            elif ext == ".pdf" and convert_to == ".txt":
                out_file = pdf_to_text(uploaded_file)
                mime_type = "text/plain"
            elif ext == ".pdf" and convert_to == ".docx":
                out_file = pdf_to_docx(uploaded_file)
                mime_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

            if out_file:
                st.success("✅ File converted!")
                st.download_button(
                    label=f"Download {base}{convert_to}",
                    data=out_file,
                    file_name=f"{base}{convert_to}",
                    mime=mime_type
                )
            else:
                st.warning("⚠️ Unsupported file conversion.")
else:
    st.info("Upload a file to get started.")
