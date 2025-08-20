from typing import Dict, Any
from sqlalchemy.orm import Session
from .rag import embed_texts, search_similar

class RAGTool:
    def __init__(self, tei_url: str, session: Session):
        self.tei_url = tei_url
        self.session = session

    def run(self, query: str, k: int = 5) -> Dict[str, Any]:
        q_emb = embed_texts(self.tei_url, [query])[0]
        hits = search_similar(self.session, q_emb, k=k)
        context = "\n\n".join(f"[{h['doc_id']}#{h['chunk_id']}] {h['content']}" for h in hits)
        return {"context": context, "chunks": hits}
