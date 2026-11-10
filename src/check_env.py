"""Environment check for the Digital Advertising Budget Optimizer project."""
import importlib
import platform
import shutil
import subprocess
import sys

print("Environment Check")
print("-" * 40)
print(f"Python version : {sys.version.split()[0]}")
print(f"Platform       : {platform.system()} {platform.release()}")
print()

# Libraries needed in this project
packages = ["numpy", "pandas", "scipy", "matplotlib", "seaborn", "pyarrow", "pyspark"]

print(f"{'Package':<12}{'Status':<10}Version")
for name in packages:
    try:
        module = importlib.import_module(name)
        print(f"{name:<12}{'OK':<10}{getattr(module, '__version__', 'n/a')}")
    except ImportError:
        print(f"{name:<12}{'MISSING':<10}-")

# Java is required by PySpark
print()
if shutil.which("java"):
    result = subprocess.run(["java", "-version"], capture_output=True, text=True)
    print(f"Java           : found ({result.stderr.splitlines()[0]})")
else:
    print("Java           : NOT FOUND")