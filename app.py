import re
from io import StringIO

import streamlit as st
import streamlit.components.v1 as stc
from st_click_detector import click_detector as did_click

from utils import chat_completion


def render_html(html_file):
    st.markdown(
        "<style>iframe {border: 2px dashed #ccc;}</style>", unsafe_allow_html=True
    )
    st.write("页面预览")
    if isinstance(html_file, StringIO):
        stc.html(html_file.read(), height=500)
    else:
        with open(html_file, "r", encoding="utf-8") as f:
            stc.html(f.read())


def render_copy_html_button(html_content):
    if st.button("展示 html 并复制", help="在下方代码框右上角点击 Copy to clipboard"):
        st.code(html_content, language="html")


def extract_code(text):
    pattern = r"```(.*?)```"
    code_blocks = re.findall(pattern, text, re.DOTALL)
    return code_blocks


def show_welcome_page():
    st.write("欢迎来到 Chat Html")
    st.write("请查看左侧的示例")
    st.write("或者点击Upload上传自己的文件")
    st.write("或者键入自己的需求")
    st.write(":speech_balloon: 注意，由于浏览器安全限制，请使用 Chrome 浏览器")


def multi_page_inner_logic():
    multi_pages = []

    # register
    multi_pages.append(("欢迎", show_welcome_page))

    # render

    # render multi pages
    current_page = 0
    # call render function
    st.header(multi_pages[current_page][0])
    multi_pages[current_page][1]()


if __name__ == "__main__":
    st.set_page_config(
        page_title="Chat Html", layout="wide", page_icon=":speech_balloon:"
    )
    st.title("Chat Html")

    x = did_click(
        '<a href="#" id="reset">Reset</a> / <a href="#" id="foo">Waha</a>', None
    )
    st.write(f"clicked={x}")
    if x:
        st.info("已重置")
        del st.session_state["messages"]

    uploaded_file = st.sidebar.file_uploader(
        "Upload your html file here...", type=["html"]
    )

    if "messages" not in st.session_state or len(st.session_state["messages"]) <= 1:
        if uploaded_file is None:
            st.session_state["messages"] = [
                {
                    "role": "system",
                    "content": "You are an expert at writing html code. You always write html code in ``` blocks.",
                }
            ]
        else:
            html_content = uploaded_file.getvalue().decode("utf-8")
            render_html(StringIO(html_content))
            render_copy_html_button(html_content)
            st.session_state["messages"] = [
                {
                    "role": "system",
                    "content": "You are an expert at writing html code. You always write html code in ``` blocks.",
                },
                {
                    "role": "user",
                    "content": "Write a html code with my demands following...",
                },
                {
                    "role": "assistant",
                    "content": f"Here is your code:\n\n```\n{html_content}\n```",
                },
            ]

    with st.sidebar.expander("messages"):
        if "messages" in st.session_state:
            st.json(st.session_state["messages"])
        else:
            st.warning("No messages yet")

    demands = st.chat_input()
    if demands is not None:
        st.info(demands)

        st.session_state.messages.append({"role": "user", "content": demands})
        st.chat_message("user").write(demands)

        response = chat_completion(
            message_list=st.session_state.messages,
            model="gpt-3.5-turbo-16k",
            stream=True,
        )
        answer = response["choices"][0]["message"]["content"]
        st.session_state.messages.append({"role": "assistant", "content": answer})
        st.chat_message("assistant").write(answer)

        code_block = extract_code(answer)
        if len(code_block) >= 1:
            render_html(StringIO(code_block[0]))

    # multi_page_inner_logic()
