#!/usr/bin/env python3
import os
import sys
import shutil
import subprocess
import zipfile
from pathlib import Path


def create_lambda_layer_from_requirements(requirements_file: str, layer_name: str = "lambda-layer", output_dir: str = "output"):    
    python_dir = Path("python")
    
    try:
        if python_dir.exists():
            shutil.rmtree(python_dir)
        python_dir.mkdir(parents=True)
        
        req_path = Path(requirements_file)
        if not req_path.exists():
            print(f"Error: No se encontró {requirements_file}")
            return None
        
        print(f"\nCreando layer con librerías desde {requirements_file}")
        
        result = subprocess.run([
            sys.executable, "-m", "pip", "install",
            "-r", str(req_path),
            "-t", str(python_dir)
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Error instalando dependencias:")
            print(result.stderr)
            return None
        
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        zip_filename = f"{layer_name}.zip"
        zip_path = output_path / zip_filename
        
        # Crear el archivo ZIP con la carpeta python/
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(python_dir):
                for file in files:
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(python_dir.parent)
                    zipf.write(file_path, arcname)
        
        shutil.rmtree(python_dir)
        
        file_size = zip_path.stat().st_size / (1024 * 1024)  # MB
        print(f"\n✓ Lambda Layer creado exitosamente")
        print(f"  Nombre: {layer_name}")
        print(f"  Tamaño: {file_size:.2f} MB")
        print(f"  Ubicación: {zip_path}")
        print(f"  Librerías incluidas:")
        
        # Mostrar librerías
        with open(req_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    print(f"    - {line}")
        
        return str(zip_path.absolute())
        
    except Exception as e:
        print(f"Error: {e}")
        if python_dir.exists():
            shutil.rmtree(python_dir)
        return None


def main():
    
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        
        if arg.endswith('.txt'):
            layer_name = sys.argv[2] if len(sys.argv) > 2 else "lambda-layer"
            create_lambda_layer_from_requirements(arg, layer_name)
        else:
            print("Por favor proporciona un archivo requirements.txt")
    else:
        # Menú interactivo
        print("\n=== Creador de Lambda Layers ===")
        
        requirements_file = input("Ruta del archivo requirements.txt: ").strip()
        layer_name = input("Nombre de la layer (Enter para 'lambda-layer'): ").strip()
        if not layer_name:
            layer_name = "lambda-layer"
        create_lambda_layer_from_requirements(requirements_file, layer_name)

if __name__ == "__main__":
    main()
