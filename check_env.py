import sys
print("Python is running")
try:
    import pydantic
    print("Pydantic is installed")
    import fastapi
    print("FastAPI is installed")
except ImportError as e:
    print(f"Import Error: {e}")
print("Done")
