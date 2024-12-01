from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import URLShort
from database import get_db
from fastapi.responses import RedirectResponse

router = APIRouter()


@router.get("/health")
async def health_check():
    return {"status": "ok"}


@router.get("/info/{url_hash}")
async def redirect_to_url(url_hash: str, db: Session = Depends(get_db)):
    # Buscar el registro en la base de datos
    url_record = db.query(URLShort).filter_by(name=url_hash).first()
    
    # Si no se encuentra el registro, lanzar una excepción
    if not url_record:
        raise HTTPException(status_code=404, detail="URL no encontrada")
    
    # Redirigir a la URL original
    return RedirectResponse(url=url_record.original_url)