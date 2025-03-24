import azure.functions as func
import logging
import json
import os
import urllib.parse
from typing import List, Dict, Any

from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.exc import SQLAlchemyError

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
from src.models.cliente import Cliente
from src.models.idioma import Idioma
from src.models.guia_idioma import GuiaIdioma
from datetime import datetime

# Database Connection Configuration
server = os.getenv("SQL_SERVER", "sem6.database.windows.net")
database = os.getenv("SQL_DATABASE", "db_tourismo")
username = os.getenv("SQL_USERNAME", "admin2025")
password = os.getenv("SQL_PASSWORD", "seminario_sesion6_2025")
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

# Usuario Endpoints
@app.route(route="usuarios", methods=["GET", "POST"])
def manage_usuarios(req: func.HttpRequest) -> func.HttpResponse:
    try:
        session = SessionLocal()
        
        if req.method == "GET":
            usuarios = session.query(Usuario).all()
            return func.HttpResponse(
                json.dumps([to_dict(usuario) for usuario in usuarios]),
                mimetype="application/json"
            )
        
        elif req.method == "POST":
            usuario_data = req.get_json()
            nuevo_usuario = Usuario(**usuario_data)
            session.add(nuevo_usuario)
            session.commit()
            return func.HttpResponse(
                json.dumps(to_dict(nuevo_usuario)), 
                mimetype="application/json", 
                status_code=201
            )
    
    except SQLAlchemyError as e:
        logging.error(f"Error de base de datos: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Error de base de datos"}), 
            mimetype="application/json", 
            status_code=500
        )
    finally:
        session.close()

@app.route(route="usuarios/{usuario_id}", methods=["GET", "PUT", "DELETE"])
def manage_usuario_by_id(req: func.HttpRequest) -> func.HttpResponse:
    try:
        session = SessionLocal()
        usuario_id = int(req.route_params.get('usuario_id'))
        
        if req.method == "GET":
            usuario = session.query(Usuario).filter(Usuario.id == usuario_id).first()
            if usuario:
                return func.HttpResponse(
                    json.dumps(to_dict(usuario)),
                    mimetype="application/json"
                )
            return func.HttpResponse("Usuario no encontrado", status_code=404)
        
        elif req.method == "PUT":
            usuario = session.query(Usuario).filter(Usuario.id == usuario_id).first()
            if usuario:
                usuario_data = req.get_json()
                for key, value in usuario_data.items():
                    setattr(usuario, key, value)
                session.commit()
                return func.HttpResponse(
                    json.dumps(to_dict(usuario)), 
                    mimetype="application/json"
                )
            return func.HttpResponse("Usuario no encontrado", status_code=404)
        
        elif req.method == "DELETE":
            usuario = session.query(Usuario).filter(Usuario.id == usuario_id).first()
            if usuario:
                session.delete(usuario)
                session.commit()
                return func.HttpResponse("Usuario eliminado", status_code=204)
            return func.HttpResponse("Usuario no encontrado", status_code=404)
    
    except SQLAlchemyError as e:
        logging.error(f"Error de base de datos: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Error de base de datos"}), 
            mimetype="application/json", 
            status_code=500
        )
    finally:
        session.close()

# Destino Endpoints
@app.route(route="destinos", methods=["GET", "POST"])
def manage_destinos(req: func.HttpRequest) -> func.HttpResponse:
    try:
        session = SessionLocal()
        
        if req.method == "GET":
            destinos = session.query(Destino).all()
            return func.HttpResponse(
                json.dumps([to_dict(destino) for destino in destinos]),
                mimetype="application/json"
            )
        
        elif req.method == "POST":
            destino_data = req.get_json()
            nuevo_destino = Destino(**destino_data)
            session.add(nuevo_destino)
            session.commit()
            return func.HttpResponse(
                json.dumps(to_dict(nuevo_destino)), 
                mimetype="application/json", 
                status_code=201
            )
    
    except SQLAlchemyError as e:
        logging.error(f"Error de base de datos: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Error de base de datos"}), 
            mimetype="application/json", 
            status_code=500
        )
    finally:
        session.close()

@app.route(route="destinos/{destino_id}", methods=["GET", "PUT", "DELETE"])
def manage_destino_by_id(req: func.HttpRequest) -> func.HttpResponse:
    try:
        session = SessionLocal()
        destino_id = int(req.route_params.get('destino_id'))
        
        if req.method == "GET":
            destino = session.query(Destino).filter(Destino.id == destino_id).first()
            if destino:
                return func.HttpResponse(
                    json.dumps(to_dict(destino)),
                    mimetype="application/json"
                )
            return func.HttpResponse("Destino no encontrado", status_code=404)
        
        elif req.method == "PUT":
            destino = session.query(Destino).filter(Destino.id == destino_id).first()
            if destino:
                destino_data = req.get_json()
                for key, value in destino_data.items():
                    setattr(destino, key, value)
                session.commit()
                return func.HttpResponse(
                    json.dumps(to_dict(destino)), 
                    mimetype="application/json"
                )
            return func.HttpResponse("Destino no encontrado", status_code=404)
        
        elif req.method == "DELETE":
            destino = session.query(Destino).filter(Destino.id == destino_id).first()
            if destino:
                session.delete(destino)
                session.commit()
                return func.HttpResponse(
                    json.dumps({"message": "Destino eliminado exitosamente"}), 
                    mimetype="application/json", 
                    status_code=200
                )
            return func.HttpResponse("Destino no encontrado", status_code=404)

    
    except SQLAlchemyError as e:
        logging.error(f"Error de base de datos: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Error de base de datos"}), 
            mimetype="application/json", 
            status_code=500
        )
    finally:
        session.close()

# Reserva Endpoints
def to_dict(obj):
    """
    Convierte un objeto SQLAlchemy a un diccionario, 
    manejando conversión de fechas, relaciones y objetos datetime
    """
    from datetime import datetime
    
    # Si el objeto es None, devuelve None
    if obj is None:
        return None
    
    # Convierte el objeto a un diccionario
    dict_obj = {c.name: getattr(obj, c.name) for c in obj.__table__.columns}
    
    # Convierte datetime a string ISO format
    for key, value in list(dict_obj.items()):
        if isinstance(value, datetime):
            dict_obj[key] = value.isoformat()
        # Convierte objetos None a null
        elif value is None:
            dict_obj[key] = None
    
    return dict_obj

@app.route(route="reservas", methods=["GET", "POST"])
def manage_reservas(req: func.HttpRequest) -> func.HttpResponse:
    try:
        session = SessionLocal()
        
        if req.method == "GET":
            reservas = session.query(Reserva).all()
            return func.HttpResponse(
                json.dumps([to_dict(reserva) for reserva in reservas]),
                mimetype="application/json"
            )
        
        elif req.method == "POST":
            # Obtener datos de la solicitud
            reserva_data = req.get_json()
            
            # Obtener los nombres de columnas del modelo Reserva
            columnas_validas = [c.name for c in Reserva.__table__.columns]
            
            # Filtrar solo los datos válidos
            datos_filtrados = {
                key: value for key, value in reserva_data.items() 
                if key in columnas_validas
            }
            
            # Manejar conversión de fecha si está presente
            if 'fecha' in datos_filtrados:
                try:
                    from datetime import datetime
                    datos_filtrados['fecha'] = datetime.fromisoformat(datos_filtrados['fecha'])
                except (ValueError, TypeError):
                    return func.HttpResponse(
                        json.dumps({"error": "Formato de fecha inválido"}),
                        mimetype="application/json",
                        status_code=400
                    )
            
            # Crear nueva reserva solo con datos válidos
            nueva_reserva = Reserva(**datos_filtrados)
            session.add(nueva_reserva)
            session.commit()
            
            return func.HttpResponse(
                json.dumps(to_dict(nueva_reserva)),
                mimetype="application/json",
                status_code=201
            )
    
    except SQLAlchemyError as e:
        logging.error(f"Error de base de datos: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Error de base de datos", "detalle": str(e)}),
            mimetype="application/json",
            status_code=500
        )
    finally:
        session.close()

@app.route(route="reservas/{reserva_id}", methods=["GET", "PUT", "DELETE"])
def manage_reserva_by_id(req: func.HttpRequest) -> func.HttpResponse:
    try:
        session = SessionLocal()
        reserva_id = int(req.route_params.get('reserva_id'))

        if req.method == "GET":
            # Obtener reserva por ID
            reserva = session.query(Reserva).filter(Reserva.id == reserva_id).first()
            
            if reserva:
                return func.HttpResponse(
                    json.dumps(to_dict(reserva)),
                    mimetype="application/json"
                )
            
            return func.HttpResponse(
                json.dumps({"error": "Reserva no encontrada"}),
                mimetype="application/json",
                status_code=404
            )

        elif req.method == "PUT":
            # Buscar la reserva existente
            reserva = session.query(Reserva).filter(Reserva.id == reserva_id).first()
            
            if not reserva:
                return func.HttpResponse(
                    json.dumps({"error": "Reserva no encontrada"}),
                    mimetype="application/json",
                    status_code=404
                )

            # Obtener datos de la solicitud
            reserva_data = req.get_json()
            
            # Obtener columnas válidas
            columnas_validas = [c.name for c in Reserva.__table__.columns]
            
            # Filtrar datos válidos
            datos_filtrados = {
                key: value for key, value in reserva_data.items() 
                if key in columnas_validas
            }
            
            # Manejar conversión de fecha si está presente
            if 'fecha' in datos_filtrados:
                try:
                    from datetime import datetime
                    datos_filtrados['fecha'] = datetime.fromisoformat(datos_filtrados['fecha'])
                except (ValueError, TypeError):
                    return func.HttpResponse(
                        json.dumps({"error": "Formato de fecha inválido"}),
                        mimetype="application/json",
                        status_code=400
                    )
            
            # Actualizar la reserva
            for key, value in datos_filtrados.items():
                setattr(reserva, key, value)
            
            session.commit()
            
            return func.HttpResponse(
                json.dumps(to_dict(reserva)),
                mimetype="application/json"
            )

        elif req.method == "DELETE":
            # Buscar la reserva
            reserva = session.query(Reserva).filter(Reserva.id == reserva_id).first()
            
            if not reserva:
                return func.HttpResponse(
                    json.dumps({"error": "Reserva no encontrada"}),
                    mimetype="application/json",
                    status_code=404
                )
            
            # Eliminar la reserva
            session.delete(reserva)
            session.commit()
            
            return func.HttpResponse(
                json.dumps({"message": "Reserva eliminada correctamente"}),
                mimetype="application/json",
                status_code=200
            )

    except ValueError:
        return func.HttpResponse(
            json.dumps({"error": "ID de reserva inválido"}),
            mimetype="application/json",
            status_code=400
        )
    
    except SQLAlchemyError as e:
        logging.error(f"Error de base de datos: {str(e)}")
        session.rollback()
        return func.HttpResponse(
            json.dumps({"error": "Error de base de datos", "detalle": str(e)}),
            mimetype="application/json",
            status_code=500
        )
    
    finally:
        session.close()
# Guia Endpoints
@app.route(route="guias", methods=["GET", "POST"])
def manage_guias(req: func.HttpRequest) -> func.HttpResponse:
    try:
        session = SessionLocal()
        
        if req.method == "GET":
            guias = session.query(Guia).all()
            return func.HttpResponse(
                json.dumps([to_dict(guia) for guia in guias], default=str),
                mimetype="application/json"
            )
        
        elif req.method == "POST":
            guia_data = req.get_json()

            # Validar que f_nacimiento esté presente y tenga un valor válido
            if "f_nacimiento" not in guia_data or not guia_data["f_nacimiento"]:
                return func.HttpResponse(
                    json.dumps({"error": "El campo 'f_nacimiento' es obligatorio."}),
                    mimetype="application/json",
                    status_code=400
                )

            # Convertir la fecha a un objeto datetime
            try:
                guia_data["f_nacimiento"] = datetime.strptime(guia_data["f_nacimiento"], "%Y-%m-%d")
            except ValueError:
                return func.HttpResponse(
                    json.dumps({"error": "Formato de fecha incorrecto. Usa 'YYYY-MM-DD'."}),
                    mimetype="application/json",
                    status_code=400
                )

            nuevo_guia = Guia(**guia_data)
            session.add(nuevo_guia)
            session.commit()
            return func.HttpResponse(
                json.dumps(to_dict(nuevo_guia), default=str)
, 
                mimetype="application/json", 
                status_code=201
            )
    
    except SQLAlchemyError as e:
        logging.error(f"Error de base de datos: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Error de base de datos"}), 
            mimetype="application/json", 
            status_code=500
        )
    finally:
        session.close()

@app.route(route="guias/{guia_id}", methods=["GET", "PUT", "DELETE"])
def manage_guia_by_id(req: func.HttpRequest) -> func.HttpResponse:
    try:
        session = SessionLocal()
        guia_id = int(req.route_params.get('guia_id'))
        
        if req.method == "GET":
            guia = session.query(Guia).filter(Guia.id == guia_id).first()
            if guia:
                return func.HttpResponse(
                    json.dumps(to_dict(guia), default=str),
                    mimetype="application/json"
                )
            return func.HttpResponse("Guia no encontrado", status_code=404)
        
        elif req.method == "PUT":
            guia = session.query(Guia).filter(Guia.id == guia_id).first()
            if guia:
                guia_data = req.get_json()
                for key, value in guia_data.items():
                    setattr(guia, key, value)
                session.commit()
                return func.HttpResponse(
                    json.dumps(to_dict(guia), default=str), 
                    mimetype="application/json"
                )
            return func.HttpResponse("Guia no encontrado", status_code=404)
        
        elif req.method == "DELETE":
            guia = session.query(Guia).filter(Guia.id == guia_id).first()
            if guia:
                session.delete(guia)
                session.commit()
                return func.HttpResponse("Guia eliminado", status_code=204)
            return func.HttpResponse("Guia no encontrado", status_code=404)
    
    except SQLAlchemyError as e:
        logging.error(f"Error de base de datos: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Error de base de datos"}), 
            mimetype="application/json", 
            status_code=500
        )
    finally:
        session.close()

# Genero Endpoints
@app.route(route="generos", methods=["GET", "POST"])
def manage_generos(req: func.HttpRequest) -> func.HttpResponse:
    try:
        session = SessionLocal()
        
        if req.method == "GET":
            generos = session.query(Genero).all()
            return func.HttpResponse(
                json.dumps([to_dict(genero) for genero in generos]),
                mimetype="application/json"
            )
        
        elif req.method == "POST":
            genero_data = req.get_json()
            nuevo_genero = Genero(**genero_data)
            session.add(nuevo_genero)
            session.commit()
            return func.HttpResponse(
                json.dumps(to_dict(nuevo_genero)), 
                mimetype="application/json", 
                status_code=201
            )
    
    except SQLAlchemyError as e:
        logging.error(f"Error de base de datos: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Error de base de datos"}), 
            mimetype="application/json", 
            status_code=500
        )
    finally:
        session.close()

@app.route(route="generos/{genero_id}", methods=["GET", "PUT", "DELETE"])
def manage_genero_by_id(req: func.HttpRequest) -> func.HttpResponse:
    try:
        session = SessionLocal()
        genero_id = int(req.route_params.get('genero_id'))
        
        if req.method == "GET":
            genero = session.query(Genero).filter(Genero.id == genero_id).first()
            if genero:
                return func.HttpResponse(
                    json.dumps(to_dict(genero)),
                    mimetype="application/json"
                )
            return func.HttpResponse("Genero no encontrado", status_code=404)
        
        elif req.method == "PUT":
            genero = session.query(Genero).filter(Genero.id == genero_id).first()
            if genero:
                genero_data = req.get_json()
                for key, value in genero_data.items():
                    setattr(genero, key, value)
                session.commit()
                return func.HttpResponse(
                    json.dumps(to_dict(genero)), 
                    mimetype="application/json"
                )
            return func.HttpResponse(
                json.dumps({"error": "Género no encontrado"}), 
                mimetype="application/json", 
                status_code=404
            )
        
        elif req.method == "DELETE":
            genero = session.query(Genero).filter(Genero.id == genero_id).first()
            if genero:
                session.delete(genero)
                session.commit()
                return func.HttpResponse(
                    json.dumps({"message": "Genero eliminado correctamente"}), 
                    mimetype="application/json", 
                    status_code=200
                )
            return func.HttpResponse(
                json.dumps({"error": "Genero no encontrado"}), 
                mimetype="application/json", 
                status_code=404
            )

    
    except SQLAlchemyError as e:
        logging.error(f"Error de base de datos: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Error de base de datos"}), 
            mimetype="application/json", 
            status_code=500
        )
    finally:
        session.close()

# Pais Endpoints
@app.route(route="paises", methods=["GET", "POST"])
def manage_paises(req: func.HttpRequest) -> func.HttpResponse:
    try:
        session = SessionLocal()
        
        if req.method == "GET":
            paises = session.query(Pais).all()
            return func.HttpResponse(
                json.dumps([to_dict(pais) for pais in paises]),
                mimetype="application/json"
            )
        
        elif req.method == "POST":
            pais_data = req.get_json()
            nuevo_pais = Pais(**pais_data)
            session.add(nuevo_pais)
            session.commit()
            return func.HttpResponse(
                json.dumps(to_dict(nuevo_pais)), 
                mimetype="application/json", 
                status_code=201
            )
    
    except SQLAlchemyError as e:
        logging.error(f"Error de base de datos: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Error de base de datos"}), 
            mimetype="application/json", 
            status_code=500
        )
    finally:
        session.close()

@app.route(route="paises/{pais_id}", methods=["GET", "PUT", "DELETE"])
def manage_pais_by_id(req: func.HttpRequest) -> func.HttpResponse:
    try:
        session = SessionLocal()
        pais_id = int(req.route_params.get('pais_id'))
        
        if req.method == "GET":
            pais = session.query(Pais).filter(Pais.id == pais_id).first()
            if pais:
                return func.HttpResponse(
                    json.dumps(to_dict(pais)),
                    mimetype="application/json"
                )
            return func.HttpResponse("Pais no encontrado", status_code=404)
        
        elif req.method == "PUT":
            pais = session.query(Pais).filter(Pais.id == pais_id).first()
            if pais:
                pais_data = req.get_json()
                for key, value in pais_data.items():
                    setattr(pais, key, value)
                session.commit()
                return func.HttpResponse(
                    json.dumps(to_dict(pais)), 
                    mimetype="application/json"
                )
            return func.HttpResponse("Pais no encontrado", status_code=404)
        
        elif req.method == "DELETE":
            pais = session.query(Pais).filter(Pais.id == pais_id).first()
            if pais:
                session.delete(pais)
                session.commit()
                return func.HttpResponse("Pais eliminado", status_code=204)
            return func.HttpResponse("Pais no encontrado", status_code=404)
    
    except SQLAlchemyError as e:
        logging.error(f"Error de base de datos: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Error de base de datos"}), 
            mimetype="application/json", 
            status_code=500
        )
    finally:
        session.close()

# Ciudad Endpoints
@app.route(route="ciudades", methods=["GET", "POST"])
def manage_ciudades(req: func.HttpRequest) -> func.HttpResponse:
    try:
        session = SessionLocal()
        
        if req.method == "GET":
            ciudades = session.query(Ciudad).all()
            return func.HttpResponse(
                json.dumps([to_dict(ciudad) for ciudad in ciudades]),
                mimetype="application/json"
            )
        
        elif req.method == "POST":
            try:
                ciudad_data = req.get_json()
                
                # Verificar que el JSON incluye 'pais_id'
                if "pais_id" not in ciudad_data or not ciudad_data["pais_id"]:
                    return func.HttpResponse(
                        json.dumps({"error": "El campo 'pais_id' es obligatorio"}), 
                        mimetype="application/json", 
                        status_code=400
                    )

                # Verificar que el 'pais_id' existe en la base de datos
                pais_existente = session.query(Pais).filter(Pais.id == ciudad_data["pais_id"]).first()
                if not pais_existente:
                    return func.HttpResponse(
                        json.dumps({"error": "El 'pais_id' proporcionado no existe"}), 
                        mimetype="application/json", 
                        status_code=400
                    )

                # Crear la ciudad con los datos validados
                nueva_ciudad = Ciudad(**ciudad_data)
                session.add(nueva_ciudad)
                session.commit()

                return func.HttpResponse(
                    json.dumps(to_dict(nueva_ciudad)), 
                    mimetype="application/json", 
                    status_code=201
                )

            except SQLAlchemyError as e:
                session.rollback()  # Revertir cambios si hay error
                logging.error(f"Error de base de datos: {str(e)}")
                return func.HttpResponse(
                    json.dumps({"error": "Error de base de datos"}), 
                    mimetype="application/json", 
                    status_code=500
                )

    
    except SQLAlchemyError as e:
        logging.error(f"Error de base de datos: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Error de base de datos"}), 
            mimetype="application/json", 
            status_code=500
        )
    finally:
        session.close()

@app.route(route="ciudades/{ciudad_id}", methods=["GET", "PUT", "DELETE"])
def manage_ciudad_by_id(req: func.HttpRequest) -> func.HttpResponse:
    try:
        session = SessionLocal()
        ciudad_id = int(req.route_params.get('ciudad_id'))
        
        if req.method == "GET":
            ciudad = session.query(Ciudad).filter(Ciudad.id == ciudad_id).first()
            if ciudad:
                return func.HttpResponse(
                    json.dumps(to_dict(ciudad)),
                    mimetype="application/json"
                )
            return func.HttpResponse("Ciudad no encontrada", status_code=404)
        
        elif req.method == "PUT":
            ciudad = session.query(Ciudad).filter(Ciudad.id == ciudad_id).first()
            if ciudad:
                ciudad_data = req.get_json()
                for key, value in ciudad_data.items():
                    setattr(ciudad, key, value)
                session.commit()
                return func.HttpResponse(
                    json.dumps(to_dict(ciudad)), 
                    mimetype="application/json"
                )
            return func.HttpResponse("Ciudad no encontrada", status_code=404)
        
        elif req.method == "DELETE":
            ciudad = session.query(Ciudad).filter(Ciudad.id == ciudad_id).first()
            if ciudad:
                session.delete(ciudad)
                session.commit()
                return func.HttpResponse("Ciudad eliminada", status_code=204)
            return func.HttpResponse("Ciudad no encontrada", status_code=404)
    
    except SQLAlchemyError as e:
        logging.error(f"Error de base de datos: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Error de base de datos"}), 
            mimetype="application/json", 
            status_code=500
        )
    finally:
        session.close()