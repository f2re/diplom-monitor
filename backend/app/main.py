from fastapi import FastAPI

app = FastAPI(title="Weeks Until Diploma API")

@app.get("/")
async def root():
    return {"message": "Welcome to Weeks Until Diploma API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
