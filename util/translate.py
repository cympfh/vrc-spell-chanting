import json
import os


class Translate:
    """DeepL/ChatGPT を用いた翻訳器"""

    def __init__(self, model: str):
        self.model = model

    def run(self, query: str) -> dict | None:
        if self.model == "deepl":
            return self.run_deepl(query)
        else:
            return self.run_gpt(query)

    def run_deepl(self, query: str) -> dict:
        import requests

        key = os.getenv("DEEPL_AUTH_KEY")
        assert key is not None
        self.uri = "https://api.deepl.com/v2/translate"
        self.headers = {
            "Authorization": f"DeepL-Auth-Key {key}",
        }
        target_langs = {
            "en": "EN",
            "cn": "ZH",
            "kr": "KO",
        }
        result = {}
        for lang_alias, lang in target_langs.items():
            data = {
                "text": query,
                "target_lang": lang,
            }
            response = requests.post(self.uri, headers=self.headers, data=data)
            result[lang_alias] = (
                response.json()
                .get("translations", [{}])[0]
                .get("text", "[err]")
                .rstrip(".。,、")
            )
        return result

    def run_gpt(self, query: str) -> dict | None:
        import guidance

        chat = guidance.llms.OpenAI(self.model)
        program = guidance.Program(
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
        out: dict = program(query=query)  # type: ignore
        answer: str = out.get("answer")  # type: ignore
        try:
            return json.loads(answer)
        except Exception:
            return None
