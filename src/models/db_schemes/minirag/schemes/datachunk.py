from .minirag_base import SQLAlchemyBase
from sqlalchemy import Column, Index, Integer, DateTime,func,String,ForeignKey 
from sqlalchemy.dialects.postgresql import UUID,JSONB
from sqlalchemy.orm import relationship
from pydantic import BaseModel
import uuid
class DataChunk(SQLAlchemyBase):
    __tablename__ = "data_chunks"
    data_chunk_id=Column(Integer, primary_key=True, autoincrement=True)
    data_chunk_uuid=Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    chunk_text=Column(String,nullable=False)
    chunk_metadata=Column(JSONB,nullable=True)
    chunk_order=Column(Integer,nullable=False)

    chunk_project_id=Column(Integer,ForeignKey("projects.project_id"),nullable=False)
    chunk_asset_id=Column(Integer,ForeignKey("assets.asset_id"),nullable=False)
    created_at=Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    uploaded_at=Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    project=relationship("Project",backref="chunks")
    asset=relationship("Asset",backref="chunks")

    __table_args__ = (
        Index('ix_chunk_project_id', chunk_project_id),
        Index('ix_chunk_asset_id', chunk_asset_id),
    )
class RetrievedDocument(BaseModel):
    text: str
    score: float