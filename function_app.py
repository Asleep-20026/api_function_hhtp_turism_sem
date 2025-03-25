import azure.functions as func

import os
import urllib.parse
import json

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session

from src.models.usuario import Usuario
from src.models.destino import Destino
from src.models.ciudad import Ciudad
from src.models.guia import Guia
from src.models.reserva import Reserva
from src.models.reserva_usuario import ReservaUsuario
from src.models.reserva_guia import ReservaGuia
from src.models.genero import Genero
from src.models.guia_calificacion import GuiaCalificacion
from src.models.destino_calificacion import DestinoCalificacion
from src.models.pais import Pais
from src.models.idioma import Idioma
from src.models.guia_idioma import GuiaIdioma
from src.models.matriz_precio_usaurio import MatrizPrecioUsuario
from datetime import datetime
import pytz

# Database Connection Configuration
server = os.getenv("SQL_SERVER")
database = os.getenv("SQL_DATABASE", "db_tourismo2")
username = os.getenv("SQL_USERNAME")
password = os.getenv("SQL_PASSWORD")
encoded_password = urllib.parse.quote_plus(password)

DB_URL = f"mssql+pyodbc://{username}:{encoded_password}@{server}/{database}?driver=ODBC+Driver+18+for+SQL+Server&Encrypt=yes&TrustServerCertificate=no&Connection Timeout=30"

# Create engine and session
engine = create_engine(DB_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Helper function to convert SQLAlchemy objects to dictionaries
def to_dict(obj):
    return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}

# Azure Function App
app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

def get_all_reservas(session: Session):
    """
    Retrieve all reservations with related information
    """
    reservas = session.query(Reserva).all()
    return [
        {
            "id": reserva.id,
            "fecha": reserva.fecha.isoformat(),
            "destino": {
                "id": reserva.destino.id,
                "nombre": reserva.destino.nombre
            },
            "usuario": {
                "id": reserva.usuario.id,
                "nombre": reserva.usuario.nombre
            },
            "guia": {
                "id": reserva.guia.id,
                "nombre": reserva.guia.nombre
            },
            "precio": float(reserva.precio)
        } for reserva in reservas
    ]

def get_reserva_by_id(session: Session, reserva_id: int):
    """
    Retrieve a specific reservation by ID
    """
    reserva = session.query(Reserva).filter(Reserva.id == reserva_id).first()
    if not reserva:
        return None
    
    return {
        "id": reserva.id,
        "fecha": reserva.fecha.isoformat(),
        "destino": {
            "id": reserva.destino.id,
            "nombre": reserva.destino.nombre
        },
        "usuario": {
            "id": reserva.usuario.id,
            "nombre": reserva.usuario.nombre
        },
        "guia": {
            "id": reserva.guia.id,
            "nombre": reserva.guia.nombre
        },
        "precio": float(reserva.precio)
    }

def get_reservas_by_guia(session: Session, guia_id: int):
    """
    Retrieve reservations for a specific guide
    """
    reservas = session.query(Reserva).filter(Reserva.guia_id == guia_id).all()
    return [
        {
            "id": reserva.id,
            "fecha": reserva.fecha.isoformat(),
            "destino": {
                "id": reserva.destino.id,
                "nombre": reserva.destino.nombre
            },
            "usuario": {
                "id": reserva.usuario.id,
                "nombre": reserva.usuario.nombre
            },
            "precio": float(reserva.precio)
        } for reserva in reservas
    ]

def get_reservas_by_usuario(session: Session, usuario_id: int):
    """
    Retrieve reservations for a specific user
    """
    reservas = session.query(Reserva).filter(Reserva.usuario_id == usuario_id).all()
    return [
        {
            "id": reserva.id,
            "fecha": reserva.fecha.isoformat(),
            "destino": {
                "id": reserva.destino.id,
                "nombre": reserva.destino.nombre
            },
            "guia": {
                "id": reserva.guia.id,
                "nombre": reserva.guia.nombre
            },
            "precio": float(reserva.precio)
        } for reserva in reservas
    ]

def crear_reserva(session: Session, reserva_data: dict):
    """
    Create a new reservation
    """
    try:
        # Parse input data
        fecha = datetime.fromisoformat(reserva_data['fecha'])
        
        # Validate related entities exist
        destino = session.query(Destino).filter(Destino.id == reserva_data['destino_id']).first()
        usuario = session.query(Usuario).filter(Usuario.id == reserva_data['usuario_id']).first()
        guia = session.query(Guia).filter(Guia.id == reserva_data['guia_id']).first()
        
        if not (destino and usuario and guia):
            raise ValueError("Destino, Usuario, or Guia not found")
        
        # Create new reservation
        nueva_reserva = Reserva(
            fecha=fecha,
            destino_id=reserva_data['destino_id'],
            usuario_id=reserva_data['usuario_id'],
            guia_id=reserva_data['guia_id'],
            precio=reserva_data['precio']
        )
        
        session.add(nueva_reserva)
        session.commit()
        session.refresh(nueva_reserva)
        
        # Prepare response
        return {
            "success": True,
            "message": "Reserva creada exitosamente",
            "data": {
                "id": nueva_reserva.id,
                "fecha": nueva_reserva.fecha.isoformat(),
                "destino": {
                    "id": destino.id,
                    "nombre": destino.nombre
                },
                "usuario": {
                    "id": usuario.id,
                    "nombre": usuario.nombre
                },
                "guia": {
                    "id": guia.id,
                    "nombre": guia.nombre
                },
                "precio": float(nueva_reserva.precio)
            },
            "metadata": {
                "table": "reserva",
                "created_at": datetime.now(pytz.UTC).isoformat()
            }
        }
    except Exception as e:
        session.rollback()
        raise

@app.route(route="reservas")
def reservas_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """
    Main endpoint for reservations
    Supports GET (all reservas) and POST (create reserva)
    """
    session = SessionLocal()
    try:
        if req.method == "GET":
            reservas = get_all_reservas(session)
            return func.HttpResponse(
                json.dumps(reservas), 
                mimetype="application/json",
                status_code=200
            )
        
        elif req.method == "POST":
            try:
                req_body = req.get_json()
                result = crear_reserva(session, req_body)
                return func.HttpResponse(
                    json.dumps(result), 
                    mimetype="application/json",
                    status_code=200
                )
            except ValueError as ve:
                return func.HttpResponse(
                    json.dumps({"error": str(ve)}), 
                    mimetype="application/json",
                    status_code=400
                )
    except Exception as e:
        return func.HttpResponse(
            json.dumps({"error": str(e)}), 
            mimetype="application/json",
            status_code=500
        )
    finally:
        session.close()

@app.route(route="reservas/{id}")
def reserva_by_id_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """
    Endpoint to get a specific reservation by ID
    """
    session = SessionLocal()
    try:
        reserva_id = int(req.route_params.get('id'))
        reserva = get_reserva_by_id(session, reserva_id)
        
        if reserva:
            return func.HttpResponse(
                json.dumps(reserva), 
                mimetype="application/json",
                status_code=200
            )
        else:
            return func.HttpResponse(
                json.dumps({"error": "Reserva no encontrada"}), 
                mimetype="application/json",
                status_code=404
            )
    except Exception as e:
        return func.HttpResponse(
            json.dumps({"error": str(e)}), 
            mimetype="application/json",
            status_code=500
        )
    finally:
        session.close()

@app.route(route="reservas/guia/{id}")
def reservas_by_guia_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """
    Endpoint to get reservations for a specific guide
    """
    session = SessionLocal()
    try:
        guia_id = int(req.route_params.get('id'))
        reservas = get_reservas_by_guia(session, guia_id)
        
        return func.HttpResponse(
            json.dumps(reservas), 
            mimetype="application/json",
            status_code=200
        )
    except Exception as e:
        return func.HttpResponse(
            json.dumps({"error": str(e)}), 
            mimetype="application/json",
            status_code=500
        )
    finally:
        session.close()

@app.route(route="reservas/usuario/{id}")
def reservas_by_usuario_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """
    Endpoint to get reservations for a specific user
    """
    session = SessionLocal()
    try:
        usuario_id = int(req.route_params.get('id'))
        reservas = get_reservas_by_usuario(session, usuario_id)
        
        return func.HttpResponse(
            json.dumps(reservas), 
            mimetype="application/json",
            status_code=200
        )
    except Exception as e:
        return func.HttpResponse(
            json.dumps({"error": str(e)}), 
            mimetype="application/json",
            status_code=500
        )
    finally:
        session.close()