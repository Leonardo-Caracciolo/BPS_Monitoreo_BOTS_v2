"""
fetch_db_server.py
------------------
Descarga la tabla monitoreo_bots desde SQL Server y la exporta
a data/inputs/DB_Server.xlsx con el mismo formato del archivo original.

Este módulo es llamado desde main.py — no tiene entry point propio.
"""

import os
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.exc import OperationalError, InterfaceError
from taxteclib.database_logger import SqlServerClient

load_dotenv()

SHEET_NAME = "Tabla Monitoreos"

# La tabla SQL guarda estado como entero — el pipeline espera strings
ESTADO_MAP = {
    0: "Correcto",
    1: "Proceso finalizado con errores",
    2: "Erróneo",
}

# Columnas en el mismo orden que el Excel original
COLUMNAS_EXCEL = [
    "id", "username", "proceso", "estado",
    "iniciado", "finalizado", "cliente", "items_count", "observaciones",
]


def _try_database_drivers(
    db_server: str,
    db_name: str,
    username: str,
    password: str,
) -> str:
    """
    Prueba drivers ODBC en orden hasta encontrar uno que funcione.

    Returns
    -------
    str
        Nombre del driver que funcionó.

    Raises
    ------
    RuntimeError
        Si ningún driver conecta. Generalmente indica que la VPN no está activa.
    """
    drivers = [
        "ODBC Driver 17 for SQL Server",
        "SQL Server",
        "ODBC Driver 13 for SQL Server",
    ]
    errores = []
    for driver in drivers:
        try:
            inst = SqlServerClient(
                username, password, db_server, db_name, driver
            ).engine.connect()
            inst.close()
            del inst
            print(f"  ✅ Conectado con driver: {driver}")
            return driver
        except (OperationalError, InterfaceError) as e:
            errores.append(f"{driver}: {str(e)[:100]}")

    raise RuntimeError(
        f"No se pudo conectar a la base de datos.\n"
        f"¿Está la VPN activa?\n"
        f"Detalle:\n" + "\n".join(errores)
    )


def fetch_and_export(output_path: Path) -> None:
    """
    Conecta a SQL Server, descarga monitoreo_bots y exporta a Excel.

    Lee las credenciales desde el archivo .env en la raíz del proyecto.
    Convierte el campo `estado` de entero a string para mantener
    compatibilidad con el formato del Excel original y con el pipeline.

    Parameters
    ----------
    output_path : Path
        Ruta destino del Excel. Normalmente: data/inputs/DB_Server.xlsx

    Raises
    ------
    EnvironmentError
        Si faltan variables de entorno en el .env.
    RuntimeError
        Si no se puede conectar (VPN inactiva o credenciales incorrectas).
    """
    db_server   = os.getenv("DB_SERVER")
    db_database = os.getenv("DB_DATABASE")
    db_user     = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")

    faltantes = [k for k, v in {
        "DB_SERVER":   db_server,
        "DB_DATABASE": db_database,
        "DB_USER":     db_user,
        "DB_PASSWORD": db_password,
    }.items() if not v]

    if faltantes:
        raise EnvironmentError(
            f"Faltan variables en el archivo .env: {faltantes}\n"
            f"Usá .env.example como plantilla."
        )

    print(f"  Servidor  : {db_server}")
    print(f"  Base datos: {db_database}")
    print(f"  Usuario   : {db_user}")
    print(f"  Detectando driver ODBC...")

    driver = _try_database_drivers(db_server, db_database, db_user, db_password)
    client = SqlServerClient(db_user, db_password, db_server, db_database, driver)

    print(f"  Descargando tabla monitoreo_bots...")
    with client.engine.connect() as conn:
        df = pd.read_sql(text("SELECT * FROM monitoreo_bots ORDER BY id"), conn)
    print(f"  {len(df):,} registros descargados.")

    # Convertir estado int → string
    if pd.api.types.is_integer_dtype(df["estado"]):
        df["estado"] = df["estado"].map(ESTADO_MAP).fillna(df["estado"].astype(str))

    # Reordenar columnas igual al Excel original
    cols = [c for c in COLUMNAS_EXCEL if c in df.columns]
    df = df[cols]

    # Exportar
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name=SHEET_NAME, index=False)

    print(f"  ✅ Exportado: {output_path}  ({len(df):,} filas)")