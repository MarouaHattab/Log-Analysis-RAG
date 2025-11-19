from enum import Enum
class LLMModel(Enum):
    OPENAI="OPENAI"
    GEMINI="GEMINI"
    ANTHROPIC="ANTHROPIC"
class OpenAIEnum(Enum):
    SYSTEM="system"
    USER="user"
    ASSISTANT="assistant"
class CoHereEnums(Enum):
    SYSTEM="SYSTEM"
    USER="USER"
    ASSISTANT="CHATBOT"
    DOCUMENT="search_document"
    QUERY="search_query"
    
class DocumentTypeEnum(Enum):
   DOCUMENT="DOCUMENT"
   QUERY="QUERY"