from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from src.models.base import Base

class Usuario(Base):
    __tablename__ = 'usuario'
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    usuario = Column(String(100), nullable=False, unique=True)
    contrasena = Column(String(50), nullable=False)

    # Relación inversa
    reservas = relationship("Reserva", back_populates="usuario")
