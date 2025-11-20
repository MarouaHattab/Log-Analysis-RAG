from typing import List
from qdrant_client import QdrantClient,models
from VectorDBInterface import VectorDBInterface
from VectorDBEnums import DistanceMethodEnums
import logging
class QdrantDB(VectorDBInterface):
    def __init__(self,db_path:str,distance_method:str)->None:
        self.db_path = db_path
        self.distance_method = None
        self.client = None
        if distance_method==DistanceMethodEnums.COSINE.value:
            self.distance_method = models.Distance.COSINE
        elif distance_method==DistanceMethodEnums.DOT.value:
            self.distance_method = models.Distance.DOT
            
        self.logger = logging.getLogger(__name__)
    def connect(self):
        self.client = QdrantClient(path=self.db_path)
        
    def disconnect(self):
        self.client=None

    def is_collection_exists(self,collection_name:str)->bool:
        return self.client.collections.exists(collection_name=collection_name)
    
    def list_all_collections(self)->List:
        return self.client.get_collections()
    
    def get_collection_info(self,collection_name:str)->dict:
        return self.client.get_collection(collection_name=collection_name)
    
    def delete_collection(self,collection_name:str):
        if self.is_collection_exists(collection_name):
            self.client.delete_collection(collection_name=collection_name)