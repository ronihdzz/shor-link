from fastapi import APIRouter, Depends
from schemas import URLItem
from models import URLShort
from utils import get_db
import uuid
from sqlalchemy.orm import Session

router = APIRouter()

# Endpoint para acortar URL
@router.post("/shorten")
async def shorten_url(item: URLItem, db: Session = Depends(get_db)):
    # Generar un hash aleatorio único para la URL
    url_hash = str(uuid.uuid4())[:8]
    shortened_url = f"localhost:9595/info/{url_hash}"
    
    # Crear un nuevo registro de URLShort
    new_url = URLShort(original_url=item.url, name=url_hash)
    
    # Insertar el registro en la base de datos
    db.add(new_url)
    db.commit()
    
    return {"shortened_url": shortened_url}

