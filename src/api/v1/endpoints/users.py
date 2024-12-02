from fastapi import APIRouter, Depends,status
from sqlalchemy import select
from sqlalchemy.orm import Session
from models import Plans, User, PlansAgreement
from schemas import PlansAgreementCreateSchema, PlansCreateSchema, PlansSchema, UserLoginSchema, UserRetrieveSchema, UserCreateSchema, Token,PlansAgreementSchema
from utils import get_db, create_access_token, get_current_user, authenticate_user
from passlib.context import CryptContext
from datetime import timedelta
from settings import settings
from datetime import datetime,timezone
from uuid import UUID

from responses import EnvelopeResponse,create_response_for_fast_api

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/users/", response_model=EnvelopeResponse)
def create_user(user: UserCreateSchema, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == user.username, User.is_removed == False).first()
    if existing_user:
        response = create_response_for_fast_api(
            status_code_http=status.HTTP_400_BAD_REQUEST,
            message="Username already registered"
        )
        return response
    existing_user = db.query(User).filter(User.email == user.email, User.is_removed == False).first()
    if existing_user:
        response = create_response_for_fast_api(
            status_code_http=status.HTTP_400_BAD_REQUEST,
            message="Email already registered"
        )
        return response
    hashed_password = pwd_context.hash(user.password)
    db_user = User(username=user.username, hashed_password=hashed_password, email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    response = create_response_for_fast_api(
        data=UserRetrieveSchema(**db_user.__dict__),
        message="User created successfully"
    )
    return response

@router.post("/token", response_model=EnvelopeResponse)
def login_for_access_token(form_data: UserLoginSchema = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        response = create_response_for_fast_api(
            status_code_http=status.HTTP_401_UNAUTHORIZED,
            message="Incorrect username or password",
        )
        return response
    access_token_expires = timedelta(minutes=settings.jwt_expiration_minutes)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    response = create_response_for_fast_api(
        data={"access_token": access_token, "token_type": "Bearer"},
        message="Token created successfully"
    )
    return response


@router.get("/users/me/", response_model=EnvelopeResponse)
def read_users_me(current_user: User = Depends(get_current_user)):
    response = create_response_for_fast_api(
        data=UserRetrieveSchema(**current_user.__dict__).model_dump(mode="json"),
        message="User retrieved successfully"
    )
    return response


@router.delete("/users/me/", response_model=EnvelopeResponse)
def delete_user_me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    current_user.is_removed = True
    db.commit()
    response = create_response_for_fast_api(
        message="User deleted successfully"
    )
    return response






@router.get("/plans/", response_model=EnvelopeResponse)
def get_plans(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = select(Plans).select_from(Plans).where(Plans.is_removed == False)
    plans = db.execute(query).scalars().all()
    plans_schema = [PlansSchema(**plan.__dict__).model_dump(mode="json") for plan in plans]

    response = create_response_for_fast_api(
        data={"plans": plans_schema},
        message="Plans retrieved successfully"
    )
    return response


@router.post("/plans/", response_model=EnvelopeResponse)
def create_plan(plan: PlansCreateSchema, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query_plan_duplicate = select(Plans).where(Plans.name == plan.name, Plans.is_removed == False)
    plan_duplicate = db.execute(query_plan_duplicate).scalars().first()
    if plan_duplicate:
        response = create_response_for_fast_api(
            status_code_http=status.HTTP_400_BAD_REQUEST,
            message="Plan name already exists"
        )
        return response
    
    db_plan = Plans(**plan.model_dump())
    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)
    plan_schema = PlansSchema(**db_plan.__dict__)
    response = create_response_for_fast_api(
        data=plan_schema,
        message="Plan created successfully"
    )
    return response

@router.post("/plans/agreement/", response_model=EnvelopeResponse)
def create_plan_agreement(plan_agreement: PlansAgreementCreateSchema, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query_plan = select(Plans).where(Plans.id == plan_agreement.plan_id, Plans.is_removed == False)
    plan = db.execute(query_plan).scalars().first()
    if not plan:
        response = create_response_for_fast_api(
            status_code_http=status.HTTP_400_BAD_REQUEST,
            message="Plan not found"
        )
        return response
    
    agrement_start_date = datetime.now(timezone.utc)
    agrement_end_date = agrement_start_date + timedelta(days=plan.duration_months * 30)
    
    query_plan_on_course = select(PlansAgreement).where(PlansAgreement.end_date >= agrement_start_date, PlansAgreement.user_id == current_user.id, PlansAgreement.is_removed == False)
    plan_on_course = db.execute(query_plan_on_course).scalars().first()
    if plan_on_course:
        response = create_response_for_fast_api(
            status_code_http=status.HTTP_400_BAD_REQUEST,
            message="Plan already on course"
        )
        return response
    
    db_plan_agreement = PlansAgreement(plan_id=plan_agreement.plan_id, user_id=current_user.id, start_date=agrement_start_date, end_date=agrement_end_date)
    db.add(db_plan_agreement)
    db.commit()
    db.refresh(db_plan_agreement)
    plan_agreement_schema = PlansAgreementSchema(**db_plan_agreement.__dict__) # type: ignore
    response = create_response_for_fast_api(
        data=plan_agreement_schema,
        message="Plan agreement created successfully"
    )
    return response

@router.get("/plans/agreement/", response_model=EnvelopeResponse)
def get_plan_agreement(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query_plan_agreement = select(PlansAgreement).where(PlansAgreement.user_id == current_user.id, PlansAgreement.is_removed == False)
    plan_agreement = db.execute(query_plan_agreement).scalars().all()
    plan_agreement_schema = [PlansAgreementSchema(**plan_agreement.__dict__).model_dump(mode="json") for plan_agreement in plan_agreement] # type: ignore
    response = create_response_for_fast_api(
        data={"plan_agreements": plan_agreement_schema},
        message="Plan agreement retrieved successfully"
    )
    return response


@router.delete("/plans/agreement/{plan_agreement_id}", response_model=EnvelopeResponse)
def delete_plan_agreement(plan_agreement_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query_plan_agreement = select(PlansAgreement).where(PlansAgreement.id == plan_agreement_id, PlansAgreement.user_id == current_user.id, PlansAgreement.is_removed == False)
    plan_agreement = db.execute(query_plan_agreement).scalars().first()
    if not plan_agreement:
        response = create_response_for_fast_api(
            status_code_http=status.HTTP_400_BAD_REQUEST,
            message="Plan agreement not found"
        )
        return response
    plan_agreement.is_removed = True
    db.commit()
    response = create_response_for_fast_api(
        message="Plan agreement deleted successfully"
    )
    return response




