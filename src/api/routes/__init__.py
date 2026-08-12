"""
API route modules.
"""
from fastapi import APIRouter

# Import individual route modules
from . import exchange_rates, commodities, dollar_index, signals, backtesting, health, websocket

__all__ = [
    'exchange_rates',
    'commodities', 
    'dollar_index',
    'signals',
    'backtesting',
    'health',
    'websocket'
]
