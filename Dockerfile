FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 PYTHONPATH=/app PIP_NO_CACHE_DIR=1 PIP_DISABLE_PIP_VERSION_CHECK=1
WORKDIR /app

# Solo lo necesario para correr (sin pruebas): ver requirements-prod.txt
COPY requirements-prod.txt .
RUN pip install -r requirements-prod.txt

COPY . .
# Corre como root a propósito: los volúmenes de Railway se montan con dueño root y un usuario
# sin privilegios no podría escribir el acta. Es una demo con datos ficticios.

# Railway define PORT. El volumen (si existe) se monta en RAILWAY_VOLUME_MOUNT_PATH.
CMD ["sh", "-c", "exec python -m streamlit run app/Panel_1_Proveedor.py --server.address=0.0.0.0 --server.port=${PORT:-8501} --server.headless=true"]
