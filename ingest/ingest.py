import os, glob
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, Integer, Text, JSON
from sqlalchemy.orm import declarative_base
import requests

PG_DSN = os.getenv("PG_DSN","postgresql+psycopg2://raguser:pass@pgvector:5432/ragdb")
TEI_URL = os.getenv("TEI_URL","http://tei")

Base = declarative_base()
class DocChunk(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True)
    doc_id = Column(Text, nullable=False)
    chunk_id = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(768))
    metadata = Column(JSON)

def embed(texts):
    r = requests.post(f"{TEI_URL}/embed", json={"inputs":texts}, timeout=60)
    r.raise_for_status()
    return r.json()["embeddings"]

def chunks(s, size=800, ov=100):
    i=0
    out=[]
    while i<len(s):
        out.append(s[i:i+size]); i+= size-ov
    return out

def main():
    engine = create_engine(PG_DSN, pool_pre_ping=True)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    s = Session()
    files = glob.glob("/data/**/*", recursive=True)
    batch_texts=[]
    meta=[]
    for fp in files:
        if not os.path.isfile(fp):
            continue
        if fp.lower().endswith(".pdf"):
            import fitz
            txt = "\n".join([p.get_text() for p in fitz.open(fp)])
        else:
            try:
                txt = open(fp,"r",encoding="utf-8").read()
            except Exception:
                continue
        cs = chunks(txt)
        for i,c in enumerate(cs):
            batch_texts.append(c); meta.append((os.path.basename(fp), i))
    if not batch_texts:
        print("No files found for ingestion")
        return
    embs = embed(batch_texts)
    for (doc,i),e,c in zip(meta, embs, batch_texts):
        s.add(DocChunk(doc_id=doc, chunk_id=i, content=c, embedding=e, metadata={}))
    s.commit()
    print(f"Ingested: {len(batch_texts)}")

if __name__=="__main__":
    main()
