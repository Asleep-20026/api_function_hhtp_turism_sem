from src.models.base import Base
from sqlalchemy import Column, Integer, String, ForeignKey

class MatrizPrecioUsuario(Base):
    __tablename__ = 'matriz_precio_usuario'
    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String(100), nullable=False)
    rangoPrecios = Column(String(100))
    cantidadUsuarios = Column(Integer)