import streamlit as st
import os
from markitdown import MarkItDown
import requests

# App Configuration
st.set_page_config(page_title="Universal Document Reader", page_icon="📄")

def main():
    st.title("📄 Universal Document Reader")
    st.markdown("Convert your Office docs, PDFs, and HTML into clean Markdown instantly.")

    # [1] Initialize the Engine with Technical Constraints [3]
    # MarkItDown uses requests internally for certain tasks; 
    # we can pass a pre-configured requests session if needed, 
    # but for local files, we initialize the standard object.
    md = MarkItDown()

    # [2] Interface: Upload Area
    uploaded_files = st.file_uploader(
        "Drag and drop files here", 
        type=["docx", "xlsx", "pptx", "pdf", "html", "zip"],
        accept_multiple_files=True
    )

    if uploaded_files:
        for uploaded_file in uploaded_files:
            file_name = uploaded_file.name
            base_name = os.path.splitext(file_name)[0]

            try:
                # To process with MarkItDown, we save the uploaded bytes to a temp file
                # because some parsers within the library require a file path.
                temp_path = f"temp_{file_name}"
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                # [1] The Engine: Conversion logic
                result = md.convert(temp_path)
                content = result.text_content

                # [2] Interface: Instant Preview
                with st.expander(f"👁️ Preview: {file_name}", expanded=True):
                    st.text_area(
                        label="Extracted Content",
                        value=content,
                        height=300,
                        key=f"text_{file_name}"
                    )

                    # [2] Download Options
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.download_button(
                            label="📥 Download as Markdown",
                            data=content,
                            file_name=f"{base_name}_converted.md",
                            mime="text/markdown",
                            key=f"md_{file_name}"
                        )
                    
                    with col2:
                        st.download_button(
                            label="📥 Download as Text",
                            data=content,
                            file_name=f"{base_name}_converted.txt",
                            mime="text/plain",
                            key=f"txt_{file_name}"
                        )

                # Cleanup temp file
                os.remove(temp_path)

            except Exception as e:
                # [3] Resilience: Error Handling
                st.error(f"⚠️ Could not read {file_name}. Please check the format.")
                # Log the specific error to the console for the developer
                print(f"Error processing {file_name}: {e}")

if __name__ == "__main__":
    main()
