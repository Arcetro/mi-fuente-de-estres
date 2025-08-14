#!/bin/bash

# Script para desarrollo con Docker
# Uso: ./scripts/docker-dev.sh [comando]

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para mostrar ayuda
show_help() {
    echo -e "${BLUE}Rswarm - Script de Desarrollo Docker${NC}"
    echo ""
    echo "Uso: $0 [comando]"
    echo ""
    echo "Comandos disponibles:"
    echo "  build     - Construir la imagen Docker"
    echo "  dev       - Iniciar entorno de desarrollo"
    echo "  test      - Ejecutar tests"
    echo "  run       - Ejecutar la aplicación"
    echo "  shell     - Abrir shell en el container"
    echo "  logs      - Mostrar logs del container"
    echo "  stop      - Detener todos los containers"
    echo "  clean     - Limpiar containers e imágenes"
    echo "  help      - Mostrar esta ayuda"
    echo ""
}

# Función para construir la imagen
build_image() {
    echo -e "${YELLOW}🔨 Construyendo imagen Docker...${NC}"
    docker-compose build
    echo -e "${GREEN}✅ Imagen construida exitosamente${NC}"
}

# Función para iniciar entorno de desarrollo
start_dev() {
    echo -e "${YELLOW}🚀 Iniciando entorno de desarrollo...${NC}"
    docker-compose up -d rswarm-dev
    echo -e "${GREEN}✅ Entorno de desarrollo iniciado${NC}"
    echo -e "${BLUE}💡 Para acceder al container: $0 shell${NC}"
}

# Función para ejecutar tests
run_tests() {
    echo -e "${YELLOW}🧪 Ejecutando tests...${NC}"
    docker-compose run --rm rswarm-test
}

# Función para ejecutar la aplicación
run_app() {
    echo -e "${YELLOW}🎯 Ejecutando aplicación...${NC}"
    docker-compose up rswarm-run
}

# Función para abrir shell en el container
open_shell() {
    echo -e "${YELLOW}🐚 Abriendo shell en el container...${NC}"
    docker-compose exec rswarm-dev /bin/bash
}

# Función para mostrar logs
show_logs() {
    echo -e "${YELLOW}📋 Mostrando logs...${NC}"
    docker-compose logs -f rswarm-dev
}

# Función para detener containers
stop_containers() {
    echo -e "${YELLOW}🛑 Deteniendo containers...${NC}"
    docker-compose down
    echo -e "${GREEN}✅ Containers detenidos${NC}"
}

# Función para limpiar
clean_all() {
    echo -e "${YELLOW}🧹 Limpiando containers e imágenes...${NC}"
    docker-compose down --rmi all --volumes --remove-orphans
    echo -e "${GREEN}✅ Limpieza completada${NC}"
}

# Función para ejecutar comandos personalizados
run_custom_command() {
    echo -e "${YELLOW}⚡ Ejecutando comando personalizado: $1${NC}"
    docker-compose exec rswarm-dev "$@"
}

# Verificar si Docker está instalado
check_docker() {
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker no está instalado${NC}"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        echo -e "${RED}❌ Docker Compose no está instalado${NC}"
        exit 1
    fi
}

# Función principal
main() {
    check_docker
    
    case "${1:-help}" in
        build)
            build_image
            ;;
        dev)
            start_dev
            ;;
        test)
            run_tests
            ;;
        run)
            run_app
            ;;
        shell)
            open_shell
            ;;
        logs)
            show_logs
            ;;
        stop)
            stop_containers
            ;;
        clean)
            clean_all
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            # Si no es un comando conocido, intentar ejecutarlo en el container
            if [ $# -gt 0 ]; then
                run_custom_command "$@"
            else
                show_help
            fi
            ;;
    esac
}

# Ejecutar función principal
main "$@" 