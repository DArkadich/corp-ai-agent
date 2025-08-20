import os

OPENAI_API_BASE = os.getenv("OPENAI_API_BASE", "http://localhost:4000")
OPENAI_API_KEY  = os.getenv("OPENAI_API_KEY", "dummy_key")
MODEL           = os.getenv("MODEL", "llama3.1:8b")

TEI_URL         = os.getenv("TEI_URL", "http://localhost")
PG_DSN          = os.getenv("PG_DSN", "postgresql+psycopg2://raguser:pass@localhost:5432/ragdb")

_postgres_password = os.getenv("POSTGRES_PASSWORD")
if _postgres_password and "$(POSTGRES_PASSWORD)" in PG_DSN:
    PG_DSN = PG_DSN.replace("$(POSTGRES_PASSWORD)", _postgres_password)
