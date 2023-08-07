import os
from typing import Iterator

import requests


class Translate:
    """DeepL を用いた翻訳器"""

    def __init__(self, langs: list[str]):
        key = os.getenv("DEEPL_AUTH_KEY")
        assert key is not None
        self.uri = "https://api.deepl.com/v2/translate"
        self.headers = {
            "Authorization": f"DeepL-Auth-Key {key}",
        }
        self.langs = langs

    def run(self, query: str) -> Iterator[str]:
        """翻訳する

        Parameters
        ----------
        query
            翻訳する文章
        """
        for lang in self.langs:
            data = {
                "text": query,
                "target_lang": lang,
            }
            response = requests.post(self.uri, headers=self.headers, data=data)
            result = (
                response.json()
                .get("translations", [{}])[0]
                .get("text", "[err]")
                .rstrip(".。,、")
            )
            yield result
