import json

import guidance


class Translate:
    """ChatGPT を用いた翻訳器"""

    def __init__(self, model="gpt-4"):
        chat = guidance.llms.OpenAI(model)
        self.program = guidance.Program(
            """
{{#system~}}
You are a helpful and terse Machine Translation to 日本語, English, Chinese and Korean.

User Input: (こんにちは、私の名前は枚方です)

Your Output (JSON): {"ja": "こんにちは、私の名前は枚方です", "en": "Hello, my name is Hirakata." "cn": "你好，我的名字是枚方", "kr": "안녕하세요, 제 이름은 히라카타입니다"}

User Input: (Hi, my name is Hirakata)

Your Output (JSON): {"ja": "こんにちは、私の名前は枚方です", "en": "Hello, my name is Hirakata." "cn": "你好，我的名字是枚方", "kr": "안녕하세요, 제 이름은 히라카타입니다"}
{{~/system}}

{{#user~}}
次の文を日本語、英語、中国後、韓国語のすべてに翻訳してください.

User Input: ({{query}})

Your Output (JSON):
{{~/user}}

{{#assistant~}}
{{gen 'answer' temperature=0 max_tokens=500}}
{{~/assistant}}
""",
            llm=chat,
        )

    def run(self, query: str) -> dict | None:
        out = self.program(query=query)
        answer = out.get("answer")
        try:
            return json.loads(answer)
        except Exception:
            return None
