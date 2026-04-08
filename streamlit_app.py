import streamlit as st
import base64
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from pdf_processor import process_pdf
import requests

BASE_DIR = Path(__file__).resolve().parent
header_img_path = BASE_DIR / "static" / "SIDBI_LOGO.png"
# LLM_API_URL = "http://172.30.1.200/dan-financial-analysis-agent/financial-analysis" #latest
LLM_API_URL = "http://172.30.1.200:7000/financial-analysis" # v1
MAX_WORKERS = 6

# ================== CONFIG ==================
st.set_page_config(page_title="Financial Document Analyzer", layout="wide")
img_tag = ""
try:
    if header_img_path.exists():
        with open(header_img_path, "rb") as f:
            img_b64 = base64.b64encode(f.read()).decode("utf-8")
        img_tag = f"<img src='data:image/png;base64,{img_b64}' alt='logo' style='height:64px; max-width:250px; object-fit:contain; display:block;'/>"
except:
    img_tag = ""
# # For main header in page


if "analysis_ready" not in st.session_state:
    st.session_state["analysis_ready"] = False

html = f"""
<style>
.st-emotion-cache-zy6yx3 {{
    padding: 10px;

}}

.header-wrap {{

    display: flex;
    justify-content: left;
    align-items: center;
    column-gap: 15%;
    box-shadow: 1px 2px 5px #bdbcbc;
    
}}

.header-container {{
    box-shadow: 1px 2px 5px #bdbcbc;
}}

.stAppHeader{{
display: none !important;
}}
</style>
<div class ="">
<div class="header-wrap">
  <div class="header-logo">
    {img_tag}
    
  </div>
  <div class="">
  <h2 style='text-align: center; color: black; padding: 1px 0 0 0'>Financial Document Analyzer</h2>
   <p style='margin-bottom:0;text-align:center;color:gray'>
            Upload financial documents and then let AI analyze them.
     </p>
      </div>
   </div>
</div>


"""
st.markdown(html, unsafe_allow_html=True)

# def process_file(uploaded_file):
#     with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
#         tmp.write(uploaded_file.read())
#         path = tmp.name

#     text = process_pdf(path)

#     return {
#         "filename":uploaded_file.name,
#         "text":text
#     }

left, right = st.columns([1, 2])


# st.markdown("""
# <style>
# .uploader-label {
#     font-size: 24px;      /* ← adjust this */
#     font-weight: 600;     /* semi-bold */
#     margin-bottom: 6px;
# }
# </style>
# <div class="uploader-label">Upload Balance Sheet / P&amp;L PDFs</div>
# """, unsafe_allow_html=True)

# --- The uploader with its label hidden ---

with left:
    st.subheader("Upload Financial Documents")
    uploaded_files = st.file_uploader(
        label="Upload Balance Sheet / P&L PDFs",
        type=["pdf"],
        accept_multiple_files=True,
        label_visibility="collapsed"   # hides default label
    )
    if uploaded_files:
        st.session_state["raw_docs"] = [
            {
                "name": f.name,
                "bytes": f.getvalue()
            }
            for f in uploaded_files
        ]
        st.success(f"{len(uploaded_files)} files uploaded")
        

    # if uploaded_files:
    #     st.session_state["files"] = uploaded_files
    if st.button("Process Documents"):

        if "raw_docs" not in st.session_state:
            st.error("Upload files first")
        else:
            results = []
            progress = st.progress(0)

            for i, file in enumerate(st.session_state["raw_docs"]):

                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    tmp.write(file["bytes"])
                    path = tmp.name

                text = process_pdf(path)

                results.append({
                    "filename": file["name"],
                    "text": text
                })
                progress.progress((i + 1) / len(st.session_state["raw_docs"]))
            st.success("All PDFs processed")
            # ✅ Combine text
            combined_text = ""

            for r in results:
                combined_text += f"\n\n===== {r['filename']} ====\n\n"
                combined_text += r["text"] or ""

            st.session_state["document_text"] = combined_text
            st.session_state["ready_for_llm"] = True
            st.session_state["llm_called"] = False   # reset flag
    if st.session_state.get("ready_for_llm") and st.session_state.get("document_text"):

        if not st.session_state.get("llm_called"):

            # st.write("Calling LLM API...")

            with st.spinner("Running Analysis........"):

                data = {
                    "financial_text": st.session_state["document_text"]
                }
                try:
                    # st.write("Calling LLM API: ",LLM_API_URL)
                    resp = requests.post(
                    LLM_API_URL,
                    data=data,
                    timeout=6000,
                    proxies= {"http":None, "https":None}
                )
                    # st.write("STATUS: ",resp.status_code)
                    if resp.status_code == 200:
                        st.session_state["html_output"] = resp.text
                        st.session_state["analysis_ready"] = True
                        st.session_state["llm_called"] = True
                except Exception as e:
                    st.write(f"API CALL FAIL: {e}")        
                # resp = requests.post(
                #     LLM_API_URL,
                #     data=data,
                #     timeout=6000
                # )
                # st.write(resp.status_code)
                # if resp.status_code == 200:
                #     st.session_state["html_output"] = resp.text
                #     st.session_state["analysis_ready"] = True
                #     st.session_state["llm_called"] = True
                # else:
                #     st.error("LLM API request failed!") 
                #     resp.raise_for_status()      

    #             # OLD app
    #             # for r in results:
    #             #     combined_text += f"\n\n===== {r['filename']} ====\n\n"
    #             #     combined_text += r["text"] or ""

    #             # st.session_state["combined_text"] = combined_text

with right:
#     if combined_text:
#         st.text_area(
#                 "Output",
#                 st.session_state["combined_text"],
#                 height=500
#             ) 
    if st.session_state.get("analysis_ready") and "html_output" in st.session_state:
        st.subheader("AI Analysis")
        # left, center, right = st.columns([2, 2, 1])
        # with center:
            # st.subheader("AI Analysis")
            # Centered subheader
            # st.markdown(
            #     "<h3 style='text-align:center;margin-top:0;'>AI Analysis</h3>",
            #     unsafe_allow_html=True
            # )

        # st.subheader("AI Analysis")
        # if "combined_text" in st.session_state:
        #     st.text_area(
        #         "Preview",
        #         st.session_state["combined_text"][:5000],
        #         height=550
        #     ) 
        if "html_output" in st.session_state:
            # st.markdown(
            #     st.session_state["html_output"],
            #     unsafe_allow_html=True
            # )

            st.components.v1.html(
                    st.session_state["html_output"], height=500, scrolling=True)  # type: ignore
            st.markdown(
                """
                <style>
                iframe{
                border: 1px solid #85929E !important;
                border-radius: 6px !important;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            
                }
                div[data-testId="stVerticalBlock"]{
                margin-top: 15px !important;
                }
                </style>
                """,
                unsafe_allow_html=True
            )    


st.markdown("""
<style>
/* 1️⃣ Hide original button text by making font-size 0 */ 
div[data-testid="stFileUploader"] button[kind="secondary"]{
    font-size: 0 !important;
}
 
/* 2️⃣ Add custom text via ::after */ 
div[data-testid="stFileUploader"] button[kind="secondary"]::after {
    content: "Upload File";
    font-size: 16px !important;
    display: inline-block !important;
}
</style>
""", unsafe_allow_html=True)