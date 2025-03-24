from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Float

from sqlalchemy.orm import sessionmaker, relationship
Base = declarative_base()

class GuiaCalificacion(Base):
    __tablename__ = 'guia_calificacion'
    id = Column(Integer, primary_key=True)
    comentario = Column(String(255), nullable=True)
    calificacion = Column(Float, nullable=True)
    usuario_id = Column(Integer, ForeignKey('usuario.id'))
    guia_id = Column(Integer, ForeignKey('guia.id'))
    usuario = relationship("Usuario")
    guia = relationship("Guia")