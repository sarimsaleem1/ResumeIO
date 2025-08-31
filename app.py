import streamlit as st
import requests
from bs4 import BeautifulSoup
import io
from xhtml2pdf import pisa
from docx import Document
import time

# Page configuration
st.set_page_config(
    layout="wide", 
    page_title="Resume IO Downloader"
)

# Session state initialization
if "render_token" not in st.session_state:
    st.session_state["render_token"] = ""
if "render_token_bool" not in st.session_state:
    st.session_state["render_token_bool"] = True

# Navigation
page = st.sidebar.radio("Navigation", ["Home", "Download Resume", "About"])

# Home Page
if page == "Home":
    st.title("Resume IO Downloader")
    st.write("""
        To fetch your resume from resume.io, you need to get your `rendering token` from 
        https://resume.io/api/app/resumes
    """)
    
    st.markdown("""
    ### How to get your renderToken:
    1. Go to https://resume.io and open your resume
    2. Open your browser's developer tools (F12)
    3. Go to the Network tab
    4. Refresh the page and look for a request to `https://resume.io/api/app/resumes/[some_id]`
    5. Click on that request and check the Response tab
    6. Copy the `rendering token` from the response
    """)
    
    render_token = st.text_input("Enter renderToken", placeholder="Paste renderToken here...")
    st.session_state["render_token"] = render_token
    
    if st.button("Submit"):
        if st.session_state["render_token"]:
            st.session_state["render_token_bool"] = False
            st.success("Token accepted! Proceed to download page.")
        else:
            st.error("renderToken required to proceed.")
            st.session_state["render_token_bool"] = True
    
    st.button(
        "Go to Download Resume", 
        disabled=st.session_state["render_token_bool"],
        on_click=lambda: st.session_state.update({"page": "Download Resume"})
    )

# Download Resume Page
elif page == "Download Resume":
    if st.session_state["render_token_bool"]:
        st.error("renderToken required to proceed.")
    else:
        st.title("Download Your Resume")
        
        try:
            # Show loading animation
            with st.spinner("Creating your document..."):
                time.sleep(1)  # Simulate processing
                
                # Get HTML content
                token = str(st.session_state["render_token"]).strip()
                response = requests.get(f"https://resume.io/api/app/resumes/{token}")
                
                if response.status_code != 200:
                    st.error("Failed to fetch resume. Please check your token.")
                else:
                    data = response.json()
                    html_content = data.get("html", "")
                    
                    if not html_content:
                        st.error("No resume content found.")
                    else:
                        # Generate PDF
                        pdf_bytes = io.BytesIO()
                        pisa.CreatePDF(io.StringIO(html_content), dest=pdf_bytes)
                        pdf_bytes.seek(0)
                        
                        # Generate DOCX
                        doc = Document()
                        soup = BeautifulSoup(html_content, 'html.parser')
                        
                        for element in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p']):
                            if element.name.startswith('h'):
                                level = int(element.name[1])
                                doc.add_heading(element.get_text(), level=level)
                            else:
                                doc.add_paragraph(element.get_text())
                        
                        docx_bytes = io.BytesIO()
                        doc.save(docx_bytes)
                        docx_bytes.seek(0)
                        
                        # Download buttons
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.download_button(
                                label="📄 Download PDF",
                                data=pdf_bytes.getvalue(),
                                file_name=f"resume_{token}.pdf",
                                mime="application/pdf"
                            )
                        
                        with col2:
                            st.download_button(
                                label="📝 Download DOCX",
                                data=docx_bytes.getvalue(),
                                file_name=f"resume_{token}.docx",
                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                            )
                        
                        st.success("Resume generated successfully!")
                        
        except Exception as e:
            st.error(f"Error: {str(e)}")

# About Page
elif page == "About":
    st.title("About")
    st.info("This app allows you to download your resume from resume.io in both PDF and DOCX formats.")
