import azure.functions as func
import logging
import json
import pyodbc
import os
from sqlalchemy.ext.declarative import declarative_base
app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

import urllib.parse
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from src.models.user import User

# Configuración de la conexión a Azure SQL Database desde variables de entorno
server = os.getenv("SQL_SERVER", "sem6.database.windows.net")
database = os.getenv("SQL_DATABASE", "db_tourismo")
username = os.getenv("SQL_USERNAME", "admin2025")
password = os.getenv("SQL_PASSWORD", "seminario_sesion6_2025")
# Codificar la contraseña para la URL
encoded_password = urllib.parse.quote_plus(password)

# URL de conexión para SQLAlchemy con formato específico para Azure SQL
DB_URL = f"mssql+pyodbc://{username}:{encoded_password}@{server}/{database}?driver=ODBC+Driver+18+for+SQL+Server&Encrypt=yes&TrustServerCertificate=no&Connection Timeout=30"

# Crear motor con SQLAlchemy
engine = create_engine(DB_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Función para obtener una sesión de base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db  
    finally:
        db.close() 
        
# Función auxiliar para convertir filas a diccionarios
def rows_to_dict_list(cursor, rows):
    return [dict(zip([column[0] for column in cursor.description], row)) for row in rows]


###############################################
# CRUD para la tabla Users
###############################################

@app.route(route="test-db", methods=["GET"])
def test_db(req: func.HttpRequest) -> func.HttpResponse:
    try:
        db = SessionLocal()
        result = db.execute(text("SELECT DB_NAME()")).fetchone()
        db.close()
        return func.HttpResponse(json.dumps({"connected_to": result[0]}), mimetype="application/json", status_code=200)
    except Exception as e:
        return func.HttpResponse(json.dumps({"error": str(e)}), mimetype="application/json", status_code=500)

@app.route(route="get-tables", methods=["GET"])
def get_tables(req: func.HttpRequest) -> func.HttpResponse:
    try:
        db = SessionLocal()
        result = db.execute(text("""
            SELECT TABLE_SCHEMA + '.' + TABLE_NAME AS full_table_name 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_TYPE = 'BASE TABLE'
        """)).fetchall()
        db.close()
        
        # Convertir resultado a JSON
        tables = [{"table_name": row[0]} for row in result]
        return func.HttpResponse(json.dumps(tables), mimetype="application/json", status_code=200)

    except Exception as e:
        return func.HttpResponse(json.dumps({"error": str(e)}), mimetype="application/json", status_code=500)

@app.route(route="users", methods=["GET"])
def get_users(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Fetching users from database.")
    
    try:
        db: Session = SessionLocal()
        
        # Verifica si la tabla existe
        result = db.execute(text("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'Users'"))
        print(result)
        print("iniciando debug")
        table_exists = result.fetchall()
        print(table_exists)
        if not table_exists:
            return func.HttpResponse("Table 'users' does not exist in the database.", status_code=404)
        
        # Si la tabla existe, intenta consultar la tabla con el esquema correcto
        users = db.query(User).all()
        db.close()
        
        users_list = [user.to_dict() for user in users]
        
        return func.HttpResponse(json.dumps(users_list, default=str), mimetype="application/json")
    
    except Exception as e:
        logging.error(str(e))
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)

@app.route(route="users/{id}", methods=["GET"])
def get_user_by_id(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Fetching user by ID")
    try:
        # Obtener el ID de la ruta
        id = int(req.route_params.get('id'))
        
        db: Session = SessionLocal()
        user = db.query(User).filter(User.id == id).first()
        
        if user:
            return func.HttpResponse(json.dumps(user.to_dict(), default=str), mimetype="application/json")
        else:
            return func.HttpResponse("User not found", status_code=404)
    except Exception as e:
        logging.error(str(e))
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)
    finally:
        db.close()

@app.route(route="users", methods=["POST"])
def create_user(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Creating a new user.")
    db: Session = SessionLocal()
    try:
        req_body = req.get_json()
        name = req_body.get("name")
        email = req_body.get("email")
        password_hash = req_body.get("password_hash")
        phone = req_body.get("phone")
        
        # Check if email already exists
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            return func.HttpResponse(
                json.dumps({"error": "User with this email already exists"}),
                status_code=409,  # Conflict status code
                mimetype="application/json"
            )
        
        # Create new user with SQLAlchemy
        new_user = User(
            name=name,
            email=email,
            password_hash=password_hash,
            phone=phone
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return func.HttpResponse(
            json.dumps({"id": new_user.id, "status": "succes"}, default=str),
            status_code=201,
            mimetype="application/json"
        )
    
    except Exception as e:
        db.rollback()
        logging.error(str(e))
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)
    
    finally:
        db.close()
    
@app.route(route="users/update", methods=["PUT"])
def update_user(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Updating user")
    db: Session = SessionLocal()
    
    try:
        # Obtener datos de la solicitud
        req_body = req.get_json()
        id = req_body.get("id")  # Obtener el ID desde el cuerpo
        name = req_body.get("name")
        email = req_body.get("email")
        password_hash = req_body.get("password_hash")
        phone = req_body.get("phone")
        
        if not id:
            return func.HttpResponse(
                json.dumps({"error": "ID is required"}), 
                status_code=400, 
                mimetype="application/json"
            )

        # Buscar usuario con SQLAlchemy
        user = db.query(User).filter(User.id == id).first()
        
        if not user:
            return func.HttpResponse(
                json.dumps({"error": "User not found"}), 
                status_code=404, 
                mimetype="application/json"
            )
        
        # Actualizar los campos si existen en la solicitud
        if name:
            user.name = name
        if email:
            user.email = email
        if password_hash:
            user.password_hash = password_hash
        if phone:
            user.phone = phone
        
        db.commit()
        
        return func.HttpResponse(
            json.dumps({"message": "User updated successfully"}), 
            status_code=200, 
            mimetype="application/json"
        )
    
    except Exception as e:
        db.rollback()
        logging.error(str(e))
        return func.HttpResponse(
            json.dumps({"error": str(e)}), 
            status_code=500, 
            mimetype="application/json"
        )
    
    finally:
        db.close()

@app.route(route="users/{id}", methods=["DELETE"])
def delete_user(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Deleting user")
    db: Session = SessionLocal()
    try:
        id = int(req.route_params.get('id'))
        
        # Buscar y eliminar usuario con SQLAlchemy
        user = db.query(User).filter(User.id == id).first()
        
        if not user:
            return func.HttpResponse("User not found", status_code=404)
        
        db.delete(user)
        db.commit()
        
        return func.HttpResponse("User deleted successfully", status_code=200)
    except Exception as e:
        db.rollback()
        logging.error(str(e))
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)
    finally:
        db.close()

###############################################
# CRUD para la tabla Destinations
###############################################

@app.route(route="destinations", methods=["GET"])
def get_destinations(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Fetching destinations from database.")
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Destinations")
        destinations = rows_to_dict_list(cursor, cursor.fetchall())
        conn.close()
        return func.HttpResponse(json.dumps(destinations, default=str), mimetype="application/json")
    except Exception as e:
        logging.error(str(e))
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)

@app.route(route="destinations/{id}", methods=["GET"])
def get_destination_by_id(req: func.HttpRequest) -> func.HttpResponse:
    try:
        id = int(req.route_params.get('id'))
        logging.info(f"Fetching destination with ID: {id}")
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Destinations WHERE id = ?", (id,))
        destination = cursor.fetchone()
        if destination:
            destination_dict = dict(zip([column[0] for column in cursor.description], destination))
            conn.close()
            return func.HttpResponse(json.dumps(destination_dict, default=str), mimetype="application/json")
        else:
            conn.close()
            return func.HttpResponse("Destination not found", status_code=404)
    except Exception as e:
        logging.error(str(e))
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)

@app.route(route="destinations", methods=["POST"])
def create_destination(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Creating a new destination.")
    try:
        req_body = req.get_json()
        name = req_body.get("name")
        country = req_body.get("country")
        city = req_body.get("city")
        description = req_body.get("description")
        image_url = req_body.get("image_url")
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Destinations (name, country, city, description, image_url) VALUES (?, ?, ?, ?, ?)",
                      (name, country, city, description, image_url))
        conn.commit()
        
        # Obtener el ID generado
        cursor.execute("SELECT @@IDENTITY AS ID")
        destination_id = cursor.fetchone()[0]
        conn.close()
        
        return func.HttpResponse(json.dumps({"id": destination_id}), status_code=201, mimetype="application/json")
    except Exception as e:
        logging.error(str(e))
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)

@app.route(route="destinations/{id}", methods=["PUT"])
def update_destination(req: func.HttpRequest) -> func.HttpResponse:
    try:
        id = int(req.route_params.get('id'))
        logging.info(f"Updating destination with ID: {id}")
        
        req_body = req.get_json()
        name = req_body.get("name")
        country = req_body.get("country")
        city = req_body.get("city")
        description = req_body.get("description")
        image_url = req_body.get("image_url")
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE Destinations SET name = ?, country = ?, city = ?, description = ?, image_url = ? WHERE id = ?",
                      (name, country, city, description, image_url, id))
        conn.commit()
        
        if cursor.rowcount == 0:
            conn.close()
            return func.HttpResponse("Destination not found", status_code=404)
        
        conn.close()
        return func.HttpResponse("Destination updated successfully", status_code=200)
    except Exception as e:
        logging.error(str(e))
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)

@app.route(route="destinations/{id}", methods=["DELETE"])
def delete_destination(req: func.HttpRequest) -> func.HttpResponse:
    try:
        id = int(req.route_params.get('id'))
        logging.info(f"Deleting destination with ID: {id}")
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Destinations WHERE id = ?", (id,))
        conn.commit()
        
        if cursor.rowcount == 0:
            conn.close()
            return func.HttpResponse("Destination not found", status_code=404)
        
        conn.close()
        return func.HttpResponse("Destination deleted successfully", status_code=200)
    except Exception as e:
        logging.error(str(e))
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)

###############################################
# CRUD para la tabla Trips
###############################################

@app.route(route="trips", methods=["GET"])
def get_trips(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Fetching trips from database.")
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Trips")
        trips = rows_to_dict_list(cursor, cursor.fetchall())
        conn.close()
        return func.HttpResponse(json.dumps(trips, default=str), mimetype="application/json")
    except Exception as e:
        logging.error(str(e))
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)

@app.route(route="trips/{id}", methods=["GET"])
def get_trip_by_id(req: func.HttpRequest) -> func.HttpResponse:
    try:
        id = int(req.route_params.get('id'))
        logging.info(f"Fetching trip with ID: {id}")
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Trips WHERE id = ?", (id,))
        trip = cursor.fetchone()
        if trip:
            trip_dict = dict(zip([column[0] for column in cursor.description], trip))
            conn.close()
            return func.HttpResponse(json.dumps(trip_dict, default=str), mimetype="application/json")
        else:
            conn.close()
            return func.HttpResponse("Trip not found", status_code=404)
    except Exception as e:
        logging.error(str(e))
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)

@app.route(route="trips", methods=["POST"])
def create_trip(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Creating a new trip.")
    try:
        req_body = req.get_json()
        destination_id = req_body.get("destination_id")
        user_id = req_body.get("user_id")
        start_date = req_body.get("start_date")
        end_date = req_body.get("end_date")
        total_cost = req_body.get("total_cost")
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Trips (destination_id, user_id, start_date, end_date, total_cost) VALUES (?, ?, ?, ?, ?)",
                      (destination_id, user_id, start_date, end_date, total_cost))
        conn.commit()
        
        # Obtener el ID generado
        cursor.execute("SELECT @@IDENTITY AS ID")
        trip_id = cursor.fetchone()[0]
        conn.close()
        
        return func.HttpResponse(json.dumps({"id": trip_id}), status_code=201, mimetype="application/json")
    except Exception as e:
        logging.error(str(e))
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)

@app.route(route="trips/{id}", methods=["PUT"])
def update_trip(req: func.HttpRequest) -> func.HttpResponse:
    try:
        id = int(req.route_params.get('id'))
        logging.info(f"Updating trip with ID: {id}")
        
        req_body = req.get_json()
        destination_id = req_body.get("destination_id")
        user_id = req_body.get("user_id")
        start_date = req_body.get("start_date")
        end_date = req_body.get("end_date")
        total_cost = req_body.get("total_cost")
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE Trips SET destination_id = ?, user_id = ?, start_date = ?, end_date = ?, total_cost = ? WHERE id = ?",
                      (destination_id, user_id, start_date, end_date, total_cost, id))
        conn.commit()
        
        if cursor.rowcount == 0:
            conn.close()
            return func.HttpResponse("Trip not found", status_code=404)
        
        conn.close()
        return func.HttpResponse("Trip updated successfully", status_code=200)
    except Exception as e:
        logging.error(str(e))
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)

@app.route(route="trips/{id}", methods=["DELETE"])
def delete_trip(req: func.HttpRequest) -> func.HttpResponse:
    try:
        id = int(req.route_params.get('id'))
        logging.info(f"Deleting trip with ID: {id}")
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Trips WHERE id = ?", (id,))
        conn.commit()
        
        if cursor.rowcount == 0:
            conn.close()
            return func.HttpResponse("Trip not found", status_code=404)
        
        conn.close()
        return func.HttpResponse("Trip deleted successfully", status_code=200)
    except Exception as e:
        logging.error(str(e))
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)

###############################################
# CRUD para la tabla Bookings
###############################################

@app.route(route="bookings", methods=["GET"])
def get_bookings(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Fetching bookings from database.")
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Bookings")
        bookings = rows_to_dict_list(cursor, cursor.fetchall())
        conn.close()
        return func.HttpResponse(json.dumps(bookings, default=str), mimetype="application/json")
    except Exception as e:
        logging.error(str(e))
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)

@app.route(route="bookings/{id}", methods=["GET"])
def get_booking_by_id(req: func.HttpRequest) -> func.HttpResponse:
    try:
        id = int(req.route_params.get('id'))
        logging.info(f"Fetching booking with ID: {id}")
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Bookings WHERE id = ?", (id,))
        booking = cursor.fetchone()
        if booking:
            booking_dict = dict(zip([column[0] for column in cursor.description], booking))
            conn.close()
            return func.HttpResponse(json.dumps(booking_dict, default=str), mimetype="application/json")
        else:
            conn.close()
            return func.HttpResponse("Booking not found", status_code=404)
    except Exception as e:
        logging.error(str(e))
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)

@app.route(route="bookings", methods=["POST"])
def create_booking(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Creating a new booking.")
    try:
        req_body = req.get_json()
        user_id = req_body.get("user_id")
        trip_id = req_body.get("trip_id")
        status = req_body.get("status")
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Bookings (user_id, trip_id, status) VALUES (?, ?, ?)",
                      (user_id, trip_id, status))
        conn.commit()
        
        # Obtener el ID generado
        cursor.execute("SELECT @@IDENTITY AS ID")
        booking_id = cursor.fetchone()[0]
        conn.close()
        
        return func.HttpResponse(json.dumps({"id": booking_id}), status_code=201, mimetype="application/json")
    except Exception as e:
        logging.error(str(e))
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)

@app.route(route="bookings/{id}", methods=["PUT"])
def update_booking(req: func.HttpRequest) -> func.HttpResponse:
    try:
        # Obtener el ID desde los parámetros de ruta
        id = req.route_params.get('id')
        booking_id = int(id)
        logging.info(f"Updating booking with ID: {booking_id}")
        
        req_body = req.get_json()
        user_id = req_body.get("user_id")
        trip_id = req_body.get("trip_id")
        status = req_body.get("status")
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE Bookings SET user_id = ?, trip_id = ?, status = ? WHERE id = ?",
                      (user_id, trip_id, status, booking_id))
        conn.commit()
        
        if cursor.rowcount == 0:
            conn.close()
            return func.HttpResponse("Booking not found", status_code=404)
        
        conn.close()
        return func.HttpResponse("Booking updated successfully", status_code=200)
    except ValueError:
        return func.HttpResponse("Invalid booking ID format", status_code=400)
    except Exception as e:
        logging.error(str(e))
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)

@app.route(route="bookings/{id}", methods=["DELETE"])
def delete_booking(req: func.HttpRequest) -> func.HttpResponse:
    try:
        id = req.route_params.get('id')
        booking_id = int(id)
        logging.info(f"Deleting booking with ID: {booking_id}")
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Bookings WHERE id = ?", (booking_id,))
        conn.commit()
        
        if cursor.rowcount == 0:
            conn.close()
            return func.HttpResponse("Booking not found", status_code=404)
        
        conn.close()
        return func.HttpResponse("Booking deleted successfully", status_code=200)
    except ValueError:
        return func.HttpResponse("Invalid booking ID format", status_code=400)
    except Exception as e:
        logging.error(str(e))
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)


@app.route(route="payments/{id}", methods=["GET"])
def get_payment_by_id(req: func.HttpRequest) -> func.HttpResponse:
    try:
        id = req.route_params.get('id')
        payment_id = int(id)
        logging.info(f"Fetching payment with ID: {payment_id}")
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Payments WHERE id = ?", (payment_id,))
        payment = cursor.fetchone()
        if payment:
            payment_dict = dict(zip([column[0] for column in cursor.description], payment))
            conn.close()
            return func.HttpResponse(json.dumps(payment_dict, default=str), mimetype="application/json")
        else:
            conn.close()
            return func.HttpResponse("Payment not found", status_code=404)
    except ValueError:
        return func.HttpResponse("Invalid payment ID format", status_code=400)
    except Exception as e:
        logging.error(str(e))
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)


@app.route(route="payments/{id}", methods=["PUT"])
def update_payment(req: func.HttpRequest) -> func.HttpResponse:
    try:
        id = req.route_params.get('id')
        payment_id = int(id)
        logging.info(f"Updating payment with ID: {payment_id}")
        
        req_body = req.get_json()
        user_id = req_body.get("user_id")
        booking_id = req_body.get("booking_id")
        amount = req_body.get("amount")
        payment_method = req_body.get("payment_method")
        status = req_body.get("status")
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE Payments SET user_id = ?, booking_id = ?, amount = ?, payment_method = ?, status = ? WHERE id = ?",
                      (user_id, booking_id, amount, payment_method, status, payment_id))
        conn.commit()
        
        if cursor.rowcount == 0:
            conn.close()
            return func.HttpResponse("Payment not found", status_code=404)
        
        conn.close()
        return func.HttpResponse("Payment updated successfully", status_code=200)
    except ValueError:
        return func.HttpResponse("Invalid payment ID format", status_code=400)
    except Exception as e:
        logging.error(str(e))
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)


@app.route(route="payments/{id}", methods=["DELETE"])
def delete_payment(req: func.HttpRequest) -> func.HttpResponse:
    try:
        id = req.route_params.get('id')
        payment_id = int(id)
        logging.info(f"Deleting payment with ID: {payment_id}")
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Payments WHERE id = ?", (payment_id,))
        conn.commit()
        
        if cursor.rowcount == 0:
            conn.close()
            return func.HttpResponse("Payment not found", status_code=404)
        
        conn.close()
        return func.HttpResponse("Payment deleted successfully", status_code=200)
    except ValueError:
        return func.HttpResponse("Invalid payment ID format", status_code=400)
    except Exception as e:
        logging.error(str(e))
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)

###############################################
# CRUD para la tabla Reviews
###############################################

@app.route(route="reviews", methods=["GET"])
def get_reviews(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Fetching reviews from database.")
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Reviews")
        reviews = rows_to_dict_list(cursor, cursor.fetchall())
        conn.close()
        return func.HttpResponse(json.dumps(reviews, default=str), mimetype="application/json")
    except Exception as e:
        logging.error(str(e))
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)

@app.route(route="reviews/{id}", methods=["GET"])
def get_review_by_id(req: func.HttpRequest) -> func.HttpResponse:
    try:
        id = req.route_params.get('id')
        review_id = int(id)
        logging.info(f"Fetching review with ID: {review_id}")
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Reviews WHERE id = ?", (review_id,))
        review = cursor.fetchone()
        if review:
            review_dict = dict(zip([column[0] for column in cursor.description], review))
            conn.close()
            return func.HttpResponse(json.dumps(review_dict, default=str), mimetype="application/json")
        else:
            conn.close()
            return func.HttpResponse("Review not found", status_code=404)
    except ValueError:
        return func.HttpResponse("Invalid review ID format", status_code=400)
    except Exception as e:
        logging.error(str(e))
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)

@app.route(route="reviews", methods=["POST"])
def create_review(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Creating a new review.")
    try:
        req_body = req.get_json()
        user_id = req_body.get("user_id")
        destination_id = req_body.get("destination_id")
        comment = req_body.get("comment")
        rating = req_body.get("rating")
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Reviews (user_id, destination_id, comment, rating) VALUES (?, ?, ?, ?)",
                      (user_id, destination_id, comment, rating))
        conn.commit()
        
        # Obtener el ID generado
        cursor.execute("SELECT @@IDENTITY AS ID")
        review_id = cursor.fetchone()[0]
        conn.close()
        
        return func.HttpResponse(json.dumps({"id": review_id}), status_code=201, mimetype="application/json")
    except Exception as e:
        logging.error(str(e))
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)

@app.route(route="reviews/{id}", methods=["PUT"])
def update_review(req: func.HttpRequest) -> func.HttpResponse:
    try:
        id = req.route_params.get('id')
        review_id = int(id)
        logging.info(f"Updating review with ID: {review_id}")
        
        req_body = req.get_json()
        user_id = req_body.get("user_id")
        destination_id = req_body.get("destination_id")
        comment = req_body.get("comment")
        rating = req_body.get("rating")
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE Reviews SET user_id = ?, destination_id = ?, comment = ?, rating = ? WHERE id = ?",
                      (user_id, destination_id, comment, rating, review_id))
        conn.commit()
        
        if cursor.rowcount == 0:
            conn.close()
            return func.HttpResponse("Review not found", status_code=404)
        
        conn.close()
        return func.HttpResponse("Review updated successfully", status_code=200)
    except ValueError:
        return func.HttpResponse("Invalid review ID format", status_code=400)
    except Exception as e:
        logging.error(str(e))
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)

@app.route(route="reviews/{id}", methods=["DELETE"])
def delete_review(req: func.HttpRequest) -> func.HttpResponse:
    try:
        id = req.route_params.get('id')
        review_id = int(id)
        logging.info(f"Deleting review with ID: {review_id}")
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Reviews WHERE id = ?", (review_id,))
        conn.commit()
        
        if cursor.rowcount == 0:
            conn.close()
            return func.HttpResponse("Review not found", status_code=404)
        
        conn.close()
        return func.HttpResponse("Review deleted successfully", status_code=200)
    except ValueError:
        return func.HttpResponse("Invalid review ID format", status_code=400)
    except Exception as e:
        logging.error(str(e))
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)

###############################################
# Endpoints adicionales para consultas específicas
###############################################

@app.route(route="users/{user_id}/trips", methods=["GET"])
def get_trips_by_user(req: func.HttpRequest) -> func.HttpResponse:
    try:
        user_id = req.route_params.get('user_id')
        user_id_int = int(user_id)
        logging.info(f"Fetching trips for user ID: {user_id_int}")
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Trips WHERE user_id = ?", (user_id_int,))
        trips = rows_to_dict_list(cursor, cursor.fetchall())
        conn.close()
        return func.HttpResponse(json.dumps(trips, default=str), mimetype="application/json")
    except ValueError:
        return func.HttpResponse("Invalid user ID format", status_code=400)
    except Exception as e:
        logging.error(str(e))
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)
    
@app.route(route="destinations/{destination_id}/reviews", methods=["GET"])
def get_reviews_by_destination(req: func.HttpRequest) -> func.HttpResponse:
    try:
        destination_id = req.route_params.get('destination_id')
        destination_id_int = int(destination_id)
        logging.info(f"Fetching reviews for destination ID: {destination_id_int}")
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Reviews WHERE destination_id = ?", (destination_id_int,))
        reviews = rows_to_dict_list(cursor, cursor.fetchall())
        conn.close()
        return func.HttpResponse(json.dumps(reviews, default=str), mimetype="application/json")
    except ValueError:
        return func.HttpResponse("Invalid destination ID format", status_code=400)
    except Exception as e:
        logging.error(str(e))
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)

@app.route(route="users/{user_id}/bookings", methods=["GET"])
def get_bookings_by_user(req: func.HttpRequest) -> func.HttpResponse:
    try:
        user_id = req.route_params.get('user_id')
        user_id_int = int(user_id)
        logging.info(f"Fetching bookings for user ID: {user_id_int}")
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Bookings WHERE user_id = ?", (user_id_int,))
        bookings = rows_to_dict_list(cursor, cursor.fetchall())
        conn.close()
        return func.HttpResponse(json.dumps(bookings, default=str), mimetype="application/json")
    except ValueError:
        return func.HttpResponse("Invalid user ID format", status_code=400)
    except Exception as e:
        logging.error(str(e))
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)

@app.route(route="users/{user_id}/payments", methods=["GET"])
def get_payments_by_user(req: func.HttpRequest) -> func.HttpResponse:
    try:
        user_id = req.route_params.get('user_id')
        user_id_int = int(user_id)
        logging.info(f"Fetching payments for user ID: {user_id_int}")
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Payments WHERE user_id = ?", (user_id_int,))
        payments = rows_to_dict_list(cursor, cursor.fetchall())
        conn.close()
        return func.HttpResponse(json.dumps(payments, default=str), mimetype="application/json")
    except ValueError:
        return func.HttpResponse("Invalid user ID format", status_code=400)
    except Exception as e:
        logging.error(str(e))
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)

@app.route(route="bookings/{booking_id}/payment", methods=["GET"])
def get_payment_by_booking(req: func.HttpRequest) -> func.HttpResponse:
    try:
        booking_id = req.route_params.get('booking_id')
        booking_id_int = int(booking_id)
        logging.info(f"Fetching payment for booking ID: {booking_id_int}")
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Payments WHERE booking_id = ?", (booking_id_int,))
        payment = cursor.fetchone()
        if payment:
            payment_dict = dict(zip([column[0] for column in cursor.description], payment))
            conn.close()
            return func.HttpResponse(json.dumps(payment_dict, default=str), mimetype="application/json")
        else:
            conn.close()
            return func.HttpResponse("Payment not found for this booking", status_code=404)
    except ValueError:
        return func.HttpResponse("Invalid booking ID format", status_code=400)
    except Exception as e:
        logging.error(str(e))
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)
    
@app.route(route="trips/search", methods=["GET"])
def search_trips(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Searching trips with filters")
    try:
        # Obtener parámetros de búsqueda
        params = req.params
        destination_id = params.get("destination_id")
        start_date = params.get("start_date")
        end_date = params.get("end_date")
        max_cost = params.get("max_cost")
        
        # Construir consulta dinámica
        query = "SELECT * FROM Trips WHERE 1=1"
        query_params = []
        
        if destination_id:
            query += " AND destination_id = ?"
            query_params.append(destination_id)
        
        if start_date:
            query += " AND start_date >= ?"
            query_params.append(start_date)
        
        if end_date:
            query += " AND end_date <= ?"
            query_params.append(end_date)
        
        if max_cost:
            query += " AND total_cost <= ?"
            query_params.append(max_cost)
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(query, query_params)
        trips = rows_to_dict_list(cursor, cursor.fetchall())
        conn.close()
        
        return func.HttpResponse(json.dumps(trips, default=str), mimetype="application/json")
    except Exception as e:
        logging.error(str(e))
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)

@app.route(route="destinations/search", methods=["GET"])
def search_destinations(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Searching destinations with filters")
    try:
        # Obtener parámetros de búsqueda
        params = req.params
        country = params.get("country")
        city = params.get("city")
        name_contains = params.get("name")
        
        # Construir consulta dinámica
        query = "SELECT * FROM Destinations WHERE 1=1"
        query_params = []
        
        if country:
            query += " AND country = ?"
            query_params.append(country)
        
        if city:
            query += " AND city = ?"
            query_params.append(city)
        
        if name_contains:
            query += " AND name LIKE ?"
            query_params.append(f"%{name_contains}%")
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(query, query_params)
        destinations = rows_to_dict_list(cursor, cursor.fetchall())
        conn.close()
        
        return func.HttpResponse(json.dumps(destinations, default=str), mimetype="application/json")
    except Exception as e:
        logging.error(str(e))
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)

@app.route(route="trips/destination/{destination_id}", methods=["GET"])
def get_trips_by_destination(req: func.HttpRequest) -> func.HttpResponse:
    # Obtener el destination_id de la ruta
    destination_id = int(req.route_params.get('destination_id'))
    
    logging.info(f"Fetching trips for destination ID: {destination_id}")
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Trips WHERE destination_id = ?", (destination_id,))
        trips = rows_to_dict_list(cursor, cursor.fetchall())
        conn.close()
        return func.HttpResponse(json.dumps(trips, default=str), mimetype="application/json")
    except Exception as e:
        logging.error(str(e))
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)

@app.route(route="bookings/trip/{trip_id}", methods=["GET"])
def get_bookings_by_trip(req: func.HttpRequest) -> func.HttpResponse:
    trip_id = int(req.route_params.get('trip_id'))
    logging.info(f"Fetching bookings for trip ID: {trip_id}")
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Bookings WHERE trip_id = ?", (trip_id,))
        bookings = rows_to_dict_list(cursor, cursor.fetchall())
        conn.close()
        return func.HttpResponse(json.dumps(bookings, default=str), mimetype="application/json")
    except Exception as e:
        logging.error(str(e))
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)

@app.route(route="trips-with-details", methods=["GET"])
def get_trips_with_details(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Fetching trips with destination details")
    try:
        conn = get_db()
        cursor = conn.cursor()
        query = """
        SELECT t.id, t.start_date, t.end_date, t.total_cost,
               d.name as destination_name, d.country, d.city, d.description,
               u.name as user_name, u.email
        FROM Trips t
        JOIN Destinations d ON t.destination_id = d.id
        JOIN Users u ON t.user_id = u.id
        """
        cursor.execute(query)
        trips = rows_to_dict_list(cursor, cursor.fetchall())
        conn.close()
        return func.HttpResponse(json.dumps(trips, default=str), mimetype="application/json")
    except Exception as e:
        logging.error(str(e))
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)

@app.route(route="bookings-with-details", methods=["GET"])
def get_bookings_with_details(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Fetching bookings with trip and user details")
    try:
        conn = get_db()
        cursor = conn.cursor()
        query = """
        SELECT b.id, b.status, b.booking_date,
               u.name as user_name, u.email,
               t.start_date, t.end_date, t.total_cost,
               d.name as destination_name, d.country, d.city
        FROM Bookings b
        JOIN Users u ON b.user_id = u.id
        JOIN Trips t ON b.trip_id = t.id
        JOIN Destinations d ON t.destination_id = d.id
        """
        cursor.execute(query)
        bookings = rows_to_dict_list(cursor, cursor.fetchall())
        conn.close()
        return func.HttpResponse(json.dumps(bookings, default=str), mimetype="application/json")
    except Exception as e:
        logging.error(str(e))
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)

@app.route(route="reviews-with-details", methods=["GET"])
def get_reviews_with_details(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Fetching reviews with user and destination details")
    try:
        conn = get_db()
        cursor = conn.cursor()
        query = """
        SELECT r.id, r.comment, r.rating, r.review_date,
               u.name as user_name, u.email,
               d.name as destination_name, d.country, d.city
        FROM Reviews r
        JOIN Users u ON r.user_id = u.id
        JOIN Destinations d ON r.destination_id = d.id
        """
        cursor.execute(query)
        reviews = rows_to_dict_list(cursor, cursor.fetchall())
        conn.close()
        return func.HttpResponse(json.dumps(reviews, default=str), mimetype="application/json")
    except Exception as e:
        logging.error(str(e))
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)

@app.route(route="destinations/top-rated", methods=["GET"])
def get_top_rated_destinations(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Fetching top rated destinations")
    try:
        limit = req.params.get("limit", "5")
        
        conn = get_db()
        cursor = conn.cursor()
        query = """
        SELECT d.id, d.name, d.country, d.city, d.description, d.image_url,
               AVG(r.rating) as average_rating,
               COUNT(r.id) as review_count
        FROM Destinations d
        JOIN Reviews r ON d.id = r.destination_id
        GROUP BY d.id, d.name, d.country, d.city, d.description, d.image_url
        ORDER BY average_rating DESC, review_count DESC
        """
        if limit.isdigit():
            query += f" OFFSET 0 ROWS FETCH NEXT {limit} ROWS ONLY"
            
        cursor.execute(query)
        destinations = rows_to_dict_list(cursor, cursor.fetchall())
        conn.close()
        return func.HttpResponse(json.dumps(destinations, default=str), mimetype="application/json")
    except Exception as e:
        logging.error(str(e))
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)

@app.route(route="users/{user_id}/dashboard", methods=["GET"])
def get_user_dashboard(req: func.HttpRequest) -> func.HttpResponse:
    user_id = int(req.route_params.get('user_id'))
    logging.info(f"Fetching dashboard information for user ID: {user_id}")
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Obtener usuario
        cursor.execute("SELECT * FROM Users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        if not user:
            conn.close()
            return func.HttpResponse("User not found", status_code=404)
        
        user_dict = dict(zip([column[0] for column in cursor.description], user))
        
        # Obtener viajes del usuario
        cursor.execute("SELECT * FROM Trips WHERE user_id = ?", (user_id,))
        trips = rows_to_dict_list(cursor, cursor.fetchall())
        
        # Obtener reservas del usuario
        cursor.execute("SELECT * FROM Bookings WHERE user_id = ?", (user_id,))
        bookings = rows_to_dict_list(cursor, cursor.fetchall())
        
        # Obtener pagos del usuario
        cursor.execute("SELECT * FROM Payments WHERE user_id = ?", (user_id,))
        payments = rows_to_dict_list(cursor, cursor.fetchall())
        
        # Obtener reseñas del usuario
        cursor.execute("SELECT * FROM Reviews WHERE user_id = ?", (user_id,))
        reviews = rows_to_dict_list(cursor, cursor.fetchall())
        
        # Construir objeto de dashboard
        dashboard = {
            "user": user_dict,
            "trip_count": len(trips),
            "booking_count": len(bookings),
            "payment_amount_total": sum(payment["amount"] for payment in payments),
            "review_count": len(reviews),
            "recent_trips": trips[-5:] if trips else [],
            "recent_bookings": bookings[-5:] if bookings else [],
            "recent_reviews": reviews[-5:] if reviews else []
        }
        
        conn.close()
        return func.HttpResponse(json.dumps(dashboard, default=str), mimetype="application/json")
    except Exception as e:
        logging.error(str(e))
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)
