from fastapi import FastAPI

app = FastAPI(title="BloodDrive API")


@app.get("/health")
def health() -> dict[str, str]:
    """Report that the API is running. Used by tests and, later, the hosting provider."""
    return {"status": "ok"}
