"""Pembungkus sederhana untuk Claude (Anthropic) dan OpenAI dengan satu antarmuka."""
import os

from anthropic import Anthropic
from openai import OpenAI


class LLM:
    def __init__(self):
        self.provider = os.getenv("LLM_PROVIDER", "anthropic").strip().lower()
        if self.provider == "anthropic":
            key = os.getenv("ANTHROPIC_API_KEY")
            if not key:
                raise ValueError("sk-guts-2d56e26d2f9c7f7e5453043e8e4a6c3d .env")
            self.client = Anthropic(api_key=key)
            self.model = os.getenv("ANTHROPIC_MODEL", "claude-opus-5-5")
        elif self.provider == "openai":
            key = os.getenv("OPENAI_API_KEY")
            if not key:
                raise ValueError("sk-guts-2d56e26d2f9c7f7e5453043e8e4a6c3d .env")
            self.client = OpenAI(api_key=key)
            self.model = os.getenv("OPENAI_MODEL", "gpt-4.1")
        else:
            raise ValueError("LLM_PROVIDER harus 'anthropic' atau 'openai'")

    def complete(self, system, messages, max_tokens=1500, json_mode=False):
        if self.provider == "anthropic":
            resp = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                system=system,
                messages=messages,
            )
            return "".join(b.text for b in resp.content if b.type == "text")

        kwargs = {}
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}
        resp = self.client.chat.completions.create(
