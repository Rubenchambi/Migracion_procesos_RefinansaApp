# apps/usuarios/db.py
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

def obtener_engine_sql(db_type="default"):

    if db_type == "actualizacion": # Nuevo caso
        server = os.getenv("ACT_SERVER")
        database = os.getenv("ACT_DATABASE")
        username = os.getenv("ACT_USERNAME")
        password = os.getenv("ACT_PASSWORD")
        driver = os.getenv("ACT_DRIVER")
    elif db_type == "asignaciones":
        # Lee las variables con prefijo ASIG_
        server = os.getenv("ASIG_SERVER")
        database = os.getenv("ASIG_DATABASE")
        username = os.getenv("ASIG_USERNAME")
        password = os.getenv("ASIG_PASSWORD")
        driver = os.getenv("ASIG_DRIVER")
    else:
        # Lee las variables por defecto (Django)
        server = os.getenv("DB_SERVER")
        database = os.getenv("DB_DATABASE")
        username = os.getenv("DB_USERNAME")
        password = os.getenv("DB_PASSWORD")
        driver = os.getenv("DB_DRIVER")

    cadena_conexion = f"mssql+pyodbc://{username}:{password}@{server}/{database}?driver={driver}"
    return create_engine(cadena_conexion, fast_executemany=True)