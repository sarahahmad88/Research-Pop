import os
from dataclasses import dataclass, field

# Disable optional CrewAI telemetry before importing CrewAI.
os.environ.setdefault("CREWAI_TELEMETRY_DISABLED", "true")
os.environ.setdefault("OTEL_SDK_DISABLED", "true")


@dataclass(frozen=True)
class Settings:
    groq_key: str = field(repr=False)
    groq_model: str = "openai/gpt-oss-120b"
    search_model: str = "openai/gpt-oss-120b"


def make_llm(settings):
    from crewai import LLM

    class GroqCompatibleLLM(LLM):
        """Remove CrewAI's internal cache marker before provider serialization."""

        def _format_messages_for_provider(self, messages):
            cleaned = [
                {key: value for key, value in message.items()
                 if key != "cache_breakpoint"}
                for message in messages
            ]
            return super()._format_messages_for_provider(cleaned)

    return GroqCompatibleLLM(model=f"groq/{settings.groq_model}", api_key=settings.groq_key,
               is_litellm=True,
               temperature=0.2, max_tokens=4096, timeout=60)
