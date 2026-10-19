from pathlib import Path
from setuptools import setup, find_packages

# Directorio principal del proyecto
ROOT_DIR = Path(__file__).parent

# Leer la documentación del proyecto
readme_path = ROOT_DIR / "README.md"

if readme_path.exists():
    long_description = readme_path.read_text(encoding="utf-8")
else:
    long_description = "Librería de herramientas para robótica desarrollada en Python."

setup(
    name="SimpleRobotics",
    version="1.0.5.1",
    description="Librería de herramientas para robótica en Python",
    long_description=long_description,
    long_description_content_type="text/markdown",

    packages=find_packages("src"),
    package_dir={"": "src"},

    install_requires=[
        "numpy>=1.24",
        "matplotlib>=3.5",
        "sympy>=1.12",
        "trimesh>=3.9",
    ],

    include_package_data=True,
)