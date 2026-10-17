"""Configuración desde variables de entorno. Spec: paneles-y-despliegue (PD8, PD9)."""
from __future__ import annotations

import os

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///colombiadevs.db")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
MODO_DEMO = os.environ.get("MODO_DEMO", "").lower() in {"1", "true", "si", "sí"} or not ANTHROPIC_API_KEY
LARGO_SALA = 8
