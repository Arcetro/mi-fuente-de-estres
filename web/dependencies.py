from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from infra.dedupe import build_deduper as build_deduper_instance
from config.settings import settings

# Database Engine
engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Deduper
deduper = build_deduper_instance()

def get_deduper():
    return deduper
