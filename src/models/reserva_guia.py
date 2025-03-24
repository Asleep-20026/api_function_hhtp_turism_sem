from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey

from sqlalchemy.orm import sessionmaker, relationship
Base = declarative_base()

class ReservaGuia(Base):
    __tablename__ = 'reserva_guia'
    id = Column(Integer, primary_key=True, nullable=False)
    reserva_id = Column(Integer, ForeignKey('reserva.id'), nullable=False)
    guia_id = Column(Integer, ForeignKey('guia.id'), nullable=False)
    reserva = relationship("Reserva")
    guia = relationship("Guia")
