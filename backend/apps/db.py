import os
from dotenv import load_dotenv
from sqlalchemy import create_engine

# Cargar las variables del archivo .env
load_dotenv()

# Leer las credenciales
SERVER = os.getenv("DB_SERVER")
DATABASE = os.getenv("DB_DATABASE")
USERNAME = os.getenv("DB_USERNAME")
PASSWORD = os.getenv("DB_PASSWORD")
DRIVER = os.getenv("DB_DRIVER")


def obtener_engine_sql():
    """Retorna el motor de conexión a SQL Server configurado con fast_executemany."""
    cadena_conexion = (
        f"mssql+pyodbc://{USERNAME}:{PASSWORD}@{SERVER}/{DATABASE}?driver={DRIVER}"
    )
    # Retornamos el engine con tu criterio de velocidad exacta
    return create_engine(cadena_conexion, fast_executemany=True)