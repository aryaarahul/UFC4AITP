import streamlit as st
import os
import tempfile
import requests
from markitdown import MarkItDown

st.set_page_config(page_title="Universal Converter", page_icon="📑")

def main():
    st.title("📑 Universal File to Text")
    
    # Initialize MarkItDown with a robust session
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0"})
    md = MarkItDown(requests_session=session)

    # File Uploader
    files = st.file_uploader("Upload Word, Excel, PDF, or PPT", accept_multiple_files=True)

    if files:
        for f in files:
            # 1. Create a physical temp file WITH the correct extension
            # MarkItDown USES the extension to decide which engine to use!
            ext = os.path.splitext(f.name)[1]
            with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
                tmp.write(f.getvalue())
                tmp_path = tmp.name

            try:
                # 2. Conversion
                with st.spinner(f"Reading {f.name}..."):
                    result = md.convert(tmp_path)
                    text = result.text_content

                # 3. UI and Download
                with st.expander(f"📄 {f.name}", expanded=True):
                    st.text_area("Preview", text, height=200, key=f"area_{f.name}")
                    st.download_button("Download .md", text, f"{f.name}.md", key=f"dl_{f.name}")

            except Exception as e:
                st.error(f"⚠️ Could not read {f.name}. Error: {str(e)}")
            
            finally:
                # 4. Clean up the temp file
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)

if __name__ == "__main__":
    main()
