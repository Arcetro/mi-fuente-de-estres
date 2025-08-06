import pytest
from unittest.mock import Mock, patch
import sys
import os

# Agregar el directorio raíz al path para importar el módulo
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from recepcionista_simple import Rswarm, recibir_mensaje, enviar_respuesta


class TestRswarm:
    """Tests para la clase Rswarm"""
    
    def setup_method(self):
        """Configuración antes de cada test"""
        self.rswarm = Rswarm()
    
    def test_handle_cita(self):
        """Test para mensajes que contienen 'cita'"""
        mensaje = "Necesito agendar una cita"
        respuesta = self.rswarm.handle(mensaje)
        assert "día" in respuesta.lower()
        assert "hora" in respuesta.lower()
    
    def test_handle_gracias(self):
        """Test para mensajes que contienen 'gracias'"""
        mensaje = "Muchas gracias por tu ayuda"
        respuesta = self.rswarm.handle(mensaje)
        assert "de nada" in respuesta.lower()
        assert "ayudar" in respuesta.lower()
    
    def test_handle_mensaje_generico(self):
        """Test para mensajes genéricos"""
        mensaje = "Hola, ¿cómo estás?"
        respuesta = self.rswarm.handle(mensaje)
        assert "rswarm" in respuesta.lower()
        assert "recepcionista" in respuesta.lower()
    
    def test_handle_mensaje_vacio(self):
        """Test para mensajes vacíos"""
        mensaje = ""
        respuesta = self.rswarm.handle(mensaje)
        assert respuesta is not None
        assert len(respuesta) > 0
    
    def test_handle_mensaje_con_mayusculas(self):
        """Test para mensajes con mayúsculas"""
        mensaje = "CITA para mañana"
        respuesta = self.rswarm.handle(mensaje)
        assert "día" in respuesta.lower()
    
    def test_handle_mensaje_con_numeros(self):
        """Test para mensajes con números"""
        mensaje = "Cita para el día 15"
        respuesta = self.rswarm.handle(mensaje)
        assert "día" in respuesta.lower()


class TestFuncionesAuxiliares:
    """Tests para las funciones auxiliares"""
    
    @patch('builtins.input')
    def test_recibir_mensaje(self, mock_input):
        """Test para la función recibir_mensaje"""
        mock_input.return_value = "Hola"
        mensaje = recibir_mensaje()
        assert mensaje == "Hola"
        mock_input.assert_called_once()
    
    def test_enviar_respuesta(self):
        """Test para la función enviar_respuesta"""
        respuesta = "Respuesta de prueba"
        # Simplemente verificar que la función no falla
        try:
            enviar_respuesta(respuesta)
            assert True  # Si llegamos aquí, la función funcionó
        except Exception as e:
            assert False, f"La función enviar_respuesta falló: {e}"


class TestCasosEdge:
    """Tests para casos edge y límites"""
    
    def setup_method(self):
        self.rswarm = Rswarm()
    
    def test_mensaje_muy_largo(self):
        """Test para mensajes muy largos"""
        mensaje = "a" * 1000
        respuesta = self.rswarm.handle(mensaje)
        assert respuesta is not None
        assert len(respuesta) > 0
    
    def test_mensaje_con_caracteres_especiales(self):
        """Test para mensajes con caracteres especiales"""
        mensaje = "¡Hola! ¿Cómo estás? @#$%^&*()"
        respuesta = self.rswarm.handle(mensaje)
        assert respuesta is not None
    
    def test_mensaje_con_emojis(self):
        """Test para mensajes con emojis"""
        mensaje = "Hola 😊 necesito una cita 📅"
        respuesta = self.rswarm.handle(mensaje)
        assert "día" in respuesta.lower()


if __name__ == "__main__":
    pytest.main([__file__]) 