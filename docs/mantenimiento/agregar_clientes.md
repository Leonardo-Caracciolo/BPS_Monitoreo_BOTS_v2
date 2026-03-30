# Agregar nuevos clientes

## En el Relevamiento

1. Abrí `Relevamiento_BPS_Organizado_-_v2.xlsm`
2. En la sheet **Clientes**, agregá una nueva fila con:
   - `ID_Cliente`: siguiente número disponible
   - `Cliente`: nombre del cliente
   - `Cuit`: CUIT real (con o sin guiones — el pipeline los limpia)
   - `Gerente responsable`: gerente a cargo
3. En la sheet **Uso de herramientas**, agregá 11 filas (una por herramienta) con `ID_Cliente` del nuevo cliente y `Usa Herramienta = SI` o `NO` según corresponda
4. Guardá el archivo en `data/inputs/`
5. Ejecutá `python main.py`

---

## Actualizar CUITs dummy

Los 25 clientes con CUIT placeholder se detectan con `cuit_es_dummy = True` en `dim_clientes`. Para actualizarlos, simplemente reemplazá el valor `00000000001` etc. por el CUIT real en la sheet Clientes del Relevamiento y volvé a ejecutar el pipeline.

Los clientes pendientes son:
INDUSTRIAS LEAR, AUTH0, adidas Argentina, Reebok, EUROP, BRITISH COUNCIL, BIOGEN, SHPP, SONY, HP, LINKEDTORE, VERTIV, OSIDOFT, LINKEDSTORE, ABBVIE, JOHNSON & JOHNSON MEDICAL, BIOMARIN, INLAND SERVICES, SVITZER, ADVANCED STERILIZATION PRODUCTS, JANSSEN CILAG, J&J Argentina, IGT ARGENTINA, INGREDION ARGENTINA, Munchener.
