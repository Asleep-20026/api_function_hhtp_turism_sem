from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Float

from sqlalchemy.orm import sessionmaker, relationship
Base = declarative_base()

class GuiaCalificacion(Base):
    __tablename__ = 'guia_calificacion'
    id = Column(Integer, primary_key=True, autoincrement=True)
    reserva_id = Column(Integer, ForeignKey('reserva.id'), nullable=False)
    fecha = Column(DateTime, nullable=False)
    comentario = Column(String(500), nullable=False)
    calificacion = Column(Integer, nullable=False)
    usuario_id = Column(Integer, ForeignKey('usuario.id'), nullable=False)
    guia_id = Column(Integer, ForeignKey('guia.id'), nullable=False)
    usuario = relationship("Usuario")
    guia = relationship("Guia")