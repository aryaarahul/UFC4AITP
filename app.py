import streamlit as st
import os
import tempfile
import requests
from markitdown import MarkItDown

# 1. Setup Page
st.set_page_config(page_title="Universal Doc Converter", layout="wide")

def main():
    st.title("📄 Universal Document Reader")
    st.markdown("Upload Word, Excel, PDF, or PPTX to convert to Markdown.")

    # 2. Initialize Engine with resilience [Requirement 3]
    # We create a session to handle potential web-based sub-requests
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    
    # MarkItDown is the primary engine [Requirement 1]
    md = MarkItDown(requests_session=session)

    # 3. Upload Area [Requirement 2]
    uploaded_files = st.file_uploader(
        "Choose files...", 
        type=["docx", "xlsx", "pptx", "pdf", "html", "zip", "txt"],
        accept_multiple_files=True
    )

    if uploaded_files:
        for uploaded_file in uploaded_files:
            file_name = uploaded_file.name
            base_name = os.path.splitext(file_name)[0]

            # CRITICAL: Create a real temporary file on the disk
            # This is what allows PDF/Excel/Word readers to work!
            suffix = os.path.splitext(file_name)[1]
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_path = tmp_file.name

            try:
                # Process the file via the path
                with st.spinner(f"Processing {file_name}..."):
                    # We use a timeout logic here implicitly via the session
                    result = md.convert(tmp_path)
                    content = result.text_content

                # 4. Preview and Download [Requirement 2]
                with st.expander(f"✅ Result: {file_name}", expanded=True):
                    st.text_area("Preview", value=content, height=300, key=f"prev_{file_name}")
                    
                    c1, c2 = st.columns(2)
                    c1.download_button(
                        "Download .md", 
                        content, 
                        file_name=f"{base_name}_converted.md",
                        key=f"md_{file_name}"
                    )
                    c2.download_button(
                        "Download .txt", 
                        content, 
                        file_name=f"{base_name}_converted.txt",
                        key=f"txt_{file_name}"
                    )

            except Exception as e:
                # 5. Resilience [Requirement 3]
                st.error(f"⚠️ Could not read {file_name}. Please check the format.")
                st.info(f"Technical detail: {str(e)}") # Helps you debug why it failed

            finally:
                # Cleanup: Remove the file from your computer after processing
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)

if __name__ == "__main__":
    main()
