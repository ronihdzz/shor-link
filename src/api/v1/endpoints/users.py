from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy import UUID, select
from sqlalchemy.orm import Session
from models import Plans, User, PlansAgreement
from schemas import PlansAgreementCreateSchema, PlansCreateSchema, PlansSchema, UserLoginSchema, UserRetrieveSchema, UserCreateSchema, Token,PlansAgreementSchema
from utils import get_db, create_access_token, get_current_user, authenticate_user
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta
from settings import settings
import pytz
from datetime import datetime,timezone
from fastapi.security import APIKeyHeader



router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/users/", response_model=UserRetrieveSchema)
def create_user(user: UserCreateSchema, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    hashed_password = pwd_context.hash(user.password)
    db_user = User(username=user.username, hashed_password=hashed_password, email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.post("/token", response_model=Token)
def login_for_access_token(form_data: UserLoginSchema = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.jwt_expiration_minutes)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "Bearer"}

@router.get("/plans/")
def get_plans(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = select(Plans).select_from(Plans).where(Plans.is_removed == False)
    plans = db.execute(query).scalars().all()
    plans_schema = [PlansSchema(**plan.__dict__) for plan in plans]
    
    return plans_schema


@router.post("/plans/")
def create_plan(plan: PlansCreateSchema, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query_plan_duplicate = select(Plans).where(Plans.name == plan.name)
    plan_duplicate = db.execute(query_plan_duplicate).scalars().first()
    if plan_duplicate:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Plan name already exists")
    
    db_plan = Plans(**plan.model_dump())
    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)
    plan_schema = PlansSchema(**db_plan.__dict__)
    return plan_schema

@router.post("/plans/agreement/")
def create_plan_agreement(plan_agreement: PlansAgreementCreateSchema, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query_plan = select(Plans).where(Plans.id == plan_agreement.plan_id)
    plan = db.execute(query_plan).scalars().first()
    if not plan:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Plan not found")
    
    agrement_start_date = datetime.now(timezone.utc)
    agrement_end_date = agrement_start_date + timedelta(days=plan.duration_months * 30)
    
    query_plan_on_course = select(PlansAgreement).where(PlansAgreement.end_date >= agrement_start_date, PlansAgreement.user_id == current_user.id)
    plan_on_course = db.execute(query_plan_on_course).scalars().first()
    if plan_on_course:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Plan already on course")
    
    db_plan_agreement = PlansAgreement(plan_id=plan_agreement.plan_id, user_id=current_user.id, start_date=agrement_start_date, end_date=agrement_end_date)
    db.add(db_plan_agreement)
    db.commit()
    db.refresh(db_plan_agreement)
    plan_agreement_schema = PlansAgreementSchema(**db_plan_agreement.__dict__) # type: ignore
    return plan_agreement_schema

@router.get("/plans/agreement/")
def get_plan_agreement(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query_plan_agreement = select(PlansAgreement).where(PlansAgreement.user_id == current_user.id, PlansAgreement.is_removed == False)
    plan_agreement = db.execute(query_plan_agreement).scalars().all()
    plan_agreement_schema = [PlansAgreementSchema(**plan_agreement.__dict__) for plan_agreement in plan_agreement] # type: ignore
    return plan_agreement_schema


@router.get("/users/me/", response_model=UserRetrieveSchema)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.delete("/users/me/")
def delete_user_me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db.delete(current_user)
    db.commit()
    return {"detail": "User deleted"}



