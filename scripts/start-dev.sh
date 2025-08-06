#!/bin/bash

echo "========================================"
echo "   INICIANDO ENTORNO DE DESARROLLO"
echo "   Prototipo Rswarm - Testing"
echo "========================================"
echo

# Verificar que Docker esté corriendo
echo "[1/5] Verificando Docker..."
if ! command -v docker &> /dev/null; then
    echo "ERROR: Docker no está instalado"
    exit 1
fi

if ! docker info &> /dev/null; then
    echo "ERROR: Docker no está corriendo"
    echo "Por favor, inicia Docker y vuelve a intentar"
    exit 1
fi
echo "✓ Docker está disponible"

# Verificar que Docker Compose esté disponible
echo "[2/5] Verificando Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    echo "ERROR: Docker Compose no está disponible"
    exit 1
fi
echo "✓ Docker Compose está disponible"

# Construir la imagen si no existe
echo "[3/5] Construyendo imagen Docker (si es necesario)..."
if ! docker-compose -f docker-compose.dev.yml build --no-cache; then
    echo "ERROR: Fallo al construir la imagen Docker"
    exit 1
fi
echo "✓ Imagen Docker lista"

# Iniciar el contenedor de desarrollo
echo "[4/5] Iniciando contenedor de desarrollo..."
if ! docker-compose -f docker-compose.dev.yml up -d rswarm-dev; then
    echo "ERROR: Fallo al iniciar el contenedor"
    exit 1
fi
echo "✓ Contenedor de desarrollo iniciado"

# Ejecutar tests para verificar que todo funciona
echo "[5/5] Ejecutando tests de verificación..."
if docker-compose -f docker-compose.dev.yml run --rm rswarm-test; then
    echo "✓ Todos los tests pasaron"
else
    echo "ADVERTENCIA: Algunos tests fallaron, pero el entorno está listo"
fi

echo
echo "========================================"
echo "   ¡ENTORNO LISTO!"
echo "========================================"
echo
echo "Comandos útiles:"
echo
echo "• Ejecutar tests completos:"
echo "  docker-compose -f docker-compose.dev.yml run --rm rswarm-test"
echo
echo "• Ejecutar la aplicación:"
echo "  docker-compose -f docker-compose.dev.yml exec rswarm-dev python recepcionista_simple.py"
echo
echo "• Entrar al contenedor:"
echo "  docker-compose -f docker-compose.dev.yml exec rswarm-dev bash"
echo
echo "• Ver logs:"
echo "  docker-compose -f docker-compose.dev.yml logs rswarm-dev"
echo
echo "• Detener entorno:"
echo "  docker-compose -f docker-compose.dev.yml down"
echo 