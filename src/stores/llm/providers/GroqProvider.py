from ..LLMInterface import LLMInterface
from groq import Groq
from logging import Logger
from ..LLMEnums import GroqEnums
from typing import List , Union

class GroqProvider(LLMInterface):
    def __init__(
        self,
        api_key: str,
        api_url: str=None,
        default_input_max_characters: int = 1000,
        default_output_max_tokens: int = 1000,
        default_temperature: float = 0.1
    ):
        self.api_key = api_key
        self.api_url = api_url or "https://api.groq.com"
        self.default_input_max_characters = default_input_max_characters
        self.default_output_max_tokens = default_output_max_tokens
        self.default_temperature = default_temperature

        # Model IDs
        self.generation_model_id = None
        self.embedding_model_id = None
        self.embedding_size = None

        # Groq Client
        self.client = Groq(api_key=self.api_key,
                           base_url= self.api_url if self.api_url and len(self.api_url) else None)
        self.enums = GroqEnums

        # Logger
        self.logger = Logger(__name__)

    # ==================== Generation ====================
    def set_generation_model(self, model_id: str):
        """Set the model used for text generation."""
        self.generation_model_id = model_id

    def generate_text(
        self,
        prompt: str,
        chat_history: list = None,
        max_output_tokens=None,
        temperature=None
    ):
        if not self.generation_model_id:
            raise ValueError("Groq model is not set! Call set_generation_model().")

        if chat_history is None:
            chat_history = []

        chat_history.append({
            "role": GroqEnums.USER.value,
            "content": self.process_text(prompt)
        })

        try:
            response = self.client.chat.completions.create(
                model=self.generation_model_id,
                messages=chat_history,
                max_tokens=max_output_tokens or self.default_output_max_tokens,
                temperature=temperature or self.default_temperature
            )
            return response.choices[0].message.content
        except Exception as e:
            self.logger.error(f"Groq API Error: {e}")
            raise e

    # ==================== Embeddings ====================
    def set_embedding_model(self, model_id: str, embedding_size: int):
        """Placeholder: Groq does not support embeddings."""
        self.embedding_model_id = model_id
        self.embedding_size = embedding_size
        self.logger.warning("Groq does NOT support embeddings. This is just a placeholder.")

    def embed_text(self, text: Union[str, List[str]], document_type: str = None):
        self.logger.error("Groq does NOT support embeddings.")

        if isinstance(text, str):
            text = [text]

        return None

        
    

    # ==================== Utilities ====================
    def process_text(self, text: str) -> str:
        """Limit and clean input text."""
        return text[:self.default_input_max_characters].strip()

    def construct_prompt(self, prompt: str, role: str):
        """Construct a chat message dict."""
        return {
            "role": role,  
            "content": prompt
        }