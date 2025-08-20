import os
from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from typing import List
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response

from openai import OpenAI
from sqlalchemy.orm import scoped_session
from sqlalchemy import text
from .settings import OPENAI_API_BASE, OPENAI_API_KEY, MODEL, TEI_URL, PG_DSN
from .models import make_session, DocChunk
from .rag import embed_texts
from .tools import RAGTool
from .graph import build_graph

client = OpenAI(base_url=f"{OPENAI_API_BASE}/v1", api_key=OPENAI_API_KEY)

SessionFactory, engine = make_session(PG_DSN)
db = scoped_session(SessionFactory)

app = FastAPI(title="Corp AI Agent", version="1.0.0")

REQUESTS = Counter("agent_requests_total", "Total requests")
LATENCY  = Histogram("agent_latency_seconds", "Latency", buckets=(0.1, 0.3, 0.5, 1, 2, 5, 10))

rag_tool = RAGTool(TEI_URL, db())
graph = build_graph(client, MODEL, rag_tool)

class Ask(BaseModel):
    question: str

@app.get("/healthz")
def healthz():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.post("/ask")
def ask(body: Ask):
    REQUESTS.inc()
    with LATENCY.time():
        out = graph.invoke({"input": body.question})
    return out

@app.post("/ingest")
async def ingest(files: List[UploadFile] = File(...), chunk_size: int = 800, overlap: int = 100):
    from pathlib import Path
    import tempfile

    texts = []

    def split_text(t: str, size: int, ov: int):
        res = []
        i = 0
        while i < len(t):
            res.append(t[i:i + size])
            i += (size - ov)
        return res

    for f in files:
        suffix = Path(f.filename).suffix.lower()
        content = await f.read()
        if suffix == ".pdf":
            import fitz
            with tempfile.NamedTemporaryFile(delete=True, suffix=".pdf") as tmp:
                tmp.write(content)
                tmp.flush()
                doc = fitz.open(tmp.name)
                txt = "\n".join([p.get_text() for p in doc])
        else:
            txt = content.decode("utf-8", errors="ignore")
        doc_id = f.filename
        chunks = split_text(txt, chunk_size, overlap)
        texts.extend([(doc_id, i, c) for i, c in enumerate(chunks)])

    embeddings = embed_texts(TEI_URL, [c for _, _, c in texts])
    s = db()
    try:
        for (doc_id, i, c), emb in zip(texts, embeddings):
            s.add(DocChunk(doc_id=doc_id, chunk_id=i, content=c, embedding=emb, metadata={}))
        s.commit()
    finally:
        s.close()
    return {"ingested": len(texts)}
