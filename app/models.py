from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, Integer, Text, JSON
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class DocChunk(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True)
    doc_id = Column(Text, nullable=False)
    chunk_id = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(768))
    metadata = Column(JSON)

def make_session(dsn: str):
    engine = create_engine(dsn, pool_pre_ping=True)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine), engine
