"""
House Price Prediction System
A production-ready end-to-end data science project demonstrating
advanced ML practices, API development, and deployment.

Version: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "CODTECH Internship"
__description__ = "Advanced House Price Prediction with FastAPI and Ensemble Learning"

from .config import (
    PROJECT_ROOT,
    DATA_DIR,
    MODEL_DIR,
    LOGS_DIR,
    API_HOST,
    API_PORT,
)

__all__ = [
    "PROJECT_ROOT",
    "DATA_DIR",
    "MODEL_DIR",
    "LOGS_DIR",
    "API_HOST",
    "API_PORT",
]
