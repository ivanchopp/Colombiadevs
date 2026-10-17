import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from acta import salas  # noqa: E402
from acta.almacen import AlmacenSqlite  # noqa: E402


@pytest.fixture
def almacen(tmp_path):
    return AlmacenSqlite(tmp_path / "acta.db")


@pytest.fixture
def sala(almacen):
    return salas.crear(almacen)
