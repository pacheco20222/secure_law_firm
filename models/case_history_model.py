# models/case_model.py
from sqlalchemy import Column, Integer, ForeignKey, TIMESTAMP, func, Text
from sqlalchemy.orm import relationship
from config import Base


class case_history(Base):
    __tablename__ = 'case_history'
    
    id = Column(Integer, primary_key=True)
    case_id = Column(Integer, ForeignKey('cases.id'), nullable=False)
    worker_id = Column(Integer, ForeignKey('workers.id'), nullable=False)
    update_description = Column(Text)
    updated_at = Column(TIMESTAMP, server_default=func.now())
