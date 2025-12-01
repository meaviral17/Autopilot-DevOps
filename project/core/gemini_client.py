import os
import time
import json
from typing import Optional, Dict, Any, List

from google import genai
from google.genai import types

from project.core.observability import logger
from project.config import Config


class GeminiClient:
    """Robust Gemini client that rotates API keys and uses the new google-genai SDK."""

    def __init__(self, system_instruction: Optional[str] = None):
        self.system_instruction = system_instruction
        
        self.max_retries = Config.max_retries()

        self.retry_delay = float(os.getenv("GEMINI_RETRY_DELAY", "1.0"))

    def _build_contents(self, prompt: str) -> List[types.Content]:
        """Build the contents list. 
        NOTE: Do NOT add system instruction here. It goes in config.
        """
        return [
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=prompt)],
            )
        ]

    def generate_response(self, prompt: str, json_mode: bool = False, stream: bool = False) -> Optional[str]:
        """Generate a text response from Gemini."""
        
        # Validate configuration first
        try:
            Config.validate()
        except Exception as e:
            logger.log("GeminiClient", f"Config validation failed: {e}")
            return None

        for attempt in range(self.max_retries):
            try:
                # pick a key and create a client
                api_key = Config.rotate_gemini_key()
                logger.log("GeminiClient", f"Using configured API key (attempt {attempt + 1}/{self.max_retries})")

                client = genai.Client(api_key=api_key)

                # 1. Prepare Content (User prompt only)
                contents = self._build_contents(prompt)

                # 2. Prepare Config
                config_args: Dict[str, Any] = {
                    "temperature": getattr(Config, "TEMPERATURE", 0.1),
                    "top_p": float(os.getenv("TOP_P", "0.95")),
                    "max_output_tokens": getattr(Config, "MAX_OUTPUT_TOKENS", 2048),
                }

                # FIX: Add system_instruction to config, NOT contents
                if self.system_instruction:
                    config_args["system_instruction"] = self.system_instruction

                if json_mode:
                    config_args["response_mime_type"] = "application/json"

                generate_config = types.GenerateContentConfig(**config_args)

                # 3. Generate
                if stream:
                    result_parts: List[str] = []
                    for chunk in client.models.generate_content_stream(
                        model=Config.MODEL_NAME,
                        contents=contents,
                        config=generate_config,
                    ):
                        if getattr(chunk, "text", None):
                            result_parts.append(chunk.text)
                    full_text = "".join(result_parts).strip()
                else:
                    response = client.models.generate_content(
                        model=Config.MODEL_NAME,
                        contents=contents,
                        config=generate_config,
                    )
                    full_text = getattr(response, "text", None) or ""

                if not full_text:
                    raise ValueError("Empty response from Gemini")

                return full_text.strip()

            except Exception as e:
                logger.log("GeminiClient", f"API error (attempt {attempt + 1}): {type(e).__name__}: {e}")
                time.sleep(min(self.retry_delay * (2 ** attempt), 10))

        logger.log("GeminiClient", "All retries failed.")
        return None

    def generate_json(self, prompt: str) -> Optional[Dict[str, Any]]:
        """Request a JSON response and parse it into a Python dict."""
        response_text = self.generate_response(prompt, json_mode=True, stream=False)
        if not response_text:
            return None

        # Remove common fences or markdown codeblocks if present
        cleaned = response_text.replace("```json", "").replace("```", "").strip()
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            logger.log("GeminiClient", f"JSON parsing error: {e}. Response was: {cleaned}")
            return None