"""SQLAlchemy models for Memory Agent's database (separate from application DB)."""

from datetime import datetime
from typing import Any

from sqlalchemy import Column, DateTime, ForeignKey, Integer, JSON, String, Text, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class EpisodicMemory(Base):
    """Episodic memory: Past incidents, conversations, and outcomes."""

    __tablename__ = 'episodic_memory'

    incident_id = Column(String(255), primary_key=True)
    query_text = Column(Text, nullable=False)
    resolution = Column(Text, nullable=True)
    outcome = Column(String(100), nullable=True)  # 'resolved', 'escalated', 'pending'
    tags = Column(JSON, nullable=True)  # List of tags for categorization
    user_id = Column(String(255), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    metadata = Column(JSON, nullable=True)  # Additional context

    # Indexes
    __table_args__ = (
        Index('idx_episodic_user_id', 'user_id'),
        Index('idx_episodic_timestamp', 'timestamp'),
        Index('idx_episodic_outcome', 'outcome'),
    )

    def __repr__(self) -> str:
        return f'<EpisodicMemory(incident_id={self.incident_id}, outcome={self.outcome})>'


class WorkingMemory(Base):
    """Working memory: Task-level, short-lived context."""

    __tablename__ = 'working_memory'

    session_id = Column(String(255), primary_key=True)
    context_id = Column(String(255), nullable=False)
    task_data = Column(JSON, nullable=False)  # Current task context
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=True)  # TTL for automatic cleanup
    last_accessed = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Indexes
    __table_args__ = (
        Index('idx_working_context_id', 'context_id'),
        Index('idx_working_expires_at', 'expires_at'),
    )

    def __repr__(self) -> str:
        return f'<WorkingMemory(session_id={self.session_id}, context_id={self.context_id})>'


class SemanticMemory(Base):
    """Semantic memory: Links to knowledge base documents and their usage."""

    __tablename__ = 'semantic_memory'

    doc_id = Column(String(255), primary_key=True)
    content_hash = Column(String(64), nullable=False, unique=True)
    embedding_id = Column(String(255), nullable=True)  # Link to ChromaDB embedding
    category = Column(String(100), nullable=True)  # Document category
    last_accessed = Column(DateTime, default=datetime.utcnow, nullable=False)
    access_count = Column(Integer, default=0, nullable=False)
    relevance_score = Column(Integer, nullable=True)  # Average relevance score
    metadata = Column(JSON, nullable=True)

    # Indexes
    __table_args__ = (
        Index('idx_semantic_category', 'category'),
        Index('idx_semantic_last_accessed', 'last_accessed'),
        Index('idx_semantic_embedding_id', 'embedding_id'),
    )

    def __repr__(self) -> str:
        return f'<SemanticMemory(doc_id={self.doc_id}, category={self.category})>'
