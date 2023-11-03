import random

import openai
import streamlit as st
from transformers import GPT2Tokenizer

openai.api_key = st.secrets["OPENAI_API_KEY"]
openai.api_type = "open_ai"


HINT_TEXTS = [
    "正在接通电源，请稍等 ...",
    "正在思考怎么回答，不要着急",
    "正在努力查询字典内容 ...",
    "等待对方回复中 ...",
    "正在激活神经网络 ...",
    "请稍等",
]


@st.cache_resource(ttl=86400)
def get_tokenizer():
    """Loads the GPT-2 tokenizer from the model's tokenizer file."""
    tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
    return tokenizer


@st.cache_data(ttl=3600)
def chat_completion(
    message_list,
    model="gpt-3.5-turbo-16k",
    temperature=0.4,
    max_tokens=256,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0.6,
    stream=False,
):
    """Chat completion"""
    with st.spinner(text=random.choice(HINT_TEXTS)):
        response = openai.ChatCompletion.create(
            model=model,
            messages=message_list,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            stream=stream,
        )
    if stream:
        reply_msg = ""
        finish_reason = ""

        # streaming chat with editable slot
        reply_edit_slot = st.empty()
        for chunk in response:
            c = chunk["choices"][0]
            delta = c.get("delta", {}).get("content", "")
            finish_reason = c.get("finish_reason", "")
            reply_msg += delta
            reply_edit_slot.markdown(reply_msg)
        reply_edit_slot.markdown("")

        # calculate message tokens
        txt = "".join(m["content"] for m in message_list)
        input_tokens = len(get_tokenizer().tokenize(txt))
        completion_tokens = len(get_tokenizer().tokenize(reply_msg))

        # mock response
        response = {
            "choices": [
                {
                    "message": {"content": reply_msg, "role": "assistant"},
                    "finish_reason": finish_reason,
                }
            ],
            "usage": {"total_tokens": input_tokens + completion_tokens},
        }
        return response
    else:
        return response
