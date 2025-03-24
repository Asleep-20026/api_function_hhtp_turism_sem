from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey

from sqlalchemy.orm import sessionmaker, relationship
Base = declarative_base()

class GuiaIdioma(Base):
    __tablename__ = 'guia_idioma'

    id = Column(Integer, primary_key=True, nullable=False)
    guia_id = Column(Integer, nullable=False)
    idioma_id = Column(Integer, nullable=False)