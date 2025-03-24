from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from src.models.base import Base

class Pais(Base):
    __tablename__ = 'pais'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)

    ciudades = relationship("Ciudad", back_populates="pais")
