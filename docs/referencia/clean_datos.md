# clean_datos.py

Función base de lectura y limpieza de DB_Server.xlsx. Fue escrita originalmente por el usuario del proyecto y se integró al pipeline sin cambios en su lógica.

## Responsabilidad

Esta función tiene **una sola responsabilidad**: leer el archivo Excel y normalizar los campos de texto. No aplica ninguna lógica de negocio. Toda la transformación de negocio ocurre en `paso2_db_server.py`.

## Por qué se necesita la limpieza

DB_Server es alimentada por múltiples operadores de forma manual. Es común encontrar:

- Espacios al inicio o final de strings: `"TECHINT "` en vez de `"TECHINT"`.
- Espacios dobles internos: `"FACEBOOK  ARGENTINA"` en vez de `"FACEBOOK ARGENTINA"`.

Sin esta limpieza, comparaciones como `"TECHINT" == "TECHINT "` fallarían silenciosamente, causando que matcheos y joins no funcionen correctamente.

## Función

::: clean_datos.clean_datos

## Ejemplo de uso

```python
from clean_datos import clean_datos

df = clean_datos("data/inputs/DB_Server.xlsx")

# El DataFrame tiene 9 columnas originales de "Tabla Monitoreos"
print(df.columns.tolist())
# ['id', 'username', 'proceso', 'estado', 'iniciado',
#  'finalizado', 'cliente', 'items_count', 'observaciones']

print(df.shape)
# (30881, 9)
```

## Cómo se usa en el pipeline

`clean_datos()` es llamada al inicio de `leer_db_server()` en `paso2_db_server.py`:

```python
from clean_datos import clean_datos

def leer_db_server(path_db, path_tabla_cuits, df_personal=None):
    # clean_datos hace la lectura y limpieza básica
    df = clean_datos(str(path_db))
    
    # Después de esto, paso2 aplica la lógica de negocio
    # ...
```

## Migración a SQL

Cuando DB_Server pase a SQL, esta función se reemplaza por una lectura desde la base de datos. La limpieza de strings también se aplica, ya que los datos históricos en SQL pueden tener los mismos problemas:

```python
# Versión SQL (futura)
def clean_datos_sql(connection_string: str) -> pd.DataFrame:
    engine = sqlalchemy.create_engine(connection_string)
    df = pd.read_sql("SELECT * FROM monitoreo_bots", engine)
    df = df.apply(
        lambda col: col.str.strip().str.replace(r"\s+", " ", regex=True)
        if col.dtype == "object" else col
    )
    return df
```
