from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, func
from config import Base

class ClientHistory(Base):
    __tablename__ = 'client_history'

    id = Column(Integer, primary_key=True, autoincrement=True)
    client_id = Column(Integer, nullable=False)
    name = Column(String(100), nullable=False)
    second_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=False)
    second_last_name = Column(String(100), nullable=True)
    email = Column(String(100), nullable=False)
    phone = Column(String(25), nullable=False)
    address = Column(Text, nullable=True)
    curp = Column(String(20), nullable=True)
    archived_at = Column(TIMESTAMP, server_default=func.now())

    def __repr__(self):
        return f"<ClientHistory(id={self.id}, name='{self.name}', archived_at={self.archived_at})>"