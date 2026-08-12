"""
API module for trading infrastructure.
Provides REST endpoints for dollar price data types.
"""
from fastapi import FastAPI
from .main import create_app

__all__ = ['create_app']
