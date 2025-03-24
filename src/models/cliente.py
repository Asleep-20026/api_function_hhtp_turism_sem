from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Float


from sqlalchemy.orm import sessionmaker, relationship
Base = declarative_base()

class Cliente(Base):
    __tablename__ = 'cliente'
    id = Column(Integer, primary_key=True, nullable=False)
    nombre = Column(String(100), nullable=False)
    usuario_id = Column(Integer, ForeignKey('usuario.id'), nullable=False, unique=True)
    usuario = relationship("Usuario")