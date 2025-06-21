from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(
    title="Receipt OCR Processing System",
    version="1.0.0",
    description="A FastAPI application for processing receipt PDFs using OCR"
)

# Include the API routes
app.include_router(router, tags=["receipts"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000) 