# 🚀 Inicio Rápido - Prototipo Rswarm

## Después de apagar y encender la computadora

### Opción 1: Script Automático (Recomendado)

#### Windows:
```bash
# Navegar al directorio del proyecto
cd C:\Users\Stephano\Desktop\Swarm

# Ejecutar script de inicio
scripts\start-dev.bat
```

#### Linux/Mac:
```bash
# Navegar al directorio del proyecto
cd ~/Desktop/Swarm

# Dar permisos de ejecución (solo la primera vez)
chmod +x scripts/start-dev.sh

# Ejecutar script de inicio
./scripts/start-dev.sh
```

### Opción 2: Comandos Manuales

Si prefieres hacerlo paso a paso:

```bash
# 1. Navegar al directorio del proyecto
cd C:\Users\Stephano\Desktop\Swarm

# 2. Verificar que Docker esté corriendo
docker --version
docker-compose --version

# 3. Construir la imagen (solo si es necesario)
docker-compose -f docker-compose.dev.yml build

# 4. Iniciar el entorno de desarrollo
docker-compose -f docker-compose.dev.yml up -d rswarm-dev

# 5. Verificar que todo funciona
docker-compose -f docker-compose.dev.yml run --rm rswarm-test
```

## ✅ Verificación Rápida

Una vez que el entorno esté listo, puedes verificar que todo funciona:

```bash
# Ejecutar todos los tests
docker-compose -f docker-compose.dev.yml run --rm rswarm-test

# Deberías ver: "34 passed, 2 warnings"
```

## 🎯 Comandos Más Usados

```bash
# Ejecutar la aplicación
docker-compose -f docker-compose.dev.yml exec rswarm-dev python recepcionista_simple.py

# Entrar al contenedor para desarrollo
docker-compose -f docker-compose.dev.yml exec rswarm-dev bash

# Ver logs del contenedor
docker-compose -f docker-compose.dev.yml logs rswarm-dev

# Detener el entorno
docker-compose -f docker-compose.dev.yml down
```

## 🔧 Solución de Problemas

### Docker no está corriendo
- Inicia Docker Desktop
- Espera a que aparezca el ícono de Docker en la barra de tareas
- Vuelve a ejecutar el script

### Error de permisos (Linux/Mac)
```bash
chmod +x scripts/start-dev.sh
```

### Contenedor no inicia
```bash
# Ver logs detallados
docker-compose -f docker-compose.dev.yml logs

# Reconstruir desde cero
docker-compose -f docker-compose.dev.yml down
docker-compose -f docker-compose.dev.yml build --no-cache
docker-compose -f docker-compose.dev.yml up -d rswarm-dev
```

### Tests fallan
```bash
# Verificar que el contenedor esté corriendo
docker-compose -f docker-compose.dev.yml ps

# Reconstruir y probar
docker-compose -f docker-compose.dev.yml build --no-cache
docker-compose -f docker-compose.dev.yml run --rm rswarm-test
```

## 📁 Estructura del Proyecto

```
Swarm/
├── scripts/
│   ├── start-dev.bat     # Script de inicio para Windows
│   ├── start-dev.sh      # Script de inicio para Linux/Mac
│   └── run_tests.py      # Script para ejecutar tests
├── tests/                # Suite completa de tests
├── docker-compose.dev.yml # Configuración Docker para desarrollo
└── recepcionista_simple.py # Aplicación principal
```

## 🎉 ¡Listo!

Una vez que ejecutes el script de inicio, tendrás:
- ✅ Entorno Docker funcionando
- ✅ 34 tests pasando
- ✅ Aplicación lista para usar
- ✅ Documentación completa

¡Puedes empezar a desarrollar inmediatamente! 