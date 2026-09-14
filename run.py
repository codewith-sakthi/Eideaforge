"""
run.py – Root startup script for Eideaforge (starts backend API & serves frontend).
"""
import sys
import os

# Add backend directory to sys.path
backend_path = os.path.join(os.path.dirname(__file__), "backend")
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app import create_app
from config import Config

if __name__ == "__main__":
    app = create_app()
    print("=" * 60)
    print("🚀 Eideaforge Server Running at http://localhost:5000")
    print("=" * 60)
    app.run(
        host="0.0.0.0",
        port=Config.PORT,
        debug=Config.DEBUG,
    )
