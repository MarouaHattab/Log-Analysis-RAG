from pydantic import BaseModel, Field, validator
from typing import Optional
from bson.objectid import ObjectId

class DataChunk(BaseModel):
    id: Optional[ObjectId] = Field(None, alias="_id")
    chunk_text: str = Field(..., min_length=1)
    chunk_metadata: dict
    chunk_order: int = Field(..., gt=0)
    chunk_project_id: ObjectId

    class Config:
        arbitrary_types_allowed = True #to allow ObjectId type for pydantic becuase pydantic does not know ObjectId type
     # we make indexes to optimize queries on chunk_project_id field
    @classmethod # to make it accessible without instantiating the class
    def get_indexes(cls):
        return [
            {
                "key":[
                    ("chunk_project_id", 1)
                ],
                "name": "chunk_project_id_index_1",
                "unique":   False
            }
        ]