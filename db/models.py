from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import relationship

from db.base import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String, nullable=False)

    # fragments = relationship("Fragment", back_populates="document")


class Fragment(Base):
    __tablename__ = "fragments"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    text = Column(String, nullable=False)
    # embedding = Column(Vector(1536), nullable=False) # HW: Damian

    # document = relationship("Document", back_populates="fragments")
