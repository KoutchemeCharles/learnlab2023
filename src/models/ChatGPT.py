"""
 Wrapper class around openai Python API
to perform queries and experiments with ChatGPT models
"""

import os 
import openai 

class ChatGPT():

    def __init__(self, model) -> None:
        self.api_key=os.environ.get('OPEN_AI_KEY', None)
        self.model = model 
        assert model in ["gpt3", "gpt3.5-turbo", "gpt4"]

    def query(self, past_messages=[]):
        
        messages = past_messages
        if not messages: messages = list(self.config.messages)
        
        response = openai.ChatCompletion.create(
        model=self.model,
        messages=[
            {"role": "user", 
            "content": prompt
            }
        ]
        )
        gpt_code = response["choices"][0]['message']['content']