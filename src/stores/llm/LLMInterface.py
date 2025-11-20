from abc import ABC, abstractmethod

class LLMInterface(ABC):
    @abstractmethod
    def set_generation_model(self,model_id:str):
        """Set the generation model to be used by the LLM.

        Args:
            model_id (str): The identifier of the model to be set.
        """
        pass
    @abstractmethod
    def set_embedding_model(self,model_id:str,embedding_size:int):
        """Set the embedding model to be used by the LLM.

        Args:
            model_id (str): The identifier of the model to be set.
        """
        pass
    @abstractmethod
    def generate_text(self,prompt:str,chat_history:list=[],max_output_tokens:int=None,temperature:float=None):
        """Generate text based on the given prompt.

        Args:
            prompt (str): The input prompt for text generation.
            max_output_tokens (int): The maximum number of tokens to generate.
            temperature (float, optional): The sampling temperature. Defaults to None.
"""
        pass
    @abstractmethod
    def embed_text(self,text:str,document_type:str=None):
        """Generate embeddings for the given text.

        Args:
            text (str): The input text to be embedded.
            document_type (str): The type of document for embedding context.
        """
        pass
    @abstractmethod
    def construct_prompt(self,prompt:str,role:str):
        """Construct a prompt with a specific role.

        Args:
            prompt (str): The input prompt.
            role (str): The role to be assigned in the prompt.
        """
        pass