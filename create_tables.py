from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from session import Base  # Importa la clase Base desde session.py
from settings import settings

# Crea el motor de la base de datos
engine = create_engine(settings.DATABASE_URL)

# Crea las tablas en la base de datos si no existen
Base.metadata.create_all(engine)

print("Tablas creadas exitosamente si no existían.")