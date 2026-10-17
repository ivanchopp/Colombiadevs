# Colombia Devs · Reto Blinka

Agente que revisa facturas y decide **PAGAR / FRENAR / ESCALAR** según reglas configurables. No mueve dinero real y solo usa datos ficticios. La IA lee y redacta; decide un motor de reglas sin IA.

Para entender el proyecto: `AVANCES.md`, luego `specs/README.md`.

## Ejecutar en local
```
python -m venv .venv && . .venv/bin/activate
pip install -r requirements-dev.txt
python init_db.py
streamlit run app/main.py
pytest
```
Despliegue en Railway: ver `railway.toml` y `specs/paneles-y-despliegue`. **Estado: esqueleto**; muchas piezas son stubs que dicen qué tarea las completa. PostgreSQL y Railway aún no están probados.
