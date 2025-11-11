from enum import Enum
class LLMModel(Enum):
    OPENAI="OPENAI"
    GEMINI="GEMINI"
    ANTHROPIC="ANTHROPIC"
class OpenAIEnum(Enum):
    SYSTEM="system"
    USER="user"
    ASSISTANT="assistant"