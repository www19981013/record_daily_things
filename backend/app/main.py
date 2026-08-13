from fastapi import FastAPI

from .db import Base, engine
from .routers import entries, summaries

Base.metadata.create_all(bind=engine)

app = FastAPI(title="精力恢复记事本")
app.include_router(entries.router)
app.include_router(summaries.router)


@app.get("/health")
def health():
    return {"status": "ok"}
