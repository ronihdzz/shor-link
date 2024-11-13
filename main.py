from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
from session import session
from session import URLShort
import uuid
from fastapi.responses import RedirectResponse

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
    # Generar un hash aleatorio único para la URL
    url_hash = str(uuid.uuid4())[:8]
    shortened_url = f"localhost:9595/info/{url_hash}"
    
    # Crear un nuevo registro de URLShort
    new_url = URLShort(original_url=item.url, name=url_hash)
    
    # Insertar el registro en la base de datos
    session.add(new_url)
    session.commit()
    
    return {"shortened_url": shortened_url}

# Nuevo endpoint para redirigir a la URL original
@app.get("/info/{url_hash}")
async def redirect_to_url(url_hash: str):
    # Buscar el registro en la base de datos
    url_record = session.query(URLShort).filter_by(name=url_hash).first()
    
    # Si no se encuentra el registro, lanzar una excepción
    if not url_record:
        raise HTTPException(status_code=404, detail="URL no encontrada")
    
    # Redirigir a la URL original
    return RedirectResponse(url=url_record.original_url)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9595)
