# -----------------------------
# file: config.py
# -----------------------------
import os
import random
from dotenv import load_dotenv
from typing import List, Optional

# Load environment variables from .env (if present)
load_dotenv()


class Config:
    """Application configuration and API-key rotation utilities.

    - GEMINI_API_KEYS: comma- or semicolon-separated API keys in the environment
      Example: GEMINI_API_KEYS=key1,key2,key3
    - MOCK_MODE: if set to a truthy value ("1", "true", "True") then the
      client runs in mock mode and requests are not sent to Gemini.
    - MODEL_NAME: configurable model name (defaults to gemini-2.0-flash)
    """

    # Basic runtime flags
    MOCK_MODE: bool = os.getenv("MOCK_MODE", "False").lower() in ("1", "true", "yes")

    # Model name (kept configurable, defaults to gemini-2.0-flash-exp)
    MODEL_NAME: str = os.getenv("MODEL_NAME", "gemini-2.0-flash-exp")

    # Generation configuration
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.1"))
    MAX_OUTPUT_TOKENS: int = int(os.getenv("MAX_OUTPUT_TOKENS", "2048"))

    # Internal: parsed list of API keys
    _GEMINI_API_KEYS_RAW: str = os.getenv("GEMINI_API_KEYS", "")
    
    # GitHub token for private repository access
    GITHUB_TOKEN: Optional[str] = os.getenv("GITHUB_TOKEN", None)

    # Publicly usable sequence of keys (list[str])
    @classmethod
    def GEMINI_API_KEYS(cls) -> List[str]:
        """Return a list of non-empty API keys.

        Accepts comma- or semicolon-separated lists from the env var.
        Trims whitespace and ignores empty entries.
        """
        raw = cls._GEMINI_API_KEYS_RAW or ""
        if not raw:
            return []
        # support both comma and semicolon separated lists
        parts = [p.strip() for p in raw.replace(";", ",").split(",")]
        return [p for p in parts if p]

    @classmethod
    def validate(cls) -> None:
        """Validate configuration and raise on misconfiguration.

        If MOCK_MODE is enabled we allow missing keys. Otherwise at least one
        key must be present.
        """
        keys = cls.GEMINI_API_KEYS()
        if cls.MOCK_MODE:
            # allow running without keys
            return
        if not keys:
            raise ValueError(
                "No GEMINI_API_KEYS configured. Set GEMINI_API_KEYS env or enable MOCK_MODE."
            )

    @classmethod
    def rotate_gemini_key(cls) -> str:
        """Randomly pick an available Gemini API key.

        Raises ValueError if there are no keys configured.
        """
        keys = cls.GEMINI_API_KEYS()
        if not keys:
            raise ValueError("No API keys available for rotation")
        # random.choice is fine for simple rotation; if you prefer round-robin
        # implement a persistent index (e.g. Redis/DB/file) instead.
        return random.choice(keys)

    @classmethod
    def max_retries(cls) -> int:
        """Number of retries to attempt -- usually number of keys available."""
        k = len(cls.GEMINI_API_KEYS())
        return k if k > 0 else 1



