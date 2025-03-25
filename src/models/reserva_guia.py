from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import  Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
Base = declarative_base()

class ReservaGuia(Base):
    __tablename__ = 'reserva_guia'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    reserva_id = Column(Integer, ForeignKey('reserva.id'), nullable=False)
    guia_id = Column(Integer, ForeignKey('guia.id'), nullable=False)
    reserva = relationship("Reserva")
    guia = relationship("Guia")
