from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn

app = FastAPI()

@app.get("/")
def root():
    return JSONResponse(content={"message": "Hello from Vercel Python Backend!"})

# hanya untuk local run
if __name__ == "__main__":
    uvicorn.run("index:app", host="0.0.0.0", port=8000, reload=True)
