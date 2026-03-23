"""
Streaming LLM client: yields response chunks as they arrive from Hugging Face.
Used by the /api/query/stream endpoint.
"""
from typing import AsyncGenerator
import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor

from huggingface_hub import InferenceClient
from app.config import settings

logger = logging.getLogger(__name__)

_streaming_executor = ThreadPoolExecutor(max_workers=4)


def _stream_sync(model_name: str, query: str):
    """Synchronous generator that yields text chunks from HF streaming API."""
    client = InferenceClient(api_key=settings.huggingface_api_key)
    stream = client.chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content": query}],
        stream=True,
        max_tokens=512,
        temperature=0.7,
    )
    for chunk in stream:
        if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content


async def stream_huggingface_api(model_name: str, query: str) -> AsyncGenerator[str, None]:
    """
    Async generator that yields SSE-formatted text chunks.
    Format: 'data: <token>\\n\\n'
    """
    loop = asyncio.get_running_loop()
    queue: asyncio.Queue = asyncio.Queue()

    def _producer():
        try:
            for token in _stream_sync(model_name, query):
                loop.call_soon_threadsafe(queue.put_nowait, token)
        except Exception as e:
            logger.error(f"[STREAMING] Error: {e}")
        finally:
            loop.call_soon_threadsafe(queue.put_nowait, None)  # sentinel

    loop.run_in_executor(_streaming_executor, _producer)

    while True:
        token = await queue.get()
        if token is None:
            break
        yield f"data: {token}\n\n"
