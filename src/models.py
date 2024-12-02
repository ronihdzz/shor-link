from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

Base = declarative_base()

class BaseModel(Base):
    __abstract__ = True
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    is_removed = Column(Boolean, default=False)


class User(BaseModel):
    __tablename__ = "users"
    
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    email = Column(String, unique=True, index=True)
    
    plans_agreement = relationship('PlansAgreement', back_populates='user')
    url_short = relationship('URLShort', back_populates='user')

class Plans(BaseModel):
    __tablename__ = 'plans'
    
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    duration_months = Column(Integer, nullable=False)

    plans_agreement = relationship('PlansAgreement', back_populates='plan')

class PlansAgreement(BaseModel):
    __tablename__ = 'plans_agreement'
    
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    
    plan_id = Column(UUID(as_uuid=True), ForeignKey('plans.id'), nullable=False)
    plan = relationship('Plans', back_populates='plans_agreement')
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    user = relationship('User', back_populates='plans_agreement')

class URLShort(BaseModel):
    __tablename__ = 'url_short'
    
    original_url = Column(String, nullable=False)
    name = Column(String, unique=True, nullable=False)
    domain = Column(String, nullable=True)

    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    user = relationship('User', back_populates='url_short')
