#!/usr/bin/env python3
import schedule
import time
import subprocess
import sys
import os

def run_discovery():
    print("🔄 Ejecutando descubrimiento de APIs...")
    result = subprocess.run([sys.executable, "scripts/discovery/basic_discovery.py"], 
                          capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(f"STDERR: {result.stderr}")

def run_wrapper_generation():
    print("🔄 Generando wrappers...")
    result = subprocess.run([sys.executable, "scripts/wrapper/auto_wrapper.py"], 
                          capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(f"STDERR: {result.stderr}")

def run_deployment():
    print("🔄 Desplegando APIs...")
    result = subprocess.run([sys.executable, "scripts/deployment/auto_deploy.py"], 
                          capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(f"STDERR: {result.stderr}")

def main():
    print("🚀 INICIANDO SISTEMA AUTOMATIZADO DE INGRESOS PASIVOS")
    print("=" * 60)
    
    # Ejecutar inmediatamente
    run_discovery()
    time.sleep(5)
    run_wrapper_generation()
    time.sleep(5)
    run_deployment()
    
    print("✅ Ejecución inicial completada!")
    print("📊 El sistema se ejecutará automáticamente cada 6 horas")
    
    # Programar ejecuciones automáticas
    schedule.every(6).hours.do(run_discovery)
    schedule.every(6).hours.do(run_wrapper_generation)
    schedule.every(12).hours.do(run_deployment)
    
    # Mantener el script corriendo
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main()
