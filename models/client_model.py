# models/client_model.py
from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, func
from config import Base

class Client(Base):
    __tablename__ = 'clients'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    second_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=False)
    second_last_name = Column(String(100), nullable=True)
    email = Column(String(100), unique=True, nullable=False)
    phone = Column(String(25), unique=True, nullable=False)
    address = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
