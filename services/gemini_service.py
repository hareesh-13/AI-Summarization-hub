"""
services/gemini_service.py
Reusable Gemini LLM service built on LangChain + Google Generative AI.
"""

import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

load_dotenv()

DEFAULT_MODEL = "gemini-2.5-flash"


class GeminiService:
    """Singleton-style wrapper for the Gemini LLM via LangChain."""

    def __init__(self, model_name: str = DEFAULT_MODEL, temperature: float = 0.3):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise EnvironmentError(
                "GOOGLE_API_KEY is not set. "
                "Add it to your .env file or environment variables."
            )
        self.model_name = model_name
        self.temperature = temperature
        self.llm = ChatGoogleGenerativeAI(
            model=model_name,
            temperature=temperature,
            google_api_key=api_key,
        )

    def invoke(self, system_prompt: str, user_prompt: str) -> str:
        """Send a system + user message and return the text response with exponential backoff retry for rate limits."""
        import time
        import sys
        max_retries = 3
        base_delay = 5.0  # Reduced to avoid Streamlit event loop timeout

        for attempt in range(max_retries):
            try:
                messages = [
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=user_prompt),
                ]
                response = self.llm.invoke(messages)
                return response.content.strip()
            except Exception as exc:
                msg = str(exc).lower()
                is_rate_limit = any(term in msg for term in ["quota", "rate", "429", "resource_exhausted", "resource"])

                if is_rate_limit and attempt < max_retries - 1:
                    sleep_time = base_delay * (1.5 ** attempt)
                    plain_msg = f"[Rate Limit] Retrying in {sleep_time:.1f}s (Attempt {attempt + 1}/{max_retries})..."
                    toast_msg = f"Rate limit hit. Retrying in {sleep_time:.1f} seconds (Attempt {attempt + 1}/{max_retries})..."
                    # Safe toast — no emoji in icon to avoid Windows cp1252 crash
                    try:
                        import streamlit as st
                        st.toast(toast_msg, icon=None)
                    except Exception:
                        pass
                    # Safe print — write UTF-8 bytes directly to avoid cp1252 crash
                    try:
                        sys.stdout.buffer.write((plain_msg + "\n").encode("utf-8", errors="replace"))
                        sys.stdout.buffer.flush()
                    except Exception:
                        pass
                    
                    for _ in range(int(sleep_time)):
                        time.sleep(1)
                    time.sleep(sleep_time - int(sleep_time))
                    continue

                raise RuntimeError(self._friendly_error(exc)) from exc

    @staticmethod
    def _friendly_error(exc: Exception) -> str:
        msg = str(exc).lower()
        if "api_key" in msg or "api key" in msg:
            return "❌ Invalid or missing Gemini API key. Please check your .env file."
        if "quota" in msg or "rate" in msg:
            return "⚠️ Gemini API quota exceeded. Please wait a moment and try again."
        if "network" in msg or "connection" in msg:
            return "🌐 Network error. Please check your internet connection."
        return f"🤖 Gemini error: {exc}"
