import streamlit as st
import time
from parser.DocumentEngine import ApplicationRunner

# Page configuration
st.set_page_config(
    layout="wide", 
    page_title="Resume IO Downloader"
)

# Session state initialization
def init_session_state():
    if "render_token" not in st.session_state:
        st.session_state["render_token"] = ""
    if "render_token_bool" not in st.session_state:
        st.session_state["render_token_bool"] = True
    if "current_page" not in st.session_state:
        st.session_state["current_page"] = "Home"

init_session_state()

# Navigation handler
def navigate_to(page):
    st.session_state["current_page"] = page

# Navigation
st.sidebar.title("Navigation")
if st.sidebar.button("Home", use_container_width=True):
    navigate_to("Home")
if st.sidebar.button("Download Resume", use_container_width=True):
    navigate_to("Download Resume")
if st.sidebar.button("About", use_container_width=True):
    navigate_to("About")

# Highlight current page in sidebar
if st.session_state["current_page"] == "Home":
    st.sidebar.markdown("**Home**")
elif st.session_state["current_page"] == "Download Resume":
    st.sidebar.markdown("**Download Resume**")
elif st.session_state["current_page"] == "About":
    st.sidebar.markdown("**About**")

# Home Page
if st.session_state["current_page"] == "Home":
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
            # Automatically navigate to download page after successful token submission
            navigate_to("Download Resume")
        else:
            st.error("renderToken required to proceed.")
            st.session_state["render_token_bool"] = True
    
    st.button(
        "Go to Download Resume", 
        disabled=st.session_state["render_token_bool"],
        on_click=lambda: navigate_to("Download Resume")
    )

# Download Resume Page
elif st.session_state["current_page"] == "Download Resume":
    if st.session_state["render_token_bool"]:
        st.error("renderToken required to proceed.")
        st.button("Back to Home", on_click=lambda: navigate_to("Home"))
    else:
        st.title("Download Your Resume")
        
        # Display the token for verification (you can remove this line if you want)
        st.write(f"Token: {st.session_state['render_token']}")
        
        try:
            # Show loading animation
            with st.spinner("Creating your document..."):
                time.sleep(1)  # Simulate processing
                
                # Create an instance of ApplicationRunner
                app_runner = ApplicationRunner()
                
                # Get HTML content
                token = str(st.session_state["render_token"]).strip()
                html_content = app_runner.get_resume_html(token)
                
                # Debug information (you can remove these lines if you want)
                if html_content is None:
                    st.error("Failed to fetch resume. Please check your token.")
                    st.button("Try Again", on_click=lambda: navigate_to("Home"))
                else:
                    # Generate PDF and DOCX
                    pdf_bytes = app_runner.html_to_pdf(html_content)
                    docx_bytes = app_runner.html_to_docx(html_content)
                    
                    if pdf_bytes is None and docx_bytes is None:
                        st.error("Failed to generate documents. Please try again.")
                        st.button("Try Again", on_click=lambda: navigate_to("Home"))
                    else:
                        # Download buttons
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            if pdf_bytes is not None:
                                st.download_button(
                                    label="📄 Download PDF",
                                    data=pdf_bytes,
                                    file_name=f"resume_{token}.pdf",
                                    mime="application/pdf"
                                )
                        
                        with col2:
                            if docx_bytes is not None:
                                st.download_button(
                                    label="📝 Download DOCX",
                                    data=docx_bytes,
                                    file_name=f"resume_{token}.docx",
                                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                                )
                        
                        st.success("Resume generated successfully!")
                        
                        # Add option to download another resume
                        st.button("Download Another Resume", on_click=lambda: navigate_to("Home"))
                        
        except Exception as e:
            st.error(f"Error: {str(e)}")
            st.button("Try Again", on_click=lambda: navigate_to("Home"))

# About Page
elif st.session_state["current_page"] == "About":
    st.title("About")
    st.info("This app allows you to download your resume from resume.io in both PDF and DOCX formats.")
    st.button("Back to Home", on_click=lambda: navigate_to("Home"))
