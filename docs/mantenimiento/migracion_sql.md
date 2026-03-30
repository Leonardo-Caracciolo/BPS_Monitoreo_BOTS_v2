# Migración a SQL

Actualmente el pipeline lee `DB_Server.xlsx` (exportación manual de la tabla `monitoreo_bots`). Cuando se conecte directamente a la base de datos SQL, el cambio es mínimo.

## Cambio necesario

Solo hay que modificar la función `clean_datos()` en `clean_datos.py`.

**Antes (Excel):**
```python
def clean_datos(file_path: str) -> pd.DataFrame:
    df_server = pd.read_excel(file_path, sheet_name="Tabla Monitoreos", engine="openpyxl")
    df_server = df_server.apply(
        lambda col: col.str.strip().str.replace(r"\s+", " ", regex=True)
        if col.dtype == "object" else col
    )
    return df_server
```

**Después (SQL):**
```python
import sqlalchemy

def clean_datos(connection_string: str) -> pd.DataFrame:
    engine = sqlalchemy.create_engine(connection_string)
    df_server = pd.read_sql("SELECT * FROM monitoreo_bots", engine)
    df_server = df_server.apply(
        lambda col: col.str.strip().str.replace(r"\s+", " ", regex=True)
        if col.dtype == "object" else col
    )
    return df_server
```

**En settings.py**, reemplazar:
```python
PATH_DB_SERVER = INPUTS_DIR / "DB_Server.xlsx"
```
por:
```python
DB_CONNECTION_STRING = "postgresql://user:password@host:5432/database"
```

**En main.py**, actualizar la llamada:
```python
# Antes:
df_db = leer_db_server(PATH_DB_SERVER, PATH_TABLA_CUITS)

# Después:
df_db = leer_db_server(DB_CONNECTION_STRING, PATH_TABLA_CUITS)
```

El resto del pipeline (paso1, paso2, paso3, paso4, construir_esperado) no necesita ningún cambio.

## Dependencias adicionales para SQL

```bash
pip install sqlalchemy psycopg2-binary  # para PostgreSQL
# o
pip install sqlalchemy pyodbc           # para SQL Server
```
