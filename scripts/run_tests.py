#!/usr/bin/env python3
"""
Script para ejecutar tests con diferentes configuraciones
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(command, description):
    """Ejecuta un comando y muestra el resultado"""
    print(f"\n{'='*60}")
    print(f"🔄 {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        
        if result.stdout:
            print("✅ Salida:")
            print(result.stdout)
        
        if result.stderr:
            print("⚠️  Errores:")
            print(result.stderr)
        
        if result.returncode == 0:
            print(f"✅ {description} completado exitosamente")
        else:
            print(f"❌ {description} falló con código {result.returncode}")
        
        return result.returncode == 0
    
    except Exception as e:
        print(f"❌ Error ejecutando {description}: {e}")
        return False


def main():
    """Función principal"""
    print("🧪 Ejecutando suite de tests para Rswarm")
    
    # Cambiar al directorio raíz del proyecto
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    # Lista de comandos a ejecutar
    commands = [
        ("pytest tests/ -v --tb=short", "Tests unitarios básicos"),
        ("pytest tests/ -v -m 'not integration'", "Tests unitarios (sin integración)"),
        ("pytest tests/ -v -m integration", "Tests de integración"),
        ("pytest tests/ --cov=. --cov-report=html", "Tests con cobertura"),
        ("pytest tests/ -v --durations=10", "Tests con tiempos de ejecución"),
        ("python -m black . --check", "Verificación de formato con Black"),
        ("python -m flake8 .", "Verificación de estilo con Flake8"),
    ]
    
    results = []
    
    for command, description in commands:
        success = run_command(command, description)
        results.append((description, success))
    
    # Resumen final
    print(f"\n{'='*60}")
    print("📊 RESUMEN DE TESTS")
    print(f"{'='*60}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for description, success in results:
        status = "✅ PASÓ" if success else "❌ FALLÓ"
        print(f"{status}: {description}")
    
    print(f"\n🎯 Resultado: {passed}/{total} tests pasaron")
    
    if passed == total:
        print("🎉 ¡Todos los tests pasaron exitosamente!")
        return 0
    else:
        print("⚠️  Algunos tests fallaron. Revisa los errores arriba.")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 