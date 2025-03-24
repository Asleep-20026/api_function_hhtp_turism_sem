from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey

from sqlalchemy.orm import sessionmaker, relationship
from src.models.base import Base
from src.models.destino import Destino

class Reserva(Base):
    __tablename__ = 'reserva'
    id = Column(Integer, primary_key=True, autoincrement=True)
    fecha = Column(DateTime, nullable=False)
    destino_id = Column(Integer, ForeignKey('destino.id'), nullable=False)
    destino = relationship("Destino")