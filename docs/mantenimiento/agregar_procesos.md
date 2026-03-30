# Agregar nuevos procesos

Cuando aparece un proceso nuevo en DB_Server que no está mapeado, el pipeline lo incluye igual con `en_relevamiento = False` y el nombre original como herramienta.

Para mapearlo correctamente a una herramienta del Relevamiento, editar `settings.py`:

## Si el proceso corresponde a una herramienta existente

```python
# En PROCESO_A_HERRAMIENTA, agregar:
"Nombre exacto del proceso en DB_Server": "Herramienta del Relevamiento",
```

Ejemplo:
```python
"GUI: Nuevo Control de Percepciones": "Padrones Impositivos - ComplyPro",
```

## Si el proceso es externo (no tiene herramienta en el Relevamiento)

```python
# En PROCESO_A_HERRAMIENTA, agregar:
"Nombre del proceso": "Nombre del proceso",  # mapeado a sí mismo

# En PROCESOS_SIN_HERRAMIENTA, agregar:
PROCESOS_SIN_HERRAMIENTA = {
    ...,
    "Nombre del proceso",
}
```

## Si el proceso tiene variantes de nombre

```python
# Mapear todas las variantes a la misma herramienta:
"GUI: Control de X":     "Herramienta canónica",
"GUI: Controlar X":      "Herramienta canónica",
"GUI: Controlando X":    "Herramienta canónica",
```

Después de editar `settings.py`, ejecutar `python main.py` para regenerar los CSVs.
