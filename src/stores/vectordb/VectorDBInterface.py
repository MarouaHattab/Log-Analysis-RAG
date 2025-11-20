from abc import ABC, abstractmethod
from typing import List
class VectorDBInterface(ABC):
    @abstractmethod
    def connect(self):
        """Connect to the vector database.

        Args:
            config (dict): Configuration parameters for the connection.
        """
        pass
    @abstractmethod
    def disconnect(self):
        """Disconnect from the vector database."""
        pass
    @abstractmethod
    def is_collection_exists(self,collection_name:str)->bool:
        """Check if a collection exists in the vector database.

        Args:
            collection_name (str): The name of the collection to check.
        Returns:
            bool: True if the collection exists, False otherwise.
        """
        pass
    @abstractmethod
    def list_all_collections(self)->List:
        """List all collections in the vector database.

        Returns:
            list: A list of collection names.
        """
        pass
    @abstractmethod
    def get_collection_info(self,collection_name:str)->dict:
        """Get information about a specific collection.

        Args:
            collection_name (str): The name of the collection.
        Returns:
            dict: Information about the collection.
        """
        pass
    @abstractmethod
    def delete_collection(self,collection_name:str):
        """Delete a specific collection from the vector database.

        Args:
            collection_name (str): The name of the collection to delete.
        """
        pass
    @abstractmethod
    def create_collection(self,collection_name:str,embedding_size:int,do_rest:bool=False):
        """Create a new collection in the vector database.
        Args:
            collection_name (str): The name of the collection to create.
            embedding_size (int): The size of the embeddings to be stored.
            do_rest (bool): Whether to reset the collection if it already exists.
        """
        pass
    @abstractmethod
    def insert_one(self,collection_name:str,text:str,vector:list,metadata:dict=None,record_id:str=None):
        """Insert a single record into a collection.
        Args:
            collection_name (str): The name of the collection.
            text (str): The text associated with the vector.
            vector (list): The embedding vector.
            metadata (dict, optional): Additional metadata for the record. Defaults to None.
            record_id (str, optional): The unique identifier for the record. Defaults to None.
        """
        pass
    def insert_many(self,collection_name:str,texts:list,vectors:list,metadata:list=None,record_ids:list=None,batch_size:int=50):
        """Insert multiple records into a collection.
        Args:
            collection_name (str): The name of the collection.
            texts (list): A list of texts associated with the vectors.
            vectors (list): A list of embedding vectors.
            metadata (list, optional): A list of metadata dictionaries for each record. Defaults to None.
            record_ids (list, optional): A list of unique identifiers for each record. Defaults to None.
            batch_size (int, optional): The number of records to insert in each batch. Defaults to 50.
        """
        pass
    @abstractmethod
    def search_by_vector(self,collection_name:str,vector:list,limit:int):
        """Search for similar records in a collection based on a vector.
        Args:
            collection_name (str): The name of the collection.
            vector (list): The embedding vector to search with.
            limit (int): The maximum number of results to return.
        """
        pass