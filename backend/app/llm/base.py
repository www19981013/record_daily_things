from typing import Protocol


class BaseLLM(Protocol):
    def generate(self, prompt: str) -> str: ...
