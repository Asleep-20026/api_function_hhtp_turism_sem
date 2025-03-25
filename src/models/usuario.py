from sqlalchemy import create_engine, Column, Integer, String


from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Usuario(Base):
    __tablename__ = 'usuario'
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    usuario = Column(String(100), nullable=False, unique=True)
    contrasena = Column(String(50), nullable=False)