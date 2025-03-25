
import azure.functions as func
from sqlalchemy.exc import IntegrityError
import os
import urllib.parse
import json
import hashlib

from sqlalchemy import create_engine, exists
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session
from decimal import Decimal
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
    """Convierte un SQLAlchemy obj a diccionario serializable."""
    result = {}
    for column in obj.__table__.columns:
        value = getattr(obj, column.name)
        
        # Convertir datetime a string ISO 8601
        if isinstance(value, datetime):
            result[column.name] = value.isoformat()
        # Convertir Decimal a float
        elif isinstance(value, Decimal):
            result[column.name] = float(value)
        else:
            result[column.name] = value

    return result


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
    Create a new reservation with robust error handling and entity creation
    """
    try:
        # Parse input data
        fecha = datetime.fromisoformat(reserva_data['fecha'])
        
        # Retrieve or create related entities if they don't exist
        destino_id = reserva_data['destino_id']
        usuario_id = reserva_data['usuario_id']
        guia_id = reserva_data['guia_id']
        
        # First, ensure the ciudad exists
        ciudad = session.query(Ciudad).filter(Ciudad.id == 1).first()
        if not ciudad:
            # Create a default ciudad if it doesn't exist
            ciudad = Ciudad(
                id=1,
                nombre="Ciudad por Defecto",
                pais_id=1  # Asume que tienes un país por defecto
            )
            session.add(ciudad)
        
        # Try to find existing entities, create if not found
        destino = session.query(Destino).filter(Destino.id == destino_id).first()
        if not destino:
            # Create a new Destino if it doesn't exist
            destino = Destino(
                id=destino_id, 
                nombre=f"Destino {destino_id}", 
                ciudad_id=ciudad.id,  # Use the existing or newly created ciudad
                descripcion="Destino creado automáticamente"
            )
            session.add(destino)
        
        # Rest of the function remains the same...
        usuario = session.query(Usuario).filter(Usuario.id == usuario_id).first()
        if not usuario:
            # Create a new Usuario if it doesn't exist
            usuario = Usuario(
                id=usuario_id,
                nombre=f"Usuario {usuario_id}", 
                usuario=f"usuario_{usuario_id}",
                contrasena="temp_password"
            )
            session.add(usuario)
        
        guia = session.query(Guia).filter(Guia.id == guia_id).first()
        if not guia:
            # Create a new Guia if it doesn't exist
            guia = Guia(
                id=guia_id,
                nombre=f"Guia {guia_id}", 
                descripcion="Guia creado automáticamente",
                anios_experiencia=0,
                genero_id=1  # Provide a default genero_id
            )
            session.add(guia)
        
        # Create new reservation (rest of the function remains the same)
        nueva_reserva = Reserva(
            fecha=fecha,
            destino_id=destino_id,
            usuario_id=usuario_id,
            guia_id=guia_id,
            precio=reserva_data['precio']
        )
        
        session.add(nueva_reserva)
        session.commit()
        session.refresh(nueva_reserva)
        
        # Prepare response (same as before)
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
        print(f"Error creating reservation: {str(e)}")
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
                # Log the full request body for debugging
                req_body = req.get_json()
                print("Received reservation request body:")
                print(json.dumps(req_body, indent=2))
                
                result = crear_reserva(session, req_body)
                return func.HttpResponse(
                    json.dumps(result), 
                    mimetype="application/json",
                    status_code=200
                )
            except ValueError as ve:
                # Log the specific ValueError
                print(f"ValueError: {str(ve)}")
                return func.HttpResponse(
                    json.dumps({"error": str(ve)}), 
                    mimetype="application/json",
                    status_code=400
                )
            except Exception as e:
                # Log any other unexpected exceptions
                print(f"Unexpected error: {str(e)}")
                import traceback
                traceback.print_exc()
                return func.HttpResponse(
                    json.dumps({"error": str(e)}), 
                    mimetype="application/json",
                    status_code=500
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

@app.route(route="guias")
def get_guias(req: func.HttpRequest) -> func.HttpResponse:
    """Endpoint para obtener todos los guías"""
    try:
        session = SessionLocal()
        guias = session.query(Guia).all()
        
        # Convertir guías a lista de diccionarios con información detallada
        guias_list = []
        for guia in guias:
            guia_dict = to_dict(guia)
            # Añadir información del género
            guia_dict['genero'] = to_dict(guia.genero) if guia.genero else None
            guias_list.append(guia_dict)
        
        session.close()
        return func.HttpResponse(
            json.dumps(guias_list, ensure_ascii=False),
            mimetype="application/json",
            status_code=200
        )
    except Exception as e:
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json", 
            status_code=500
        )

@app.route(route="guias/{id}")
def get_guia_by_id(req: func.HttpRequest) -> func.HttpResponse:
    """Endpoint para obtener un guía por su ID"""
    try:
        guia_id = req.route_params.get('id')
        session = SessionLocal()
        
        guia = session.query(Guia).filter(Guia.id == guia_id).first()
        
        if not guia:
            return func.HttpResponse(
                json.dumps({"error": "Guía no encontrado"}),
                mimetype="application/json",
                status_code=404
            )
        
        # Convertir guía a diccionario con información detallada
        guia_dict = to_dict(guia)
        guia_dict['genero'] = to_dict(guia.genero) if guia.genero else None
        
        session.close()
        return func.HttpResponse(
            json.dumps(guia_dict, ensure_ascii=False),
            mimetype="application/json",
            status_code=200
        )
    except Exception as e:
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json", 
            status_code=500
        )

@app.route(route="usuarios/{id}")
def get_usuario_by_id(req: func.HttpRequest) -> func.HttpResponse:
    """Endpoint para obtener un usuario por su ID"""
    try:
        usuario_id = req.route_params.get('id')
        session = SessionLocal()
        
        usuario = session.query(Usuario).filter(Usuario.id == usuario_id).first()
        
        if not usuario:
            return func.HttpResponse(
                json.dumps(usuario_dict, ensure_ascii=False, default=custom_serializer),
                mimetype="application/json",
                status_code=200
            )
        
        # Convertir usuario a diccionario
        usuario_dict = to_dict(usuario)
        
        # Opcional: Añadir información de reservas
        reservas = [to_dict(reserva) for reserva in usuario.reservas]
        usuario_dict['reservas'] = reservas
        
        session.close()
        return func.HttpResponse(
            json.dumps(usuario_dict, ensure_ascii=False),
            mimetype="application/json",
            status_code=200
        )
    except Exception as e:
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json", 
            status_code=500
        )

def custom_serializer(obj):
    """Serializa objetos no JSON directamente soportados."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError("Tipo no serializable")

@app.route(route="usuarios/login", methods=["POST"])
def login_usuario(req: func.HttpRequest) -> func.HttpResponse:
    """Endpoint para login de usuario"""
    try:
        # Parsear el cuerpo de la solicitud
        req_body = req.get_json()
        usuario = req_body.get('usuario')
        contrasena = req_body.get('contrasena')

        # Validar que se proporcionen usuario y contraseña
        if not usuario or not contrasena:
            return func.HttpResponse(
                json.dumps({"error": "Usuario y contraseña son requeridos"}),
                mimetype="application/json",
                status_code=400
            )

        # Crear sesión de base de datos
        session = SessionLocal()

        # Hashear la contraseña de la misma manera que en el registro
        hashed_password = hashlib.sha256(contrasena.encode()).hexdigest()

        # Buscar usuario en la base de datos
        user = session.query(Usuario).filter(
            Usuario.usuario == usuario, 
            Usuario.contrasena == hashed_password
        ).first()

        session.close()

        # Verificar si el usuario existe
        if user:
            return func.HttpResponse(
                json.dumps({"status": "success"}),
                mimetype="application/json",
                status_code=200
            )
        else:
            return func.HttpResponse(
                json.dumps({"error": "Credenciales inválidas"}),
                mimetype="application/json",
                status_code=401
            )

    except Exception as e:
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json", 
            status_code=500
        )

@app.route(route="usuarios/register", methods=["POST"])
def register_usuario(req: func.HttpRequest) -> func.HttpResponse:
    """Endpoint para registro de usuario"""
    try:
        # Parsear el cuerpo de la solicitud
        req_body = req.get_json()
        nombre = req_body.get('nombre')
        usuario = req_body.get('usuario')
        contrasena = req_body.get('contrasena')

        # Validar que se proporcionen todos los campos
        if not nombre or not usuario or not contrasena:
            return func.HttpResponse(
                json.dumps({"error": "Todos los campos son requeridos"}),
                mimetype="application/json",
                status_code=400
            )

        # Crear sesión de base de datos
        session = SessionLocal()

        # Verificar si el usuario ya existe
        existing_user = session.query(exists().where(Usuario.usuario == usuario)).scalar()
        if existing_user:
            session.close()
            return func.HttpResponse(
                json.dumps({"error": "El nombre de usuario ya existe"}),
                mimetype="application/json",
                status_code=409
            )

        # Hashear la contraseña
        hashed_password = hashlib.sha256(contrasena.encode()).hexdigest()

        # Crear nuevo usuario
        nuevo_usuario = Usuario(
            nombre=nombre,
            usuario=usuario,
            contrasena=hashed_password
        )

        try:
            # Guardar usuario en la base de datos
            session.add(nuevo_usuario)
            session.commit()

            # Preparar respuesta con información del usuario
            response_data = {
                "id": nuevo_usuario.id,
                "nombre": nuevo_usuario.nombre,
                "usuario": nuevo_usuario.usuario,
                "status": "success"
            }

            session.close()
            return func.HttpResponse(
                json.dumps(response_data),
                mimetype="application/json",
                status_code=200
            )

        except Exception as e:
            session.rollback()
            return func.HttpResponse(
                json.dumps({"error": "Error al crear el usuario", "details": str(e)}),
                mimetype="application/json",
                status_code=500
            )

    except Exception as e:
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json", 
            status_code=500
        )
@app.route(route="MatrizPrecioUsuario", methods=["GET"])
def get_matriz_precio_usuario(req: func.HttpRequest) -> func.HttpResponse:
    """
    Endpoint para obtener información de la tabla MatrizPrecioUsuario
    
    Returns:
    - Información de la tabla con sus columnas y metadatos
    - Registros de la tabla (opcional, dependiendo de tus requisitos)
    """
    try:
        # Iniciar sesión de base de datos
        db = SessionLocal()
        
        # Recuperar todos los registros de MatrizPrecioUsuario
        matriz_precios = db.query(MatrizPrecioUsuario).all()
        
        # Preparar la respuesta con información de la tabla
        table_info = {
            "table": "matriz_precio_usuario",
            "columns": [
                {
                    "name": "id",
                    "type": "Integer",
                    "primary_key": True,
                    "autoincrement": True,
                    "nullable": False
                },
                {
                    "name": "type",
                    "type": "String",
                    "length": 100,
                    "nullable": False
                },
                {
                    "name": "rangoPrecios",
                    "type": "String",
                    "length": 100,
                    "nullable": True
                },
                {
                    "name": "cantidadUsuarios",
                    "type": "Integer",
                    "nullable": True
                }
            ],
            "records": [to_dict(registro) for registro in matriz_precios]
        }
        
        # Cerrar sesión de base de datos
        db.close()
        
        # Devolver respuesta JSON
        return func.HttpResponse(
            json.dumps(table_info, ensure_ascii=False),
            mimetype="application/json",
            status_code=200
        )
    
    except Exception as e:
        # Manejo de errores
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json", 
            status_code=500
        )