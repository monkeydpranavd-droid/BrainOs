from fastapi import FastAPI

app = FastAPI(
    title="BrainOS API",
    version="1.0.0"
)

@app.get("/")
def root():
    return {
        "message": "🚀 BrainOS Backend Running!"
    }