from __future__ import annotations

from typing import Callable, TypeVar, AsyncGenerator

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class LLMStreamingHandler:
    def __init__(self, chunk_size: int = 1024):
        self.chunk_size = chunk_size

    async def stream_response(
        self,
        llm_provider: Any,
        system_prompt: str,
        user_prompt: str,
        response_model: type[T],
    ) -> AsyncGenerator[str, None]:
        if hasattr(llm_provider, "stream_structured"):
            async for chunk in llm_provider.stream_structured(
                system_prompt, user_prompt, response_model
            ):
                yield chunk
        else:
            result = await llm_provider.generate_structured(
                system_prompt, user_prompt, response_model
            )
            yield result.model_dump_json()

    async def collect_stream(
        self,
        llm_provider: Any,
        system_prompt: str,
        user_prompt: str,
        response_model: type[T],
    ) -> T:
        chunks: list[str] = []
        async for chunk in self.stream_response(
            llm_provider, system_prompt, user_prompt, response_model
        ):
            chunks.append(chunk)

        full_response = "".join(chunks)
        return response_model.model_validate_json(full_response)

    @staticmethod
    def format_chunk(chunk: str, index: int) -> str:
        return f"[chunk {index}] {chunk}"