from .BaseDataModel import BaseDataModel
from .db_schemes import DataChunk
from .enums.DataBaseEnum import DataBaseEnum
from bson.objectid import ObjectId
from pymongo import InsertOne

class ChunkModel(BaseDataModel):

    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)
        self.collection = self.db_client[DataBaseEnum.COLLECTION_CHUNK_NAME.value]

    async def create_chunk(self, chunk: DataChunk):
        result = await self.collection.insert_one(chunk.dict(by_alias=True, exclude_unset=True))
        chunk._id = result.inserted_id
        return chunk

    async def get_chunk(self, chunk_id: str):
        result = await self.collection.find_one({
            "_id": ObjectId(chunk_id)
        })

        if result is None:
            return None
        
        return DataChunk(**result)
    
# My mentor suggested using a bulk write method instead of inserting each chunk individually.
# Inserting chunks one by one would create a high number of database operations and increase overhead.
# With bulk write, all chunks are written together in a single batch operation.
# This approach is much faster, more efficient, and reduces the load on the database,
# especially when dealing with a large number of chunks in RAG projects.




# Although insert_many() allows inserting multiple documents at once,
# it’s still not the most efficient option for large-scale RAG projects.
# insert_many() performs a simple bulk insert without handling complex or mixed operations (like updates or deletes).
# It can also consume more memory and cause performance issues when dealing with thousands of chunks.
# Bulk write provides better control, optimization, and scalability for managing large sets of chunk data efficiently.


    async def insert_many_chunks(self, chunks: list, batch_size: int=100):

        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i+batch_size]

            operations = [
                InsertOne(chunk.dict(by_alias=True, exclude_unset=True))
                for chunk in batch
            ]

            await self.collection.bulk_write(operations)
        
        return len(chunks)

    async def delete_chunks_by_project_id(self, project_id: ObjectId):
        result = await self.collection.delete_many({
            "chunk_project_id": project_id
        })

        return result.deleted_count