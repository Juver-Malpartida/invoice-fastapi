# database.py
from sqlmodel import SQLModel, create_engine, Session
from config import settings

# Crear el motor de base de datos usando la configuración
engine = create_engine(settings.database_url, echo=False)

def create_db_and_tables():
    """Crear las tablas en la base de datos."""
    SQLModel.metadata.create_all(engine)

def get_session():
    """Obtener una sesión de base de datos."""
    with Session(engine) as session:
        yield session
