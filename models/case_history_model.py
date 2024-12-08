from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey, func
from config import Base

class CaseHistory(Base):
    __tablename__ = 'case_history'

    id = Column(Integer, primary_key=True, autoincrement=True)
    case_id = Column(Integer, nullable=False)
    client_id = Column(Integer, nullable=False)
    worker_id = Column(Integer, nullable=False)
    case_title = Column(String(255), nullable=False)
    case_description = Column(Text, nullable=True)
    case_status = Column(String(50), nullable=True)
    case_type = Column(String(50), nullable=True)
    court_date = Column(TIMESTAMP, nullable=True)
    judge_name = Column(String(100), nullable=True)
    archived_at = Column(TIMESTAMP, server_default=func.now())

    def __repr__(self):
        return f"<CaseHistory(id={self.id}, case_title='{self.case_title}', archived_at={self.archived_at})>"
