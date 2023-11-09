#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author: Art9
# @File: chat_model.py
# @Desc: { Chat Model 基类 }
# @Date: 2023/11/03 21:58


class ChatModel:
    def __init__(self, model_name):
        self.model_name = model_name
        self.instance

    def chat_completion_sync(self, message_list, stream=True):
        if stream:
            pass

    # @overload
    def chat_completion_gen(self, message_list):
        """返回一个迭代器"""
        pass
