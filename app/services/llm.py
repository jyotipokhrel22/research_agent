# app/services/llm.py
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from openai import OpenAI


class LLMClient:
    def __init__(self, api_key: str, model: str):
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1"
        )
        self.model = model

    def generate(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You extract structured research data. Always return valid JSON."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0,
        )

        content = response.choices[0].message.content
        return self._clean(content)

    def _clean(self, text: str) -> str:
        """
        Removes markdown wrappers like ```json ... ```
        """
        if not text:
            return ""

        return (
            text.replace("```json", "")
                .replace("```", "")
                .strip()
        )