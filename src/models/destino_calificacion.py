from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Float


from sqlalchemy.orm import sessionmaker, relationship
Base = declarative_base()

class DestinoCalificacion(Base):
    __tablename__ = 'destino_calificacion'
    id = Column(Integer, primary_key=True)
    fecha = Column(DateTime, nullable=True)
    comentario = Column(String(255), nullable=True)
    calificacion = Column(Float, nullable=True)
    usuario_id = Column(Integer, ForeignKey('usuario.id'))
    usuario = relationship("Usuario")