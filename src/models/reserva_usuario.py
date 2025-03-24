from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Float

from sqlalchemy.orm import sessionmaker, relationship
Base = declarative_base()

class ReservaUsuario(Base):
    __tablename__ = 'reserva_usuario'
    id = Column(Integer, primary_key=True, nullable=False)
    reserva_id = Column(Integer, ForeignKey('reserva.id'), nullable=False)
    usuario_id = Column(Integer, ForeignKey('usuario.id'), nullable=False)
    reserva = relationship("Reserva")
    usuario = relationship("Usuario")