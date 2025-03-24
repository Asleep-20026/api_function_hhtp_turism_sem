from sqlalchemy import create_engine, Column, Integer, String


from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Usuario(Base):
    __tablename__ = 'usuario'
    id = Column(Integer, primary_key=True, autoincrement=True)
    usuario = Column(String(100), unique=True, nullable=False)
    contrasena = Column(String(50), nullable=False)