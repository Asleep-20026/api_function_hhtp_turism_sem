from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
Base = declarative_base()

class Idioma(Base):
    __tablename__ = 'idioma'
    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=True)