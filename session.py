from sqlalchemy import create_engine, Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import uuid

from settings import settings

# Crea el motor de la base de datos
engine = create_engine(settings.DATABASE_URL)

# Crea una clase base para los modelos
Base = declarative_base()

# Define el modelo de la tabla
class URLShort(Base):
    __tablename__ = 'url_short'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    original_url = Column(String, nullable=False)
    name = Column(String, unique=True, nullable=False)
    domain = Column(String, nullable=True)

# Crea una sesión
Session = sessionmaker(bind=engine)
session = Session()
