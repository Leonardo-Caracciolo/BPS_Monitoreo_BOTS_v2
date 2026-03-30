# BPS Monitoreo Bots — Documentación

Pipeline ETL que toma las ejecuciones reales de bots desde `DB_Server.xlsx` y el relevamiento de clientes desde `Relevamiento BPS.xlsm`, los transforma y produce tablas listas para visualizar en Power BI.

---

## ¿Qué hace este proyecto?

La empresa ejecuta bots que automatizan tareas contables para sus clientes (NFE Alert, Padrones Impositivos, Control de Correlatividad, etc.). Estas ejecuciones se registran en una base de datos (`monitoreo_bots`, hoy exportada como `DB_Server.xlsx`).

El problema es que esa base de datos no estaba en condiciones de ser analizada directamente:

- El campo `cliente` tiene tres formatos distintos: CUIT numérico, nombre libre con errores, o vacío.
- El mismo cliente puede estar escrito de 10 formas distintas (`TECHINT`, `Techint`, `TECHINT S.A.`, etc.).
- Los nombres de procesos en la base de datos no coinciden con los nombres de herramientas del Relevamiento.
- No había ninguna columna que indicara si el proceso ejecutado estaba o no en el Relevamiento.

Este pipeline resuelve todos esos problemas y produce tablas limpias con un modelo estrella para Power BI.

---

## Cómo ejecutar

```bash
# 1. Instalar dependencias (una sola vez)
pip install pandas openpyxl

# 2. Poner los archivos de entrada en data/inputs/

# 3. Ejecutar
python main.py
```

---

## Archivos que produce

| Archivo | Filas | Uso en Power BI |
|---|---|---|
| `dim_clientes.csv` | 46 | Dimensión de clientes — lado "Uno" de las relaciones |
| `dim_herramientas.csv` | 26 | Catálogo de herramientas con flag `en_relevamiento` |
| `dim_relevamiento.csv` | 517 | Cliente × herramienta esperada — tabla suelta |
| `fact_ejecuciones.csv` | 30.881 | Tabla de hechos — ejecuciones reales |
| `fact_esperado.csv` | 2.376 | Tabla de hechos — ejecuciones esperadas por mes |
| `diagnostico_matcheo.xlsx` | — | 7 hojas de calidad de datos — uso interno |

---

## Navegación de esta documentación

- **Arquitectura** → visión general del sistema, modelo de datos y flujo ETL
- **Módulos** → documentación detallada de cada archivo `.py`
- **Power BI** → cómo configurar el modelo, relaciones y medidas DAX
- **Mantenimiento** → cómo agregar clientes, procesos y migrar a SQL
