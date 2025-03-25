# src/models/base.py
from sqlalchemy.orm import declarative_base

Base = declarative_base()

# 🔥 Registro explícito de modelos (esto previene errores de mapeo)
import src.models.usuario
import src.models.destino
import src.models.guia
import src.models.guia_calificacion
import src.models.destino_calificacion
import src.models.ciudad
import src.models.reserva
import src.models.reserva_guia
