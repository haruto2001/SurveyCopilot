from openai import OpenAI
from pydantic import BaseModel

from modules.paper import Paper


class PaperList(BaseModel):
    papers: list[Paper]


class LLMInterface:
    def __init__(self, api_key: str, model_name: str = "gpt-4o"):
        self.client = OpenAI(api_key=api_key)
        self.model_name = model_name

    def generate(self, system_prompt: str, user_prompt: str) -> PaperList:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        response = self.client.beta.chat.completions.parse(
            messages=messages,
            model=self.model_name,
            response_format=PaperList,
        )
        return response.choices[0].message.parsed
