import streamlit as st
import os
import tempfile
import requests
from markitdown import MarkItDown

st.set_page_config(page_title="Universal Converter Pro", page_icon="📑", layout="wide")

def get_file_size_label(size_bytes):
    """Converts bytes to a human-readable string (MB/KB)."""
    if size_bytes == 0: return "0 B"
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024

def main():
    st.title("📑 Universal File to Text")
    
    # Initialize Engine
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0"})
    md = MarkItDown(requests_session=session)

    files = st.file_uploader("Upload Word, Excel, PDF, or PPT", accept_multiple_files=True)

    if files:
        for f in files:
            ext = os.path.splitext(f.name)[1]
            # Create physical temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
                tmp.write(f.getvalue())
                tmp_path = tmp.name
                original_size = os.path.getsize(tmp_path)

            try:
                with st.spinner(f"Processing {f.name}..."):
                    result = md.convert(tmp_path)
                    text_content = result.text_content
                    converted_size = len(text_content.encode('utf-8'))

                # --- UI: Tabs Interface ---
                with st.container(border=True):
                    st.subheader(f"📄 {f.name}")
                    tab1, tab2 = st.tabs(["Preview & Download", "📊 File Size Comparison"])

                    with tab1:
                        st.text_area("Content Preview", text_content, height=250, key=f"area_{f.name}")
                        c1, c2 = st.columns(2)
                        c1.download_button("Download .md", text_content, f"{f.name}.md", key=f"md_{f.name}")
                        c2.download_button("Download .txt", text_content, f"{f.name}.txt", key=f"txt_{f.name}")

                    with tab2:
                        # Calculation
                        diff_percent = ((original_size - converted_size) / original_size) * 100
                        
                        # Display Table
                        data = [
                            {"Metric": "Original File Size", "Value": get_file_size_label(original_size)},
                            {"Metric": "Converted .txt Size", "Value": get_file_size_label(converted_size)}
                        ]
                        st.table(data)
                        
                        # Display Percentage
                        st.success(f"💡 **Optimization:** Text version is {diff_percent:.1f}% smaller than the original.")

            except Exception as e:
                st.error(f"⚠️ Could not read {f.name}. Error: {str(e)}")
            
            finally:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)

if __name__ == "__main__":
    main()
