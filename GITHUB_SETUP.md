# Configuración del Repositorio GitHub

## Pasos para subir el proyecto a GitHub:

### 1. Crear el repositorio en GitHub
1. Ve a [GitHub.com](https://github.com)
2. Haz clic en el botón verde "New" o "+" en la esquina superior derecha
3. Selecciona "New repository"
4. Configura el repositorio:
   - **Repository name**: `prototipo-swarm`
   - **Description**: `Sistema de recepcionista basado en agentes swarms con entorno de testing completo`
   - **Visibility**: Public o Private (según tu preferencia)
   - **NO** marques "Add a README file" (ya tenemos uno)
   - **NO** marques "Add .gitignore" (ya tenemos uno)
   - **NO** marques "Choose a license" (por ahora)

### 2. Conectar el repositorio local con GitHub
Una vez creado el repositorio, GitHub te mostrará comandos. Usa estos:

```bash
# Agregar el repositorio remoto
git remote add origin https://github.com/TU_USUARIO/prototipo-swarm.git

# Cambiar el nombre de la rama principal (opcional, GitHub ahora usa 'main' por defecto)
git branch -M main

# Subir el código
git push -u origin main
```

### 3. Verificar que todo esté subido
```bash
git status
git log --oneline
```

## Estructura del proyecto que se subirá:

```
prototipo-swarm/
├── README.md                 # Documentación completa del proyecto
├── recepcionista_simple.py   # Versión ligera del recepcionista
├── recepcionista_swarm.py    # Versión original con swarms
├── requirements.txt          # Dependencias completas
├── requirements-dev.txt      # Dependencias ligeras para desarrollo
├── Dockerfile               # Docker para producción
├── Dockerfile.dev           # Docker para desarrollo
├── docker-compose.yml       # Compose para producción
├── docker-compose.dev.yml   # Compose para desarrollo
├── pytest.ini              # Configuración de pytest
├── tests/                   # Suite completa de tests
│   ├── test_recepcionista.py
│   ├── test_integration.py
│   ├── test_scenarios.py
│   └── conftest.py
├── scripts/                 # Scripts de automatización
│   ├── docker-dev.sh
│   ├── docker-dev.bat
│   └── run_tests.py
└── .gitignore              # Archivos a ignorar
```

## Características del proyecto:

✅ **Entorno Docker completo** - Desarrollo y producción  
✅ **Suite de tests completa** - 34 tests pasando  
✅ **Documentación detallada** - README con instrucciones  
✅ **Scripts de automatización** - Para Windows y Linux/Mac  
✅ **Configuración optimizada** - Sin dependencias pesadas  
✅ **Estructura escalable** - Preparado para múltiples agentes  

## Próximos pasos después de subir:

1. **Configurar GitHub Actions** para CI/CD
2. **Agregar badges** al README
3. **Crear releases** con versiones
4. **Configurar issues templates**
5. **Agregar más agentes especializados** 