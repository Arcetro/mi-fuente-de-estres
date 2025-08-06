@echo off
echo ========================================
echo    INICIANDO ENTORNO DE DESARROLLO
echo    Prototipo Rswarm - Testing
echo ========================================
echo.

:: Verificar que Docker esté corriendo
echo [1/5] Verificando Docker...
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker no está instalado o no está corriendo
    echo Por favor, inicia Docker Desktop y vuelve a intentar
    pause
    exit /b 1
)
echo ✓ Docker está disponible

:: Verificar que Docker Compose esté disponible
echo [2/5] Verificando Docker Compose...
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker Compose no está disponible
    pause
    exit /b 1
)
echo ✓ Docker Compose está disponible

:: Construir la imagen si no existe
echo [3/5] Construyendo imagen Docker (si es necesario)...
docker-compose -f docker-compose.dev.yml build --no-cache
if %errorlevel% neq 0 (
    echo ERROR: Fallo al construir la imagen Docker
    pause
    exit /b 1
)
echo ✓ Imagen Docker lista

:: Iniciar el contenedor de desarrollo
echo [4/5] Iniciando contenedor de desarrollo...
docker-compose -f docker-compose.dev.yml up -d rswarm-dev
if %errorlevel% neq 0 (
    echo ERROR: Fallo al iniciar el contenedor
    pause
    exit /b 1
)
echo ✓ Contenedor de desarrollo iniciado

:: Ejecutar tests para verificar que todo funciona
echo [5/5] Ejecutando tests de verificación...
docker-compose -f docker-compose.dev.yml run --rm rswarm-test
if %errorlevel% neq 0 (
    echo ADVERTENCIA: Algunos tests fallaron, pero el entorno está listo
) else (
    echo ✓ Todos los tests pasaron
)

echo.
echo ========================================
echo    ¡ENTORNO LISTO!
echo ========================================
echo.
echo Comandos útiles:
echo.
echo • Ejecutar tests completos:
echo   docker-compose -f docker-compose.dev.yml run --rm rswarm-test
echo.
echo • Ejecutar la aplicación:
echo   docker-compose -f docker-compose.dev.yml exec rswarm-dev python recepcionista_simple.py
echo.
echo • Entrar al contenedor:
echo   docker-compose -f docker-compose.dev.yml exec rswarm-dev bash
echo.
echo • Ver logs:
echo   docker-compose -f docker-compose.dev.yml logs rswarm-dev
echo.
echo • Detener entorno:
echo   docker-compose -f docker-compose.dev.yml down
echo.
pause 