from typing import Optional
import asyncio
import logging
import traceback
from concurrent.futures import ThreadPoolExecutor

from huggingface_hub import InferenceClient
from app.config import settings

logger = logging.getLogger(__name__)


# ---------------------------
# Singleton instances
# ---------------------------

_client: Optional[InferenceClient] = None
_executor: Optional[ThreadPoolExecutor] = None


def get_client() -> InferenceClient:
    """Create or return a singleton Hugging Face InferenceClient."""
    global _client
    if _client is None:
        _client = InferenceClient(
            api_key=settings.huggingface_api_key
        )
    return _client


def get_executor() -> ThreadPoolExecutor:
    """Create or return a singleton ThreadPoolExecutor."""
    global _executor
    if _executor is None:
        _executor = ThreadPoolExecutor(max_workers=1)
    return _executor


# ---------------------------
# Sync inference call
# ---------------------------

def _call_inference_sync(
    client: InferenceClient,
    model_name: str,
    query: str
) -> str:
    """
    Synchronous streaming inference call.
    Handles StopIteration properly to avoid asyncio issues.
    """
    logger.info(f"[HF_CLIENT] Starting inference - model: {model_name}, query length: {len(query)}")
    
    try:
        logger.debug("[HF_CLIENT] Creating stream...")
        try:
            stream = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": query}],
                stream=True,
                max_tokens=512,
                temperature=0.7,
            )
            logger.debug(f"[HF_CLIENT] Stream created successfully. Type: {type(stream)}")
        except StopIteration as stream_e:
            # StopIteration during stream creation usually means model/provider not found
            logger.error(f"[HF_CLIENT] StopIteration during stream creation - model may not be available")
            logger.error(f"[HF_CLIENT] Model: {model_name}")
            logger.error(f"[HF_CLIENT] This usually means the model doesn't have a provider configured")
            raise RuntimeError(
                f"Model '{model_name}' is not available or doesn't have a provider configured. "
                f"Please check if the model exists and supports chat completions via Hugging Face Inference API."
            ) from stream_e

        response_parts = []
        chunk_count = 0

        # Iterate through stream - StopIteration is normal when stream ends
        try:
            logger.debug("[HF_CLIENT] Starting stream iteration...")
            for chunk in stream:
                chunk_count += 1
                logger.debug(f"[HF_CLIENT] Chunk {chunk_count} received. Type: {type(chunk)}")
                
                if not chunk.choices:
                    logger.debug(f"[HF_CLIENT] Chunk {chunk_count} has no choices, skipping")
                    continue

                delta = chunk.choices[0].delta
                logger.debug(f"[HF_CLIENT] Chunk {chunk_count} delta type: {type(delta)}")
                
                if delta and delta.content:
                    content_preview = delta.content[:50] + "..." if len(delta.content) > 50 else delta.content
                    logger.debug(f"[HF_CLIENT] Chunk {chunk_count} content: {content_preview}")
                    response_parts.append(delta.content)
                else:
                    logger.debug(f"[HF_CLIENT] Chunk {chunk_count} has no content in delta")
                    
            logger.info(f"[HF_CLIENT] Stream iteration completed normally. Total chunks: {chunk_count}")
            
        except StopIteration as e:
            # StopIteration is expected when stream ends naturally
            logger.warning(f"[HF_CLIENT] StopIteration caught in inner handler (expected). Chunks processed: {chunk_count}")
            logger.warning(f"[HF_CLIENT] StopIteration details: {e}")
            logger.warning(f"[HF_CLIENT] StopIteration traceback:\n{''.join(traceback.format_tb(e.__traceback__))}")
            pass
        except Exception as inner_e:
            logger.error(f"[HF_CLIENT] Exception in stream iteration: {type(inner_e).__name__}: {inner_e}")
            logger.error(f"[HF_CLIENT] Inner exception traceback:\n{''.join(traceback.format_tb(inner_e.__traceback__))}")
            raise

        response_text = "".join(response_parts).strip()
        logger.debug(f"[HF_CLIENT] Response text assembled. Length: {len(response_text)}")

        if not response_text:
            logger.error("[HF_CLIENT] Empty response from Hugging Face API")
            raise RuntimeError("Empty response from Hugging Face API")

        logger.info(f"[HF_CLIENT] Inference completed successfully. Response length: {len(response_text)}")
        return response_text

    except StopIteration as e:
        # Convert StopIteration to RuntimeError to avoid asyncio issues
        # This catches any StopIteration that leaks through
        logger.error(f"[HF_CLIENT] StopIteration caught in OUTER handler (UNEXPECTED)")
        logger.error(f"[HF_CLIENT] StopIteration value: {e}")
        logger.error(f"[HF_CLIENT] StopIteration type: {type(e)}")
        logger.error(f"[HF_CLIENT] StopIteration args: {e.args if hasattr(e, 'args') else 'N/A'}")
        logger.error(f"[HF_CLIENT] Full StopIteration traceback:\n{''.join(traceback.format_tb(e.__traceback__))}")
        logger.error(f"[HF_CLIENT] StopIteration context: model={model_name}, query_length={len(query)}")
        raise RuntimeError(
            f"StopIteration in stream (unexpected): {e}"
        ) from e
    except Exception as e:
        logger.error(f"[HF_CLIENT] Exception in _call_inference_sync: {type(e).__name__}: {e}")
        logger.error(f"[HF_CLIENT] Exception traceback:\n{''.join(traceback.format_tb(e.__traceback__))}")
        raise RuntimeError(
            f"Hugging Face API error ({type(e).__name__}): {e}"
        ) from e


# ---------------------------
# Async wrapper
# ---------------------------

async def call_huggingface_api(
    model_name: str,
    query: str
) -> str:
    """
    Async wrapper around the synchronous inference call.
    Safe for asyncio and FastAPI.
    """
    logger.info(f"[HF_CLIENT] Async call initiated - model: {model_name}")
    
    try:
        loop = asyncio.get_running_loop()
        client = get_client()
        executor = get_executor()
        
        logger.debug(f"[HF_CLIENT] Executor type: {type(executor)}")
        logger.debug(f"[HF_CLIENT] Submitting to executor...")

        result = await loop.run_in_executor(
            executor,
            _call_inference_sync,
            client,
            model_name,
            query,
        )
        
        logger.info(f"[HF_CLIENT] Async call completed successfully")
        return result
        
    except Exception as e:
        logger.error(f"[HF_CLIENT] Exception in async wrapper: {type(e).__name__}: {e}")
        logger.error(f"[HF_CLIENT] Async exception traceback:\n{''.join(traceback.format_tb(e.__traceback__))}")
        raise
