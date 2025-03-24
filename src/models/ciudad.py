from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from src.models.base import Base
from src.models.pais import Pais  # Importación aquí, después de definir Base

class Ciudad(Base):
    __tablename__ = 'ciudad'
    
    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    pais_id = Column(Integer, ForeignKey('pais.id'), nullable=False)

    pais = relationship("Pais", back_populates="ciudades")
