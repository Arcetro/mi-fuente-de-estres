# 🚀 CÓMO EJECUTAR EL SCRIPT CUANDO VUELVAS

## 📍 Ubicación del Script

El script está en: `C:\Users\Stephano\Desktop\Swarm\scripts\start-dev.bat`

## 🎯 Pasos Exactos para Ejecutar

### 1. Abrir PowerShell o CMD
- Presiona `Windows + R`
- Escribe `powershell` y presiona Enter

### 2. Navegar al directorio del proyecto
```bash
cd C:\Users\Stephano\Desktop\Swarm
```

### 3. Ejecutar el script
```bash
scripts\start-dev.bat
```

## 🔄 Proceso Completo (Copia y Pega)

```bash
cd C:\Users\Stephano\Desktop\Swarm
scripts\start-dev.bat
```

## ✅ Lo que verás cuando funcione:

```
========================================
   INICIANDO ENTORNO DE DESARROLLO
   Prototipo Rswarm - Testing
========================================

[1/5] Verificando Docker...
✓ Docker está disponible

[2/5] Verificando Docker Compose...
✓ Docker Compose está disponible

[3/5] Construyendo imagen Docker (si es necesario)...
✓ Imagen Docker lista

[4/5] Iniciando contenedor de desarrollo...
✓ Contenedor de desarrollo iniciado

[5/5] Ejecutando tests de verificación...
✓ Todos los tests pasaron

========================================
   ¡ENTORNO LISTO!
========================================
```

## 🎯 Comandos para usar después:

```bash
# Ejecutar la aplicación
docker-compose -f docker-compose.dev.yml exec rswarm-dev python recepcionista_simple.py

# Ejecutar tests
docker-compose -f docker-compose.dev.yml run --rm rswarm-test

# Entrar al contenedor
docker-compose -f docker-compose.dev.yml exec rswarm-dev bash
```

## 🔧 Si algo falla:

### Docker no está corriendo:
1. Busca "Docker Desktop" en el menú inicio
2. Inícialo y espera a que aparezca el ícono en la barra de tareas
3. Vuelve a ejecutar el script

### Error de permisos:
- Ejecuta PowerShell como Administrador

### Script no funciona:
```bash
# Verificar que el archivo existe
dir scripts\start-dev.bat

# Si no existe, verificar la ubicación
dir C:\Users\Stephano\Desktop\Swarm\scripts\
```

## 📁 Estructura de archivos:

```
C:\Users\Stephano\Desktop\Swarm\
├── scripts\
│   └── start-dev.bat          ← AQUÍ ESTÁ EL SCRIPT
├── tests\                     ← Tests del proyecto
├── docker-compose.dev.yml     ← Configuración Docker
└── recepcionista_simple.py    ← Aplicación principal
```

## 🎉 ¡Listo!

Una vez que ejecutes `scripts\start-dev.bat`, tendrás todo el entorno funcionando en menos de 2 minutos. 