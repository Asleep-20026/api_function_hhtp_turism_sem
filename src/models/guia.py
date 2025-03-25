from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey

from sqlalchemy.orm import sessionmaker, relationship
from src.models.base import Base
from src.models.genero import Genero

class Guia(Base):
    __tablename__ = 'guia'
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(String(100), nullable=False)
    anios_experiencia = Column(Integer, nullable=False)
    genero_id = Column(Integer, ForeignKey('genero.id'), nullable=False)
    genero = relationship("Genero")