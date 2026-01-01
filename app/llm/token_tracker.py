from transformers import AutoTokenizer
from typing import Optional


# Cache tokenizers by model name
_tokenizers: dict[str, AutoTokenizer] = {}


def get_tokenizer(model_name: str) -> AutoTokenizer:
    """Get or create tokenizer for model."""
    if model_name not in _tokenizers:
        try:
            _tokenizers[model_name] = AutoTokenizer.from_pretrained(model_name)
        except Exception:
            # Fallback to a common tokenizer
            _tokenizers[model_name] = AutoTokenizer.from_pretrained("gpt2")
    return _tokenizers[model_name]


def count_tokens(text: str, model_name: str) -> int:
    """Count tokens in text using model's tokenizer."""
    try:
        tokenizer = get_tokenizer(model_name)
        tokens = tokenizer.encode(text, add_special_tokens=True)
        return len(tokens)
    except Exception:
        # Fallback: rough estimate (1 token ≈ 4 characters)
        return len(text) // 4


def estimate_token_usage(query: str, response: str, model_name: str) -> dict:
    """
    Estimate token usage for query and response.
    Returns: {tokens_in, tokens_out, total_tokens}
    """
    tokens_in = count_tokens(query, model_name)
    tokens_out = count_tokens(response, model_name)
    total_tokens = tokens_in + tokens_out
    
    return {
        "tokens_in": tokens_in,
        "tokens_out": tokens_out,
        "total_tokens": total_tokens
    }

