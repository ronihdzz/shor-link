from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from schemas import URLShortCreateSchema, URLShortPlanCreateSchema
from models import PlansAgreement, URLShort, User
from utils import get_current_user, get_db
import uuid
from sqlalchemy.orm import Session
from settings import settings
from sqlalchemy import select, func
from fastapi import status

router = APIRouter()

# Endpoint para acortar URL
@router.post("/shorten")
async def shorten_url(item: URLShortCreateSchema, db: Session = Depends(get_db),current_user: User = Depends(get_current_user)):
    # Generar un hash aleatorio único para la URL

    today = datetime.now(timezone.utc)

    query_plan_agreement = select(PlansAgreement).where(
        PlansAgreement.user_id == current_user.id,
        PlansAgreement.is_removed == False,
        PlansAgreement.end_date >= today
    )
    plan_agreement = db.execute(query_plan_agreement).scalars().first()
    
    if not plan_agreement:
        query_count_urls = select(func.count()).where(URLShort.user_id == current_user.id)
        count_urls = db.execute(query_count_urls).scalars().first()
        if count_urls > settings.MAX_URLS_FREE:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You have reached the maximum number of URLs allowed for your plan")


    query_url_short = select(URLShort).where(URLShort.original_url == item.url, URLShort.user_id == current_user.id)
    url_short = db.execute(query_url_short).scalars().first()
    if url_short:
        return {
            "shortened_url": f"{settings.DOMAIN}/info/{url_short.name}"
        }
    
    url_hash = str(uuid.uuid4())[:8]
    shortened_url = f"{settings.DOMAIN}/info/{url_hash}"
    
    # Crear un nuevo registro de URLShort
    new_url = URLShort(original_url=item.url, name=url_hash, user_id=current_user.id)
    
    # Insertar el registro en la base de datos
    db.add(new_url)
    db.commit()
    
    return {"shortened_url": shortened_url}

@router.post("/shorten-plan/")
async def get_shorten_premium(item: URLShortPlanCreateSchema, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):

    today = datetime.now(timezone.utc)

    query_plan_agreement = select(PlansAgreement).where(
        PlansAgreement.user_id == current_user.id,
        PlansAgreement.is_removed == False,
        PlansAgreement.end_date >= today
    )
    plan_agreement = db.execute(query_plan_agreement).scalars().first()
    if not plan_agreement:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Don't have a plan on course")


    query_url_short = select(URLShort).where(URLShort.original_url == item.url, URLShort.user_id == current_user.id)
    url_short = db.execute(query_url_short).scalars().first()
    if url_short and url_short.domain:
        return {
            "shortene_url": f"{settings.DOMAIN}/info/{url_short.domain}/{url_short.name}"
        }
    elif url_short:
        url_short.domain = item.domain
        db.commit()
        db.refresh(url_short)
        return {
            "shortene_url": f"{settings.DOMAIN}/info/{url_short.name}"
        }
    
    # Generar un hash aleatorio único para la URL
    url_hash = str(uuid.uuid4())[:8]
    shortened_url = f"{settings.DOMAIN}/info/{item.domain}/{url_hash}"

    new_url = URLShort(original_url=item.url, name=url_hash, domain=item.domain, user_id=current_user.id)
    db.add(new_url)
    db.commit()
    db.refresh(new_url)

    return {
        "shortened_url": shortened_url
    }


@router.get("/urls")
async def list_urls_created(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    urls = db.query(URLShort).filter_by(user_id=current_user.id, is_removed=False).all()
    list_urls = [
        {
            "shortened_url": f"{settings.DOMAIN}/info/{url.name}",
            "original_url": url.original_url,
            "domain": url.domain,
            "user_id": url.user_id
            
        } for url in urls
    ]
    return list_urls