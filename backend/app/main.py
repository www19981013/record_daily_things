from fastapi import FastAPI

app = FastAPI(title="精力恢复记事本")


@app.get("/health")
def health():
    return {"status": "ok"}
