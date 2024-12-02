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
from responses import EnvelopeResponse,create_response_for_fast_api


router = APIRouter()

# Endpoint para acortar URL
@router.post("/shorten", response_model=EnvelopeResponse)
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
        query_count_urls = select(func.count()).where(URLShort.user_id == current_user.id, URLShort.is_removed == False)
        count_urls = db.execute(query_count_urls).scalars().first()
        if count_urls > settings.MAX_URLS_FREE:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You have reached the maximum number of URLs allowed for your plan")


    query_url_short = select(URLShort).where(URLShort.original_url == item.url, URLShort.user_id == current_user.id, URLShort.is_removed == False)
    url_short = db.execute(query_url_short).scalars().first()
    if url_short:
        response = create_response_for_fast_api(
            data={"shortened_url": f"{settings.DOMAIN}/info/{url_short.name}"},
            message="URL shortened successfully"
        )
        return response
    
    url_hash = str(uuid.uuid4())[:8]
    shortened_url = f"{settings.DOMAIN}/info/{url_hash}"
    
    # Crear un nuevo registro de URLShort
    new_url = URLShort(original_url=item.url, name=url_hash, user_id=current_user.id)
    
    # Insertar el registro en la base de datos
    db.add(new_url)
    db.commit()
    
    response = create_response_for_fast_api(
        data={"shortened_url": shortened_url},
        message="URL shortened successfully"
    )
    return response

@router.post("/shorten-plan/", response_model=EnvelopeResponse)
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


    query_url_short = select(URLShort).where(URLShort.original_url == item.url, URLShort.user_id == current_user.id, URLShort.is_removed == False)
    url_short = db.execute(query_url_short).scalars().first()
    if url_short and url_short.domain:
        response = create_response_for_fast_api(
            data={"shortene_url": f"{settings.DOMAIN}/info/{url_short.domain}/{url_short.name}"},
            message="URL shortened successfully"
        )
        return response
    elif url_short:
        url_short.domain = item.domain
        db.commit()
        db.refresh(url_short)
        response = create_response_for_fast_api(
            data={"shortene_url": f"{settings.DOMAIN}/info/{url_short.name}"},
            message="URL shortened successfully"
        )
        return response
    
    # Generar un hash aleatorio único para la URL
    url_hash = str(uuid.uuid4())[:8]
    shortened_url = f"{settings.DOMAIN}/info/{item.domain}/{url_hash}"

    new_url = URLShort(original_url=item.url, name=url_hash, domain=item.domain, user_id=current_user.id)
    db.add(new_url)
    db.commit()
    db.refresh(new_url)

    response = create_response_for_fast_api(
        data={"shortened_url": shortened_url},
        message="URL shortened successfully"
    )
    return response


@router.get("/urls", response_model=EnvelopeResponse)
async def list_urls_created(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    urls = db.query(URLShort).filter_by(user_id=current_user.id, is_removed=False).all()
    list_urls = [
        {
            "shortened_url": f"{settings.DOMAIN}/info/{url.name}" if not url.domain else f"{settings.DOMAIN}/info/{url.domain}/{url.name}",
            "original_url": url.original_url,
            "domain": url.domain,
            "user_id": str(url.user_id)
            
        } for url in urls
    ]
    response = create_response_for_fast_api(
        data={"urls": list_urls},
        message="URLs retrieved successfully"
    )
    return response