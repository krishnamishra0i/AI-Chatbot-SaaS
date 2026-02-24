"""Groq LLM integration (lightweight wrapper)

This module provides a small, robust GroqLLM wrapper used by the app.
The original file contained a large duplicated example section which caused
syntax errors; this trimmed version keeps the public API the rest of the
project expects while removing noisy example code.
"""

from typing import Optional, List, Dict, AsyncGenerator
import os
import httpx
import json
from backend.utils.logger import setup_logger
from backend.llm.prompt import (
    ENHANCED_SYSTEM_PROMPT,
    ENHANCED_STREAMING_PROMPT,
    QUESTION_ANSWERING_PROMPT,
    PROBLEM_SOLVING_PROMPT,
    CREATIVE_ASSISTANCE_PROMPT,
)

logger = setup_logger(__name__)


class GroqLLM:
    """Minimal Groq LLM client shim used by the app.

    This implementation keeps the same method signatures used elsewhere but
    focuses on robustness for local development: it degrades gracefully when
    no GROQ_API_KEY is present.
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "llama-3.1-8b-instant"):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.model = model
        self.base_url = "https://api.groq.com/openai/v1"
        self.timeout = 60.0  # OPTIMIZED: Increased from 30 to 60 seconds for better reliability
        self.max_retries = 3
        self.retry_delay = 1.0
        self.conversation_history: List[Dict] = []
        self.default_system_prompt = ENHANCED_SYSTEM_PROMPT
        self.request_count = 0
        self.error_count = 0

        if not self.api_key:
            logger.warning("Groq API key not found; Groq calls will be skipped.")
        else:
            logger.info(f"Groq LLM initialized with timeout={self.timeout}s")

    def set_conversation_history(self, history: List[Dict]):
        self.conversation_history = history

    def get_smart_system_prompt(self, user_message: str) -> str:
        m = user_message.lower()
        if any(k in m for k in ["what", "how", "why", "when", "where", "who", "?"]):
            return QUESTION_ANSWERING_PROMPT
        if any(k in m for k in ["help", "problem", "error", "fix", "issue"]):
            return PROBLEM_SOLVING_PROMPT
        if any(k in m for k in ["create", "write", "generate", "design"]):
            return CREATIVE_ASSISTANCE_PROMPT
        return self.default_system_prompt

    async def generate_async(
        self,
        prompt: str,
        max_tokens: int = 1024,
        temperature: float = 0.7,
        system_prompt: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:
        if not self.api_key:
            yield "❌ Groq API key not configured"
            return

        if system_prompt is None:
            system_prompt = ENHANCED_STREAMING_PROMPT

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.extend(self.conversation_history[-5:])
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": True,
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                async with client.stream("POST", f"{self.base_url}/chat/completions", json=payload, headers={"Authorization": f"Bearer {self.api_key}"}) as r:
                    if r.status_code != 200:
                        text = await r.aread()
                        logger.error(f"Groq API error: {r.status_code} - {text}")
                        yield f"❌ Groq API error: {r.status_code}"
                        return
                    async for line in r.aiter_lines():
                        if line.startswith("data: "):
                            s = line[6:].strip()
                            if s == "[DONE]":
                                break
                            try:
                                d = json.loads(s)
                                chunk = d.get("choices", [{}])[0].get("delta", {}).get("content", "")
                                if chunk:
                                    yield chunk
                            except Exception:
                                continue
        except Exception as e:
            logger.exception("Groq streaming error")
            yield f"❌ Error: {e}"

    def generate(self, prompt: str, max_tokens: int = 1024, temperature: float = 0.7, system_prompt: Optional[str] = None, use_smart_prompting: bool = True) -> str:
        if not self.api_key:
            return "Groq API key not configured"

        if system_prompt is None and use_smart_prompting:
            system_prompt = self.get_smart_system_prompt(prompt)
        elif system_prompt is None:
            system_prompt = self.default_system_prompt

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.extend(self.conversation_history[-6:])
        messages.append({"role": "user", "content": prompt})

        payload = {"model": self.model, "messages": messages, "max_tokens": max_tokens, "temperature": temperature}

        # Retry loop with exponential backoff
        for attempt in range(1, self.max_retries + 1):
            try:
                logger.info(f"Groq request (attempt {attempt}/{self.max_retries}): {prompt[:50]}...")
                r = httpx.post(
                    f"{self.base_url}/chat/completions",
                    json=payload,
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    timeout=self.timeout
                )
                
                # Success
                if r.status_code == 200:
                    self.request_count += 1
                    data = r.json()
                    text = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                    logger.info(f"Groq API success: {len(text)} chars returned")
                    self.conversation_history.append({"role": "user", "content": prompt})
                    self.conversation_history.append({"role": "assistant", "content": text})
                    return text
                
                # Authentication error - don't retry
                elif r.status_code == 401:
                    self.error_count += 1
                    error_msg = "Groq API Authentication Failed: Your API key is invalid or expired"
                    logger.error(error_msg)
                    raise Exception(error_msg)
                
                # Rate limit - retry with backoff
                elif r.status_code == 429:
                    self.error_count += 1
                    if attempt < self.max_retries:
                        wait_time = self.retry_delay * (2 ** (attempt - 1))
                        logger.warning(f"Groq Rate Limited (429), retry {attempt+1}/{self.max_retries} in {wait_time}s...")
                        import time
                        time.sleep(wait_time)
                        continue
                    else:
                        error_msg = "Groq API Rate Limit Exceeded: Too many requests, please try again later"
                        logger.error(error_msg)
                        raise Exception(error_msg)
                
                # Server errors - retry
                elif r.status_code >= 500:
                    self.error_count += 1
                    if attempt < self.max_retries:
                        logger.warning(f"Groq Server Error ({r.status_code}), retrying...")
                        import time
                        time.sleep(self.retry_delay)
                        continue
                    else:
                        error_msg = f"Groq API Server Error ({r.status_code}): API temporarily unavailable"
                        logger.error(error_msg)
                        raise Exception(error_msg)
                
                # Other HTTP errors
                else:
                    self.error_count += 1
                    error_msg = f"Groq API HTTP Error {r.status_code}: {r.text[:200]}"
                    logger.error(error_msg)
                    raise Exception(error_msg)
            
            except httpx.TimeoutException:
                self.error_count += 1
                if attempt < self.max_retries:
                    logger.warning(f"Groq Request Timeout, retry {attempt+1}/{self.max_retries}...")
                    import time
                    time.sleep(self.retry_delay)
                    continue
                else:
                    error_msg = "Groq API Timeout: Request took too long, please try again"
                    logger.error(error_msg)
                    raise Exception(error_msg)
            
            except httpx.ConnectError as e:
                self.error_count += 1
                if attempt < self.max_retries:
                    logger.warning(f"Groq Connection Error, retry {attempt+1}/{self.max_retries}...")
                    import time
                    time.sleep(self.retry_delay)
                    continue
                else:
                    error_msg = f"Groq API Connection Failed: Cannot reach API - {str(e)}"
                    logger.error(error_msg)
                    raise Exception(error_msg)
            
            except Exception as e:
                logger.exception(f"Groq request failed (attempt {attempt}): {str(e)}")
                if attempt >= self.max_retries:
                    raise

    def generate_enhanced(self, prompt: str, context_type: str = "general", max_tokens: int = 1024, temperature: float = 0.7) -> str:
        prompt_map = {
            "question": QUESTION_ANSWERING_PROMPT,
            "problem": PROBLEM_SOLVING_PROMPT,
            "creative": CREATIVE_ASSISTANCE_PROMPT,
            "general": self.default_system_prompt,
        }
        selected = prompt_map.get(context_type, self.default_system_prompt)
        return self.generate(prompt, max_tokens=max_tokens, temperature=temperature, system_prompt=selected, use_smart_prompting=False)

    def get_models(self) -> List[str]:
        return ["llama-3.1-8b-instant", "llama-3.1-70b-versatile", "llama-2-70b-chat", "gemma-7b-it"]

    def reset_history(self):
        self.conversation_history = []

    def set_default_system_prompt(self, prompt: str):
        self.default_system_prompt = prompt


if __name__ == "__main__":
    g = GroqLLM(api_key=os.getenv("GROQ_API_KEY"))
    print("GroqLLM module loaded (trimmed).")
    # Dry-run: when no API key is configured, the client returns a friendly message.
    try:
        out = g.generate("Hello from GroqLLM (dry-run)", max_tokens=32)
        print("Dry run output:", out)
    except Exception as e:
        print("Local test failed:", e)
