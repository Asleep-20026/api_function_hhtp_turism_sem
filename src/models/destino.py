from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey

from sqlalchemy.orm import sessionmaker, relationship
from src.models.base import Base
from src.models.ciudad import Ciudad

class Destino(Base):
    __tablename__ = 'destino'
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    ciudad_id = Column(Integer, ForeignKey('ciudad.id'), nullable=False)
    descripcion = Column(String(100))
    ciudad = relationship("Ciudad")