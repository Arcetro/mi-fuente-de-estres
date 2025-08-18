from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import declarative_base
from sqlalchemy.engine import Engine


Base = declarative_base()

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    session_id = Column(String, index=True)
    direction = Column(String)  # "inbound" or "outbound"
    text = Column(String)

def init_db(engine: Engine):
    Base.metadata.create_all(bind=engine)

def drop_db(engine: Engine):
    Base.metadata.drop_all(bind=engine)
