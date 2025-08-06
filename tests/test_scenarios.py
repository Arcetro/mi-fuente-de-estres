import pytest
import sys
import os
from unittest.mock import Mock, patch

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from recepcionista_simple import Rswarm, Swarm


class TestEscenariosReales:
    """Tests que simulan escenarios reales de uso"""
    
    def setup_method(self):
        self.rswarm = Rswarm()
        self.swarm = Swarm([self.rswarm])
    
    def test_escenario_cliente_nuevo(self):
        """Escenario: Cliente nuevo que no sabe qué hacer"""
        conversacion = [
            "Hola",
            "¿Qué servicios ofrecen?",
            "¿Cuánto cuesta?",
            "Gracias por la información"
        ]
        
        respuestas = []
        for mensaje in conversacion:
            respuesta = self.swarm.handle(mensaje)
            respuestas.append(respuesta)
        
        # Verificar que todas las respuestas son apropiadas
        assert len(respuestas) == 4
        assert all(len(resp) > 0 for resp in respuestas)
        assert "rswarm" in respuestas[0].lower()
        assert "de nada" in respuestas[3].lower()
    
    def test_escenario_cliente_urgente(self):
        """Escenario: Cliente con urgencia"""
        conversacion = [
            "¡URGENTE!",
            "Necesito ayuda inmediata",
            "Es una emergencia",
            "Por favor ayúdenme"
        ]
        
        respuestas = []
        for mensaje in conversacion:
            respuesta = self.swarm.handle(mensaje)
            respuestas.append(respuesta)
        
        # Verificar respuestas
        assert len(respuestas) == 4
        assert all(len(resp) > 0 for resp in respuestas)
    
    def test_escenario_cliente_confundido(self):
        """Escenario: Cliente confundido que repite preguntas"""
        conversacion = [
            "Hola",
            "¿Qué servicios ofrecen?",
            "¿Qué servicios ofrecen?",  # Repite la pregunta
            "No entiendo",
            "¿Pueden explicarme mejor?",
            "Gracias"
        ]
        
        respuestas = []
        for mensaje in conversacion:
            respuesta = self.swarm.handle(mensaje)
            respuestas.append(respuesta)
        
        # Verificar respuestas
        assert len(respuestas) == 6
        assert all(len(resp) > 0 for resp in respuestas)
        assert "de nada" in respuestas[5].lower()
    
    def test_escenario_cliente_agresivo(self):
        """Escenario: Cliente frustrado o agresivo"""
        conversacion = [
            "Hola",
            "Estoy muy molesto",
            "Su servicio es terrible",
            "Quiero hablar con un supervisor",
            "Esto es inaceptable"
        ]
        
        respuestas = []
        for mensaje in conversacion:
            respuesta = self.swarm.handle(mensaje)
            respuestas.append(respuesta)
        
        # Verificar que el sistema mantiene la calma
        assert len(respuestas) == 5
        assert all(len(resp) > 0 for resp in respuestas)
    
    def test_escenario_conversacion_larga(self):
        """Escenario: Conversación larga y compleja"""
        conversacion = [
            "Hola, buenos días",
            "Necesito información sobre sus servicios",
            "¿Tienen servicio de consultoría?",
            "¿Cuál es el precio?",
            "¿Pueden hacer descuento?",
            "¿Tienen referencias?",
            "¿Cuánto tiempo tardan?",
            "Me interesa, quiero agendar una cita",
            "¿Para cuándo tienen disponibilidad?",
            "Perfecto, gracias por toda la información"
        ]
        
        respuestas = []
        for mensaje in conversacion:
            respuesta = self.swarm.handle(mensaje)
            respuestas.append(respuesta)
        
        # Verificar conversación completa
        assert len(respuestas) == 10
        assert all(len(resp) > 0 for resp in respuestas)
        assert "día" in respuestas[7].lower()  # Respuesta sobre cita
        assert "de nada" in respuestas[9].lower()  # Respuesta final


class TestCasosEspeciales:
    """Tests para casos especiales y edge cases"""
    
    def setup_method(self):
        self.rswarm = Rswarm()
        self.swarm = Swarm([self.rswarm])
    
    def test_mensajes_con_errores_ortograficos(self):
        """Test para mensajes con errores ortográficos"""
        mensajes = [
            "Hla",
            "Nesito una sita",
            "Grasias"
        ]
        
        respuestas = []
        for mensaje in mensajes:
            respuesta = self.swarm.handle(mensaje)
            respuestas.append(respuesta)
        
        # Verificar que el sistema responde apropiadamente
        assert len(respuestas) == 3
        assert all(len(resp) > 0 for resp in respuestas)
    
    def test_mensajes_en_diferentes_idiomas(self):
        """Test para mensajes en diferentes idiomas"""
        mensajes = [
            "Hello",
            "I need an appointment",
            "Thank you"
        ]
        
        respuestas = []
        for mensaje in mensajes:
            respuesta = self.swarm.handle(mensaje)
            respuestas.append(respuesta)
        
        # Verificar respuestas
        assert len(respuestas) == 3
        assert all(len(resp) > 0 for resp in respuestas)
    
    def test_mensajes_con_comandos(self):
        """Test para mensajes que parecen comandos"""
        mensajes = [
            "/help",
            "!info",
            "?ayuda"
        ]
        
        respuestas = []
        for mensaje in mensajes:
            respuesta = self.swarm.handle(mensaje)
            respuestas.append(respuesta)
        
        # Verificar respuestas
        assert len(respuestas) == 3
        assert all(len(resp) > 0 for resp in respuestas)
    
    def test_mensajes_con_links(self):
        """Test para mensajes que contienen URLs"""
        mensajes = [
            "Hola, visité su sitio web https://ejemplo.com",
            "¿Pueden revisar este link? http://test.com",
            "Encontré esto en su página: www.ejemplo.com"
        ]
        
        respuestas = []
        for mensaje in mensajes:
            respuesta = self.swarm.handle(mensaje)
            respuestas.append(respuesta)
        
        # Verificar respuestas
        assert len(respuestas) == 3
        assert all(len(resp) > 0 for resp in respuestas)


class TestEscenariosMultiagente:
    """Tests para escenarios con múltiples agentes (preparación futura)"""
    
    def setup_method(self):
        self.rswarm = Rswarm()
        # Crear agentes mock para simular diferentes especialidades
        self.agente_citas = Mock()
        self.agente_citas.handle.return_value = "Respuesta del agente de citas"
        
        self.agente_soporte = Mock()
        self.agente_soporte.handle.return_value = "Respuesta del agente de soporte"
        
        self.agente_facturacion = Mock()
        self.agente_facturacion.handle.return_value = "Respuesta del agente de facturación"
    
    def test_routing_basico(self):
        """Test básico de routing entre agentes"""
        # Por ahora, el swarm solo tiene el agente Rswarm
        swarm = Swarm([self.rswarm])
        
        mensaje = "Necesito una cita"
        respuesta = swarm.handle(mensaje)
        
        # Debería responder el agente Rswarm
        assert "día" in respuesta.lower()
    
    def test_swarm_con_multiple_agentes(self):
        """Test con múltiples agentes en el swarm"""
        # Crear swarm con múltiples agentes
        swarm = Swarm([self.rswarm, self.agente_citas, self.agente_soporte])
        
        # Por ahora, el comportamiento es usar el primer agente
        mensaje = "Hola"
        respuesta = swarm.handle(mensaje)
        
        # Debería responder el agente Rswarm
        assert "rswarm" in respuesta.lower()
    
    def test_escalacion_agente(self):
        """Test para simular escalación a agente especializado"""
        # Simular que el agente Rswarm no puede manejar algo y escala
        self.rswarm.handle = Mock(side_effect=lambda x: "Escalando a especialista" if "complejo" in x else "Respuesta normal")
        
        swarm = Swarm([self.rswarm, self.agente_soporte])
        
        # Mensaje simple
        respuesta_simple = swarm.handle("Hola")
        assert "normal" in respuesta_simple
        
        # Mensaje complejo
        respuesta_compleja = swarm.handle("Problema complejo")
        assert "escalando" in respuesta_compleja.lower()


@pytest.mark.slow
class TestEscenariosCarga:
    """Tests de carga y stress (marcados como slow)"""
    
    def setup_method(self):
        self.rswarm = Rswarm()
        self.swarm = Swarm([self.rswarm])
    
    def test_muchos_usuarios_simultaneos(self):
        """Simular muchos usuarios enviando mensajes simultáneamente"""
        import threading
        import time
        
        resultados = []
        errores = []
        
        def enviar_mensaje(mensaje, indice):
            try:
                respuesta = self.swarm.handle(mensaje)
                resultados.append((indice, respuesta))
            except Exception as e:
                errores.append((indice, str(e)))
        
        # Crear múltiples hilos simulando usuarios concurrentes
        threads = []
        for i in range(50):
            mensaje = f"Mensaje del usuario {i}"
            thread = threading.Thread(target=enviar_mensaje, args=(mensaje, i))
            threads.append(thread)
            thread.start()
        
        # Esperar a que todos los hilos terminen
        for thread in threads:
            thread.join()
        
        # Verificar resultados
        assert len(resultados) == 50
        assert len(errores) == 0
        assert all(len(resp) > 0 for _, resp in resultados)
    
    def test_conversacion_muy_larga(self):
        """Test para conversación extremadamente larga"""
        mensajes = ["Hola"] * 1000
        
        import time
        start_time = time.time()
        
        respuestas = []
        for mensaje in mensajes:
            respuesta = self.swarm.handle(mensaje)
            respuestas.append(respuesta)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Verificar resultados
        assert len(respuestas) == 1000
        assert all(len(resp) > 0 for resp in respuestas)
        assert processing_time < 5.0  # Debería procesar 1000 mensajes en menos de 5 segundos 