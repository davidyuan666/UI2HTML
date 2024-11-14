# -*- coding = utf-8 -*-
# @time:2024/8/15 15:59
# Author:david yuan
# @File:conversation_handler.py
# @Software:VeSync

import sys
import os
# Add the parent parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..','..')))

from vagents.vagentic.llms.simple_client import OpenAIChatBot
from vagents.vagentic.llms.openai_vision_client import VisionOpenAIClient
import os
import base64
import requests

class WebpageHandler:
    def __init__(self, system_msg=None):
        # Set a default system message with instructions
        self.system_message = """
            Generate the corresponding HTML and CSS code from the formatted JSON input.
        """

        # If a system message is provided, update the default message
        if system_msg is not None:
            self.system_message = system_msg

        # Initialize the chatbot with the specified system message
        self.chatbot = OpenAIChatBot(system=self.system_message)

        self.OPENAI_API_KEY =''
        self.MODEL ="gpt-4o-mini"
        self.openai_chat_url = "https://api.openai.com/v1/chat/completions"

        self.image_chatbot = VisionOpenAIClient(model=self.MODEL)

    def chat(self, message):
        """
        Processes the user's input message and generates a response using the OpenAIChatBot.

        Args:
            message (str): The user's input message.

        Returns:
            str: The response from the chatbot.
        """
        response = self.chatbot(message)
        return response

    def image_chat(self,user_input,image_path):
        # Function to encode the image
        def encode_image(image_path):
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')

        base64_image = encode_image(image_path)

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.OPENAI_API_KEY}"
        }

        payload = {
            "model": self.MODEL,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": user_input
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 300
        }
        '''

        {'id': 'chatcmpl-9ougZs9OGSAklat4Jf4reXHnsoHa1', 'object': 'chat.completion', 'created': 1721921327, 'model': 'gpt-4o-mini-2024-07-18', 'choices': [{'index': 0, 'message': {'role': 'assistant', 'content': 'The character in the image is Majin Buu, a fictional character from the anime and manga series "Dragon Ball" created by Akira Toriyama. Majin Buu is known for his various forms and abilities, including his capability to absorb other characters. He is one of the primary antagonists in the "Dragon Ball Z" series.'}, 'logprobs': None, 'finish_reason': 'stop'}], 'usage': {'prompt_tokens': 25520, 'completion_tokens': 70, 'total_tokens': 25590}, 'system_fingerprint': 'fp_611b667b19'}

        '''
        response = requests.post(self.openai_chat_url, headers=headers, json=payload)

        json_obj = response.json()
        reply = json_obj['choices'][0]['message']['content']
        return reply


    def image_local_chat(self,user_input,input_image_path):
        reply = self.image_chatbot.local_chat(user_input,input_image_path)
        return reply

    def interrupt(self, message):
        """
        Checks if the input message has the intent to interrupt the conversation using a language model.

        Args:
            message (str): The user's input message.

        Returns:
            bool: True if the message has the intent to interrupt, False otherwise.
        """
        # Define the prompt
        # Define the prompt
        prompt = f"The following message is from a user in a conversation: '{message}'. Is the intent of this message to interrupt the conversation? (yes/no)"

        # Generate the response from the model
        response = self.chatbot(prompt)

        # Check if the response indicates an interruption
        if "yes" in response.lower():
            return True
        else:
            return False



