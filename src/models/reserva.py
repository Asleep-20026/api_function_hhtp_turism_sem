from sqlalchemy import Column, Integer, DateTime, ForeignKey, DECIMAL
from sqlalchemy.orm import relationship
from src.models.base import Base

class Reserva(Base):
    __tablename__ = 'reserva'
    id = Column(Integer, primary_key=True, autoincrement=True)
    fecha = Column(DateTime, nullable=False)
    destino_id = Column(Integer, ForeignKey('destino.id'), nullable=False)
    usuario_id = Column(Integer, ForeignKey('usuario.id'), nullable=False)
    guia_id = Column(Integer, ForeignKey('guia.id'), nullable=False)
    precio = Column(DECIMAL(20), nullable=False, default=0)

    # Relaciones
    destino = relationship("Destino")
    usuario = relationship("Usuario", back_populates="reservas")
    guia = relationship("Guia")
