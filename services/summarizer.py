"""
services/summarizer.py
Advanced summarization pipeline: stuff / map-reduce / refine strategies.
"""

from langchain_text_splitters import RecursiveCharacterTextSplitter
from services.gemini_service import GeminiService

CHUNK_SIZE = 10000        # Larger chunks for modern LLMs
CHUNK_OVERLAP = 1000
STUFF_THRESHOLD = 120000   # Use 'stuff' for under ~30,000 words (single fast request)
MAPREDUCE_THRESHOLD = 480000 # Map-reduce for medium-long documents

def safe_sleep(seconds: float):
    import time
    for _ in range(int(seconds)):
        time.sleep(1)
    time.sleep(seconds - int(seconds))



def get_splitter() -> RecursiveCharacterTextSplitter:
    return RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )


def _pick_strategy(text: str) -> str:
    length = len(text)
    if length <= STUFF_THRESHOLD:
        return "stuff"
    if length <= MAPREDUCE_THRESHOLD:
        return "map_reduce"
    return "refine"


class Summarizer:
    """
    High-level summarizer that automatically picks the right chain strategy
    based on document length, or accepts a user override.
    """

    def __init__(self, gemini: GeminiService):
        self.gemini = gemini

    # ------------------------------------------------------------------ #
    #  Public entry-point                                                   #
    # ------------------------------------------------------------------ #

    def summarize(
        self,
        text: str,
        system_prompt: str,
        summary_length: str = "Medium",
        summary_style: str = "Professional",
        extra_instructions: str = "",
        strategy: str = "auto",
    ) -> dict:
        """
        Returns a dict with keys: strategy, summary, chunks_used.
        """
        if not strategy or strategy == "auto":
            strategy = _pick_strategy(text)
            
        length_guide = {
            "Short": "2-3 concise paragraphs",
            "Medium": "4-6 paragraphs",
            "Detailed": "comprehensive multi-section analysis",
        }.get(summary_length, "4-6 paragraphs")

        style_guide = {
            "Professional": "Use clear, professional language suitable for a business audience.",
            "Academic": "Use formal academic language with structured arguments.",
            "Business": "Focus on actionable insights, ROI, and business impact.",
            "Beginner Friendly": "Use simple, jargon-free language. Explain technical terms.",
        }.get(summary_style, "")

        enhanced_system = (
            f"{system_prompt}\n\n"
            f"Length: {length_guide}.\n"
            f"Style: {style_guide}\n"
            f"{extra_instructions}"
        )

        if strategy == "stuff":
            summary = self._stuff(text, enhanced_system)
        elif strategy == "map_reduce":
            summary = self._map_reduce(text, enhanced_system)
        else:
            summary = self._refine(text, enhanced_system)

        chunks = get_splitter().split_text(text)
        return {
            "strategy": strategy,
            "summary": summary,
            "chunks_used": len(chunks),
        }

    # ------------------------------------------------------------------ #
    #  Private chain implementations                                        #
    # ------------------------------------------------------------------ #

    def _stuff(self, text: str, system_prompt: str) -> str:
        """Send full text in a single call."""
        return self.gemini.invoke(system_prompt, f"Text to summarize:\n\n{text}")

    def _map_reduce(self, text: str, system_prompt: str) -> str:
        """Summarize each chunk individually, then combine, respecting the 5 RPM rate limit."""
        import time
        import sys
        splitter = get_splitter()
        chunks = splitter.split_text(text)

        map_prompt = (
            "You are a summarization assistant. "
            "Summarize the following text chunk concisely, preserving key information."
        )
        partial_summaries = []
        for i, chunk in enumerate(chunks):
            if i > 0:
                throttle_msg = f"[Rate Limiter] Cooling down for 12s between chunks (Chunk {i+1}/{len(chunks)})..."
                try:
                    import streamlit as st
                    st.toast(throttle_msg, icon=None)
                except Exception:
                    pass
                sys.stdout.buffer.write((throttle_msg + "\n").encode("utf-8", errors="replace"))
                sys.stdout.buffer.flush()
                safe_sleep(12.0)
            partial = self.gemini.invoke(map_prompt, f"Chunk:\n\n{chunk}")
            partial_summaries.append(partial)

        # Cool down before the final combine request
        if len(chunks) > 0:
            throttle_msg = "[Rate Limiter] Cooling down for 12s before generating final summary..."
            try:
                import streamlit as st
                st.toast(throttle_msg, icon=None)
            except Exception:
                pass
            sys.stdout.buffer.write((throttle_msg + "\n").encode("utf-8", errors="replace"))
            sys.stdout.buffer.flush()
            safe_sleep(12.0)

        combined = "\n\n".join(partial_summaries)
        reduce_prompt = system_prompt
        return self.gemini.invoke(
            reduce_prompt,
            f"Combine and refine these partial summaries into a cohesive final summary:\n\n{combined}",
        )

    def _refine(self, text: str, system_prompt: str) -> str:
        """Iteratively refine the summary chunk by chunk, respecting the 5 RPM rate limit."""
        import time
        import sys
        splitter = get_splitter()
        chunks = splitter.split_text(text)

        running_summary = self.gemini.invoke(
            system_prompt,
            f"Summarize this opening section:\n\n{chunks[0]}",
        )

        for i, chunk in enumerate(chunks[1:], start=1):
            throttle_msg = f"[Rate Limiter] Cooling down for 12s before refining (Chunk {i+1}/{len(chunks)})..."
            try:
                import streamlit as st
                st.toast(throttle_msg, icon=None)
            except Exception:
                pass
            sys.stdout.buffer.write((throttle_msg + "\n").encode("utf-8", errors="replace"))
            sys.stdout.buffer.flush()
            safe_sleep(12.0)

            running_summary = self.gemini.invoke(
                system_prompt,
                (
                    f"Existing summary:\n{running_summary}\n\n"
                    f"Refine and expand it using this new section:\n\n{chunk}"
                ),
            )

        return running_summary
