# models/case_model.py
from sqlalchemy import Column, Integer, String, Date, ForeignKey, TIMESTAMP, func, Text
from sqlalchemy.orm import relationship
from config import Base

class Case(Base):
    __tablename__ = 'cases'
    
    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey('clients.id'), nullable=False)
    worker_id = Column(Integer, ForeignKey('workers.id'), nullable=False)
    case_title = Column(String(255), nullable=False)
    case_description = Column(Text)
    case_status = Column(String(50))
    case_type = Column(String(50), nullable=False)
    court_date = Column(Date)
    judge_name = Column(String(100))
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    client = relationship("Client")
    worker = relationship("Worker")