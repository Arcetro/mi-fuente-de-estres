# Rswarm - Laboratorio

## Requisitos
- Python 3.8+
- Docker y Docker Compose (recomendado para desarrollo)

## 🐳 Desarrollo con Docker (Recomendado)

### Configuración rápida

```bash
# Construir la imagen
docker-compose build

# Iniciar entorno de desarrollo
docker-compose up -d rswarm-dev

# Acceder al container
docker-compose exec rswarm-dev /bin/bash
```

### Scripts de desarrollo

#### En Linux/Mac:
```bash
# Mostrar ayuda
./scripts/docker-dev.sh help

# Construir imagen
./scripts/docker-dev.sh build

# Iniciar desarrollo
./scripts/docker-dev.sh dev

# Ejecutar tests
./scripts/docker-dev.sh test

# Ejecutar aplicación
./scripts/docker-dev.sh run

# Abrir shell
./scripts/docker-dev.sh shell
```

#### En Windows:
```cmd
# Mostrar ayuda
scripts\docker-dev.bat help

# Construir imagen
scripts\docker-dev.bat build

# Iniciar desarrollo
scripts\docker-dev.bat dev

# Ejecutar tests
scripts\docker-dev.bat test

# Ejecutar aplicación
scripts\docker-dev.bat run

# Abrir shell
scripts\docker-dev.bat shell
```

## 🖥️ Interfaz de Monitoreo

Una vez que la aplicación está corriendo con el comando `dev`, puedes acceder a la interfaz de monitoreo en tu navegador:

[http://localhost:8000/](http://localhost:8000/)

Esta interfaz muestra un historial de los mensajes recibidos y enviados por la aplicación, y se actualiza automáticamente cada 5 segundos.

## 📦 Instalación local (Alternativa)

```bash
python -m venv .venv
.venv\Scripts\activate  # En Windows
pip install -r requirements.txt
# La aplicación principal ahora es web/app.py y se recomienda correr con Docker.
```

## 🧪 Entorno de Testing

### Con Docker (Recomendado)
```bash
# Ejecutar todos los tests
docker-compose run --rm rswarm-test

# O usando el script
./scripts/docker-dev.sh test
```

### Localmente
```bash
# Tests básicos
pytest tests/ -v

# Tests unitarios (sin integración)
pytest tests/ -v -m "not integration"

# Tests de integración
pytest tests/ -v -m integration

# Tests con cobertura
pytest tests/ --cov=. --cov-report=html

# Tests de performance (marcados como slow)
pytest tests/ -v -m slow

# Ejecutar todos los tests con el script
python scripts/run_tests.py
```

### Estructura de Tests

```
tests/
├── __init__.py
├── conftest.py              # Configuración y fixtures
├── test_recepcionista.py    # Tests unitarios básicos
├── test_integration.py      # Tests de integración
└── test_scenarios.py        # Escenarios reales y casos edge
```

### Tipos de Tests

- **Unitarios**: Prueban funciones individuales
- **Integración**: Prueban el flujo completo del sistema
- **Escenarios**: Simulan casos de uso reales
- **Performance**: Prueban rendimiento y carga
- **Edge Cases**: Casos límite y especiales

## 🏗️ Estructura del Proyecto

```
Swarm/
├── Dockerfile              # Configuración de Docker
├── docker-compose.yml      # Orquestación de servicios
├── .dockerignore          # Archivos a ignorar en Docker
├── requirements.txt       # Dependencias de Python
├── web/app.py             # Aplicación principal (web)
├── pytest.ini            # Configuración de pytest
├── scripts/               # Scripts de desarrollo
│   ├── docker-dev.sh     # Script Docker (Linux/Mac)
│   ├── docker-dev.bat    # Script Docker (Windows)
│   └── run_tests.py      # Script de tests
├── tests/                 # Suite de tests
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_recepcionista.py
│   ├── test_integration.py
│   └── test_scenarios.py
└── README.md             # Documentación
```

## ¿Cómo funciona?
- **Recepción de Mensajes:** La aplicación recibe mensajes a través de un webhook, simulando una conexión con la API de WhatsApp.
- **Procesamiento por Agentes:** Los mensajes son procesados por una serie de agentes (`tier1`, `tier2`) que determinan la intención y complejidad.
- **Registro en Base de Datos:** Todos los mensajes entrantes y salientes son registrados en una base de datos SQLite.
- **Interfaz de Monitoreo:** Una interfaz web en `http://localhost:8000/` muestra el historial de mensajes en tiempo real.

## 🚀 Próximos Pasos
- [ ] Agregar más agentes especializados
- [ ] Implementar sistema de routing inteligente
- [ ] Integrar procesamiento de lenguaje natural
- [ ] Conectar con APIs reales (WhatsApp, Telegram)
- [X] Agregar base de datos para historial
- [X] Crear interfaz web de monitoreo

## 🐛 Troubleshooting

### Problemas con Docker
```bash
# Limpiar todo y reconstruir
docker-compose down --rmi all --volumes --remove-orphans
docker-compose build --no-cache

# Ver logs
docker-compose logs rswarm-dev
```

### Problemas con dependencias locales
```bash
# Reinstalar dependencias
pip uninstall -r requirements.txt -y
pip install -r requirements.txt
```