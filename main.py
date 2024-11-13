from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

app = FastAPI()

# Modelo para recibir la URL
class URLItem(BaseModel):
    url: str

# Endpoint de salud
@app.get("/health")
async def health_check():
    return {"status": "ok"}

# Endpoint para acortar URL
@app.post("/shorten")
async def shorten_url(item: URLItem):
    # Aquí iría la lógica para acortar la URL
    # Por ahora, simplemente devolvemos la misma URL
    return {"shortened_url": item.url}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9595)
