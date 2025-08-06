import pytest
from unittest.mock import patch, Mock
import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from recepcionista_simple import Rswarm, Swarm


class TestIntegracionSwarm:
    """Tests de integración para el sistema completo"""
    
    def setup_method(self):
        """Configuración antes de cada test"""
        self.rswarm = Rswarm()
        self.swarm = Swarm([self.rswarm])
    
    def test_swarm_creacion(self):
        """Test para verificar que el swarm se crea correctamente"""
        assert self.swarm is not None
        assert len(self.swarm.agents) == 1
        assert isinstance(self.swarm.agents[0], Rswarm)
    
    def test_swarm_handle_mensaje(self):
        """Test para verificar que el swarm maneja mensajes correctamente"""
        mensaje = "Necesito una cita"
        respuesta = self.swarm.handle(mensaje)
        assert respuesta is not None
        assert len(respuesta) > 0
    
    def test_swarm_con_multiple_agentes(self):
        """Test para verificar el comportamiento con múltiples agentes"""
        # Crear un segundo agente mock
        mock_agent = Mock()
        mock_agent.handle.return_value = "Respuesta del agente mock"
        
        # Agregar al swarm
        swarm_multi = Swarm([self.rswarm, mock_agent])
        
        # El swarm debería usar el primer agente (Rswarm)
        mensaje = "Hola"
        respuesta = swarm_multi.handle(mensaje)
        assert "rswarm" in respuesta.lower()


class TestFlujoCompleto:
    """Tests para el flujo completo de la aplicación"""
    
    @patch('builtins.input')
    @patch('rich.print')
    def test_flujo_conversacion_completa(self, mock_print, mock_input):
        """Test para simular una conversación completa"""
        # Simular entrada de usuario
        mock_input.side_effect = ["Hola", "Necesito una cita", "Gracias", "salir"]
        
        # Importar y ejecutar el main (simulado)
        from recepcionista_simple import Rswarm, Swarm
        
        rswarm = Rswarm()
        swarm = Swarm([rswarm])
        
        # Simular el procesamiento de mensajes
        respuestas = []
        for mensaje in ["Hola", "Necesito una cita", "Gracias"]:
            respuesta = swarm.handle(mensaje)
            respuestas.append(respuesta)
        
        # Verificar que se generaron respuestas
        assert len(respuestas) == 3
        assert all(len(resp) > 0 for resp in respuestas)
        
        # Verificar que la primera respuesta es genérica
        assert "rswarm" in respuestas[0].lower()
        
        # Verificar que la segunda respuesta es sobre citas
        assert "día" in respuestas[1].lower()
        
        # Verificar que la tercera respuesta es de agradecimiento
        assert "de nada" in respuestas[2].lower()


class TestCasosUsoReal:
    """Tests que simulan casos de uso reales"""
    
    def setup_method(self):
        self.rswarm = Rswarm()
        self.swarm = Swarm([self.rswarm])
    
    def test_secuencia_cita_completa(self):
        """Test para una secuencia completa de agendar cita"""
        mensajes = [
            "Hola",
            "Necesito agendar una cita",
            "Para mañana a las 3pm",
            "Gracias"
        ]
        
        respuestas = []
        for mensaje in mensajes:
            respuesta = self.swarm.handle(mensaje)
            respuestas.append(respuesta)
        
        # Verificar que todas las respuestas son apropiadas
        assert len(respuestas) == 4
        assert "rswarm" in respuestas[0].lower()
        assert "día" in respuestas[1].lower()
        assert "rswarm" in respuestas[2].lower()  # Mensaje genérico
        assert "de nada" in respuestas[3].lower()
    
    def test_secuencia_soporte_tecnico(self):
        """Test para una secuencia de soporte técnico"""
        mensajes = [
            "Hola",
            "Tengo un problema con mi cuenta",
            "No puedo acceder",
            "Gracias por la ayuda"
        ]
        
        respuestas = []
        for mensaje in mensajes:
            respuesta = self.swarm.handle(mensaje)
            respuestas.append(respuesta)
        
        # Verificar respuestas
        assert len(respuestas) == 4
        assert all(len(resp) > 0 for resp in respuestas)
    
    def test_secuencia_facturacion(self):
        """Test para una secuencia de facturación"""
        mensajes = [
            "Hola",
            "Necesito mi factura",
            "Del mes pasado",
            "Gracias"
        ]
        
        respuestas = []
        for mensaje in mensajes:
            respuesta = self.swarm.handle(mensaje)
            respuestas.append(respuesta)
        
        # Verificar respuestas
        assert len(respuestas) == 4
        assert all(len(resp) > 0 for resp in respuestas)


@pytest.mark.integration
class TestPerformance:
    """Tests de performance y carga"""
    
    def setup_method(self):
        self.rswarm = Rswarm()
        self.swarm = Swarm([self.rswarm])
    
    def test_multiples_mensajes_rapidos(self):
        """Test para verificar el manejo de múltiples mensajes rápidos"""
        mensajes = ["Hola"] * 100
        
        import time
        start_time = time.time()
        
        respuestas = []
        for mensaje in mensajes:
            respuesta = self.swarm.handle(mensaje)
            respuestas.append(respuesta)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Verificar que se procesaron todos los mensajes
        assert len(respuestas) == 100
        assert all(len(resp) > 0 for resp in respuestas)
        
        # Verificar que el tiempo de procesamiento es razonable (< 1 segundo para 100 mensajes)
        assert processing_time < 1.0
    
    def test_mensajes_largos_performance(self):
        """Test para verificar el manejo de mensajes largos"""
        mensaje_largo = "Este es un mensaje muy largo " * 50
        
        import time
        start_time = time.time()
        
        respuesta = self.swarm.handle(mensaje_largo)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Verificar que se procesó correctamente
        assert respuesta is not None
        assert len(respuesta) > 0
        
        # Verificar que el tiempo de procesamiento es razonable
        assert processing_time < 0.1 