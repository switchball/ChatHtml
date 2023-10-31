import streamlit as st
import streamlit.components.v1 as stc
from io import StringIO

def render_html(html_file):
    st.markdown("<style>iframe {border: 2px dashed #ccc;}</style>", unsafe_allow_html=True)
    st.write("页面预览")
    if isinstance(html_file, StringIO):
        stc.html(html_file.read())
    else:
        with open(html_file, "r", encoding='utf-8') as f:
            stc.html(f.read())

def render_copy_html_button(html_content):
    if st.button("展示 html 并复制", help="在下方代码框右上角点击 Copy to clipboard"):
        st.code(html_content, language="html")

st.set_page_config(page_title="Chat Html", layout="wide", page_icon=":speech_balloon:")
st.title("Chat Html")



uploaded_file = st.file_uploader("Upload your html file here...", type=['html'])

if uploaded_file is not None:
    html_content = uploaded_file.getvalue().decode('utf-8')
    render_html(StringIO(html_content))
    render_copy_html_button(html_content)
