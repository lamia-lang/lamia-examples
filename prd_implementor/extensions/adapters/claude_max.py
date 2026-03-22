"""
Adapter for anthropic-max-router local proxy.

Routes requests through anthropic-max-router
(https://github.com/nsxdavid/anthropic-max-router) — uses the native
Anthropic endpoint (/v1/messages) which passes requests directly to
api.anthropic.com, preserving full API feature support including
structured output via output_config.format.

Works with Claude Pro ($20/mo) and Max ($100/$200/mo) subscriptions
for flat-rate billing instead of pay-per-token.

The router stores its OAuth tokens in .oauth-tokens.json relative to the
working directory, so all commands below use ~ as a stable anchor.
"""

import logging
from typing import Optional, Type

import aiohttp
from pydantic import BaseModel

from lamia.adapters.llm.base import BaseLLMAdapter, LLMResponse, make_strict_schema
from lamia import LLMModel

logger = logging.getLogger(__name__)

DEFAULT_BASE_URL = "http://127.0.0.1:3000"


class ClaudeMaxAdapter(BaseLLMAdapter):
    """Adapter for anthropic-max-router using the native Anthropic endpoint."""

    @classmethod
    def name(cls) -> str:
        return "claude-max"

    @classmethod
    def env_var_names(cls) -> list[str]:
        return [] # No env variables like API key names needed

    @classmethod
    def is_remote(cls) -> bool:
        return False

    @property
    def supports_structured_output(self) -> bool:
        return True

    def __init__(self, base_url: str = DEFAULT_BASE_URL):
        self.base_url = base_url.rstrip("/")
        self.session: Optional[aiohttp.ClientSession] = None

    async def async_initialize(self) -> None:
        if self.session is None:
            self.session = aiohttp.ClientSession(
                headers={"Content-Type": "application/json"},
                timeout=aiohttp.ClientTimeout(total=600),
            )

    async def generate(
        self,
        prompt: str,
        model: LLMModel,
        response_model: Optional[Type[BaseModel]] = None,
    ) -> LLMResponse:
        if self.session is None:
            await self.async_initialize()
        assert self.session is not None

        model_name = model.get_model_name_without_provider() or "claude-sonnet-4"

        payload: dict = {
            "model": model_name,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": model.max_tokens or 64000,
            "temperature": model.temperature or 0.7,
        }

        if model.top_p is not None:
            payload["top_p"] = model.top_p

        if response_model is not None:
            payload["output_config"] = {
                "format": {
                    "type": "json_schema",
                    "schema": make_strict_schema(response_model),
                }
            }

        url = f"{self.base_url}/v1/messages"
        logger.debug("Requesting %s with model=%s", url, model_name)

        async with self.session.post(url, json=payload) as response:
            if response.status != 200:
                error_text = await response.text()
                raise RuntimeError(
                    f"claude-max-api error (status {response.status}): {error_text}"
                )

            data = await response.json()

        content = data.get("content", [])
        text = ""
        for block in content:
            if block.get("type") == "text":
                text = block["text"]
                break

        usage_data = data.get("usage", {})

        return LLMResponse(
            text=text,
            raw_response=data,
            usage={
                "input_tokens": usage_data.get("input_tokens", 0),
                "output_tokens": usage_data.get("output_tokens", 0),
                "total_tokens": (
                    usage_data.get("input_tokens", 0)
                    + usage_data.get("output_tokens", 0)
                ),
            },
            model=model_name,
        )

    async def close(self) -> None:
        if self.session:
            await self.session.close()
            self.session = None
