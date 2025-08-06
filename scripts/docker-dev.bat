@echo off
REM Script para desarrollo con Docker en Windows
REM Uso: scripts\docker-dev.bat [comando]

setlocal enabledelayedexpansion

REM Colores para output (Windows)
set "RED=[91m"
set "GREEN=[92m"
set "YELLOW=[93m"
set "BLUE=[94m"
set "NC=[0m"

REM Función para mostrar ayuda
:show_help
echo %BLUE%Rswarm - Script de Desarrollo Docker%NC%
echo.
echo Uso: %0 [comando]
echo.
echo Comandos disponibles:
echo   build     - Construir la imagen Docker
echo   dev       - Iniciar entorno de desarrollo
echo   test      - Ejecutar tests
echo   run       - Ejecutar la aplicación
echo   shell     - Abrir shell en el container
echo   logs      - Mostrar logs del container
echo   stop      - Detener todos los containers
echo   clean     - Limpiar containers e imágenes
echo   help      - Mostrar esta ayuda
echo.
goto :eof

REM Función para construir la imagen
:build_image
echo %YELLOW%🔨 Construyendo imagen Docker...%NC%
docker-compose build
if %errorlevel% equ 0 (
    echo %GREEN%✅ Imagen construida exitosamente%NC%
) else (
    echo %RED%❌ Error construyendo imagen%NC%
)
goto :eof

REM Función para iniciar entorno de desarrollo
:start_dev
echo %YELLOW%🚀 Iniciando entorno de desarrollo...%NC%
docker-compose up -d rswarm-dev
if %errorlevel% equ 0 (
    echo %GREEN%✅ Entorno de desarrollo iniciado%NC%
    echo %BLUE%💡 Para acceder al container: %0 shell%NC%
) else (
    echo %RED%❌ Error iniciando entorno de desarrollo%NC%
)
goto :eof

REM Función para ejecutar tests
:run_tests
echo %YELLOW%🧪 Ejecutando tests...%NC%
docker-compose run --rm rswarm-test
goto :eof

REM Función para ejecutar la aplicación
:run_app
echo %YELLOW%🎯 Ejecutando aplicación...%NC%
docker-compose up rswarm-run
goto :eof

REM Función para abrir shell en el container
:open_shell
echo %YELLOW%🐚 Abriendo shell en el container...%NC%
docker-compose exec rswarm-dev /bin/bash
goto :eof

REM Función para mostrar logs
:show_logs
echo %YELLOW%📋 Mostrando logs...%NC%
docker-compose logs -f rswarm-dev
goto :eof

REM Función para detener containers
:stop_containers
echo %YELLOW%🛑 Deteniendo containers...%NC%
docker-compose down
if %errorlevel% equ 0 (
    echo %GREEN%✅ Containers detenidos%NC%
) else (
    echo %RED%❌ Error deteniendo containers%NC%
)
goto :eof

REM Función para limpiar
:clean_all
echo %YELLOW%🧹 Limpiando containers e imágenes...%NC%
docker-compose down --rmi all --volumes --remove-orphans
if %errorlevel% equ 0 (
    echo %GREEN%✅ Limpieza completada%NC%
) else (
    echo %RED%❌ Error en limpieza%NC%
)
goto :eof

REM Verificar si Docker está instalado
:check_docker
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo %RED%❌ Docker no está instalado%NC%
    exit /b 1
)

docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo %RED%❌ Docker Compose no está instalado%NC%
    exit /b 1
)
goto :eof

REM Función principal
:main
call :check_docker
if %errorlevel% neq 0 exit /b 1

if "%1"=="" goto show_help
if "%1"=="help" goto show_help
if "%1"=="--help" goto show_help
if "%1"=="-h" goto show_help

if "%1"=="build" goto build_image
if "%1"=="dev" goto start_dev
if "%1"=="test" goto run_tests
if "%1"=="run" goto run_app
if "%1"=="shell" goto open_shell
if "%1"=="logs" goto show_logs
if "%1"=="stop" goto stop_containers
if "%1"=="clean" goto clean_all

REM Si no es un comando conocido, intentar ejecutarlo en el container
echo %YELLOW%⚡ Ejecutando comando personalizado: %*%NC%
docker-compose exec rswarm-dev %*
goto :eof

REM Ejecutar función principal
call :main %* 