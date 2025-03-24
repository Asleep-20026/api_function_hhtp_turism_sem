from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey

from sqlalchemy.orm import sessionmaker, relationship
from src.models.base import Base

class Genero(Base):
    __tablename__ = 'genero'
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=True)