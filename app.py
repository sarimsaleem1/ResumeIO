import streamlit as st
from streamlit_navigation_bar import st_navbar
from streamlit_extras.row import row
from parser.DocumentEngine import ApplicationRunner
import time

# Page configuration
st.set_page_config(
    layout="wide", 
    page_icon="images/icon.png", 
    page_title="Resume IO Downloader"
)

# Session state initialization
def init_session_state():
    if "render_token" not in st.session_state:
        st.session_state["render_token"] = ""
    if "render_token_bool" not in st.session_state:
        st.session_state["render_token_bool"] = True
    if "selected" not in st.session_state:
        st.session_state["selected"] = "Home"

init_session_state()

# Navigation handler
def handle_click(page):
    st.session_state["selected"] = page

# Navigation configuration
pages = ["Home", "Download Resume", "About"]
style = {
    "nav": {
        "background-color": "#2c3e50", 
        "display": "flex",
        "justify-content": "left",
        "box-shadow": "0 2px 4px rgba(0, 0, 0, 0.1)"  
    },
    "div": {"max-width": "auto"},
    "span": {
        "border-radius": "0.5rem",
        "color": "#ecf0f1",
        "padding": "0.75rem 1rem", 
        "font-family": "Arial, sans-serif",
        "transition": "background-color 0.3s ease"
    },
    "active": {"background-color": "rgba(255, 255, 255, 0.2)"},
    "hover": {"background-color": "rgba(255, 255, 255, 0.1)"},
}
options = {
    "show_menu": False,
    "show_sidebar": False,
    "use_padding": False
}

# Navigation bar
page = st_navbar(pages, styles=style, options=options, key="selected")

# Home Page
if page == "Home":
    st.subheader("How to download your resume")
    st.write("""
        To fetch your resume from resume.io, you need to get your `rendering token` from 
        https://resume.io/api/app/resumes
    """)
    
    with st.expander(label="How to get renderToken", expanded=False):
        st.image("images/copytoken.jpg", width=500, caption="Copying rendering token")
    
    # Input layout
    rows = row([0.7, 0.3], gap="large", vertical_align="center")
    with rows.container():
        render_token = st.text_input(
            label="Enter copied renderToken here", 
            placeholder="Paste renderToken here...", 
            label_visibility="collapsed"
        )
        st.session_state["render_token"] = render_token
    
    with rows.container():
        if st.button(label="Submit"):
            if st.session_state["render_token"]:
                st.session_state["render_token_bool"] = False
                st.success("Token accepted! Proceed to download page.")
            else:
                st.error("renderToken required to proceed.")
                st.session_state["render_token_bool"] = True
    
    st.write("After copying render token. Proceed to download page.")
    st.button(
        "Go to Download Resume", 
        on_click=handle_click, 
        args=["Download Resume"], 
        disabled=st.session_state["render_token_bool"]
    )
    
    # Custom CSS
    st.markdown("""
    <style>
    .stApp { background-color: #f0f2f6; font-family: 'Arial', sans-serif; }
    .stTitle, .stHeader, .stSubheader { color: #4a90e2; }
    .stButton button {
      background-color: #4a90e2; color: white; border: none; padding: 10px 20px; text-align: center;
      text-decoration: none; display: inline-block; font-size: 16px; margin: 4px 2px; cursor: pointer;
      border-radius: 12px; transition-duration: 0.4s;
    }
    .stButton button:hover {
      background-color: white; color: #4a90e2; border: 2px solid #4a90e2;
    }
    .stTextInput input {
      background-color: #ffffff; color: #4a90e2; border: 2px solid #4a90e2;
      padding: 10px; font-size: 16px; border-radius: 12px; transition-duration: 0.4s;
    }
    .stTextInput input:focus {
      border-color: #4a90e2; box-shadow: 0 0 5px #4a90e2;
    }
    </style>
    """, unsafe_allow_html=True)

# Download Resume Page
elif page == "Download Resume":
    if st.session_state["render_token_bool"]:
        st.toast(":red[renderToken required to proceed.]", icon=":material/error:")
        st.error("renderToken required to proceed.")
    else:
        try:
            st.markdown("Let's do the magic for you...")
            
            # Create a placeholder for the loading animation
            loading_placeholder = st.empty()
            
            # Show loading animation
            with loading_placeholder.container():
                st.info("Creating your document...")
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Simulate progress
                for i in range(100):
                    time.sleep(0.02)
                    progress_bar.progress(i + 1)
                    if i < 33:
                        status_text.text("Fetching resume data...")
                    elif i < 66:
                        status_text.text("Converting to PDF...")
                    else:
                        status_text.text("Converting to DOCX...")
            
            # Clear the loading animation
            loading_placeholder.empty()
            
            # Process the document
            app_runner = ApplicationRunner()
            
            # Get HTML content
            html_content = app_runner.get_resume_html(
                token=str(st.session_state["render_token"]).strip()
            )
            
            if not html_content:
                st.error("Failed to fetch resume. Please check your token.")
            else:
                # Generate both formats
                pdf_bytes = app_runner.html_to_pdf(html_content)
                docx_bytes = app_runner.html_to_docx(html_content)
                
                if not pdf_bytes and not docx_bytes:
                    st.error("Document generation failed. Please try again.")
                else:
                    st.success("Resume generated successfully!")
                    
                    # Download buttons layout
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if pdf_bytes:
                            st.download_button(
                                label="📄 Download PDF",
                                file_name=f'resume_{st.session_state["render_token"]}.pdf',
                                data=pdf_bytes,
                                mime="application/pdf"
                            )
                    
                    with col2:
                        if docx_bytes:
                            st.download_button(
                                label="📝 Download DOCX",
                                file_name=f'resume_{st.session_state["render_token"]}.docx',
                                data=docx_bytes,
                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                            )
                    
                    st.toast("Documents ready for download!", icon="✅")
                    
        except Exception as e:
            st.error(f"Error: {str(e)}", icon="⚠️")
            st.toast("Generation failed. Check your token.", icon="❌")
    
    # Custom CSS
    st.markdown("""
    <style>
    .stApp { background-color: #f0f2f6; font-family: 'Arial', sans-serif; }
    .stTitle, .stHeader, .stSubheader { color: #4a90e2; }
    a {
        background-color: #4a90e2; color: white; border: none; padding: 10px 20px;
        text-align: center; text-decoration: none; display: inline-block; font-size: 16px;
        margin: 4px 2px; cursor: pointer; border-radius: 12px; transition-duration: 0.4s;
    }
    a:hover {
        background-color: white; color: #4a90e2; border: 2px solid #4a90e2;
    }
    </style>
    """, unsafe_allow_html=True)

# About Page
elif page == "About":
    st.info("Not yet implemented", icon=":material/warning:")
