import httpx
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Dict

def embed_texts(tei_url: str, texts: List[str]) -> List[List[float]]:
    # TEI: POST /embed
    payload = {"inputs": texts}
    with httpx.Client(timeout=30.0) as client:
        r = client.post(f"{tei_url}/embed", json=payload)
        r.raise_for_status()
        return r.json()["embeddings"]

def search_similar(session: Session, query_emb: List[float], k: int = 5) -> List[Dict]:
    sql = text("""
      SELECT doc_id, chunk_id, content, metadata
      FROM documents
      ORDER BY embedding <=> :q
      LIMIT :k
    """)
    rows = session.execute(sql, {"q": query_emb, "k": k}).fetchall()
    return [dict(r._mapping) for r in rows]
