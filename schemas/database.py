from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "postgresql://postgres:yamsaid@localhost:5432/api_db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# Dépendance pour récupérer la session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()