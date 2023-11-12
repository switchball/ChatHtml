import re
from io import StringIO
from typing import List
import time
import streamlit as st
import streamlit.components.v1 as stc
import asyncio

from st_click_detector import click_detector as did_click

from chat_models.spark_model import SparkClient
from juicy import clickable_select
from utils import chat_completion

SYSTEM_PROMPT = (
    "You are an expert at writing html code. You write css style in <style> tag in <head>. You always write html code in ``` blocks."
)


def render_html(html_file):
    st.markdown(
        "<style>iframe {border: 2px dashed #ccc;}</style>", unsafe_allow_html=True
    )
    st.write("页面预览")
    if isinstance(html_file, StringIO):
        stc.html(html_file.read(), height=750, scrolling=1)
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


def show_conversation():
    """展示对话的内容"""
    if "messages" in st.session_state:
        for message in st.session_state["messages"]:
            st.chat_message(message["role"]).write(message["content"])


async def chat_completion_async(message_list):
    client = SparkClient(
        app_id=st.secrets["Spark"]["APP_ID"],
        api_secret=st.secrets["Spark"]["API_SECRET"],
        api_key=st.secrets["Spark"]["API_KEY"],
    )
    answer = await client.chat_completion_async(message_list)
    return answer


def show_instruction_guide():
    st.markdown("将你的需求转为所见即所得的网页")


def is_first_landing():
    return "messages" not in st.session_state or len(st.session_state["messages"]) <= 1


def show_welcome_starter():
    st.markdown("尝试以下几个例子")

    create_init_button("创建一个网页，用于展示公司的产品和服务。页面中需要包含一个导航栏、一个产品列表和一个联系方式区域。")

    create_init_button("设计一个博客页面，要求包括文章列表、文章详情页和侧边栏。文章列表需要支持分页功能，文章详情页需要有评论功能。")

    create_init_button("编写一个登录页面，要求包括用户名和密码输入框以及登录按钮。用户输入正确的用户名和密码后，跳转到主页面。")

    # 创建一个网页，用于展示公司的产品和服务。页面中需要包含一个导航栏、一个产品列表和一个联系方式区域。

    # 设计一个博客页面，要求包括文章列表、文章详情页和侧边栏。文章列表需要支持分页功能，文章详情页需要有评论功能。

    # 编写一个登录页面，要求包括用户名和密码输入框以及登录按钮。用户输入正确的用户名和密码后，跳转到主页面。


def create_init_button(text):
    """创建用于直接作为用户输入的 button"""
    if st.button(label=text, type="secondary"):
        st.session_state["messages"] = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": text},
        ]
        st.success(text)


if __name__ == "__main__":
    st.set_page_config(
        page_title="Chat Html", layout="wide", page_icon=":speech_balloon:"
    )
    st.title("Chat Html")
    show_instruction_guide()
    show_welcome_starter()

    # x = clickable_select(["星火V3", "星火V2", "gpt3-16k"])
    # st.write(f"you select {x}")

    with st.sidebar:
        x = did_click(
            '<a href="#" id="reset">Reset</a> / <a href="#" id="foo">Reset</a>', None
        )
        st.write(f"clicked={x}")
    if x:
        st.info("已重置")
        del st.session_state["messages"]

    # with st.empty():
    #     for seconds in range(3):
    #         st.write(f"⏳ {seconds} seconds have passed")
    #         time.sleep(1)
    #     st.write("✔️ 1 minute over!")

    uploaded_file = st.sidebar.file_uploader(
        "Upload your html file here...", type=["html"]
    )

    if "messages" not in st.session_state or len(st.session_state["messages"]) <= 1:
        if uploaded_file is None:
            st.session_state["messages"] = [
                {"role": "system", "content": SYSTEM_PROMPT}
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
        st.session_state.messages.append({"role": "user", "content": demands})
        st.info(demands)

    should_show_conv = clickable_select(["隐藏对话", "显示对话"], key="show_conv", sidebar=True)
    st.sidebar.write(should_show_conv)
    if should_show_conv == "显示对话":
        show_conversation()
    if st.session_state.messages[-1]["role"] == "assistant":
        answer = st.session_state.messages[-1]["content"]
        code_block = extract_code(answer)
        if len(code_block) >= 1:
            render_html(StringIO(code_block[0]))
            render_copy_html_button(code_block[0])

    if st.session_state.messages[-1]["role"] == "user":
        tic = time.time()
        answer = asyncio.run(
            chat_completion_async(message_list=st.session_state.messages)
        )

        st.write(f"used {time.time() - tic}")

        # response = chat_completion(
        #     message_list=st.session_state.messages,
        #     model="gpt-3.5-turbo-16k",
        #     max_tokens=2048,
        #     stream=True,
        # )
        # answer = response["choices"][0]["message"]["content"]
        if "messages" in st.session_state:
            st.session_state.messages.append({"role": "assistant", "content": answer})
        else:
            st.warning("no messages!")
        st.write(f"fin {time.time()}")
        st.chat_message("assistant").write(answer)

        code_block = extract_code(answer)
        if len(code_block) >= 1:
            render_html(StringIO(code_block[0]))
            render_copy_html_button(code_block[0])

    # multi_page_inner_logic()
