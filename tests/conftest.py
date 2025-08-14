import pytest
import sys
import os
from unittest.mock import Mock

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from recepcionista_simple import Rswarm


@pytest.fixture
def rswarm_instance():
    """Fixture que proporciona una instancia de Rswarm para los tests"""
    return Rswarm()


@pytest.fixture
def mock_swarm():
    """Fixture que proporciona un mock del Swarm"""
    mock = Mock()
    mock.handle.return_value = "Respuesta mock del swarm"
    return mock


@pytest.fixture
def mensajes_prueba():
    """Fixture que proporciona mensajes de prueba comunes"""
    return {
        "cita": "Necesito agendar una cita para mañana",
        "gracias": "Muchas gracias por tu ayuda",
        "generico": "Hola, ¿cómo estás?",
        "vacio": "",
        "largo": "a" * 500,
        "especiales": "¡Hola! ¿Cómo estás? @#$%^&*()",
        "emojis": "Hola 😊 necesito una cita 📅",
        "numeros": "Cita para el día 15 a las 3pm"
    }


@pytest.fixture
def respuestas_esperadas():
    """Fixture que proporciona respuestas esperadas para validación"""
    return {
        "cita": ["día", "hora"],
        "gracias": ["de nada", "ayudar"],
        "generico": ["rswarm", "recepcionista"],
        "default": ["rswarm", "recepcionista"]
    }

# Database fixture for tests that need it
@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Set up the database for the test session."""
    # This import is here to avoid circular dependencies
    from infra.database import init_db, drop_db
    init_db()
    yield
    drop_db()