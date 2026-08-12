"""
WebSocket API routes for real-time data streaming.
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from typing import Optional

from src.websocket_manager import get_websocket_manager

router = APIRouter()


@router.websocket("/ws/exchange_rates/{currency}")
async def websocket_exchange_rates(websocket: WebSocket, currency: str):
    """
    WebSocket endpoint for real-time exchange rate updates.
    
    Args:
        websocket: WebSocket connection
        currency: Currency code (e.g., EUR, GBP, JPY)
    """
    manager = get_websocket_manager()
    client_id = None
    
    try:
        # Get client IP from WebSocket
        client_ip = websocket.client.host if websocket.client else "unknown"
        
        # Accept connection and get client ID
        client_id = await manager.connect(websocket, client_ip)
        
        # Subscribe to exchange rate updates
        await manager.subscribe(client_id, "exchange_rate", currency.upper())
        
        # Keep connection alive and handle messages
        while True:
            data = await websocket.receive_text()
            # Handle client messages if needed
            await manager.handle_client_message(client_id, data)
            
    except WebSocketDisconnect:
        if client_id:
            await manager.disconnect(client_id)
    except Exception as e:
        if client_id:
            await manager.disconnect(client_id)
        raise


@router.websocket("/ws/dollar_index")
async def websocket_dollar_index(websocket: WebSocket):
    """
    WebSocket endpoint for real-time Dollar Index updates.
    
    Args:
        websocket: WebSocket connection
    """
    manager = get_websocket_manager()
    client_id = None
    
    try:
        client_ip = websocket.client.host if websocket.client else "unknown"
        client_id = await manager.connect(websocket, client_ip)
        
        # Subscribe to dollar index updates
        await manager.subscribe(client_id, "dollar_index", "DXY")
        
        while True:
            data = await websocket.receive_text()
            await manager.handle_client_message(client_id, data)
            
    except WebSocketDisconnect:
        if client_id:
            await manager.disconnect(client_id)
    except Exception as e:
        if client_id:
            await manager.disconnect(client_id)
        raise


@router.websocket("/ws/commodity_prices/{commodity}")
async def websocket_commodity_prices(websocket: WebSocket, commodity: str):
    """
    WebSocket endpoint for real-time commodity price updates.
    
    Args:
        websocket: WebSocket connection
        commodity: Commodity name or symbol (e.g., GOLD, XAUUSD)
    """
    manager = get_websocket_manager()
    client_id = None
    
    try:
        client_ip = websocket.client.host if websocket.client else "unknown"
        client_id = await manager.connect(websocket, client_ip)
        
        # Subscribe to commodity price updates
        await manager.subscribe(client_id, "commodity", commodity.upper())
        
        while True:
            data = await websocket.receive_text()
            await manager.handle_client_message(client_id, data)
            
    except WebSocketDisconnect:
        if client_id:
            await manager.disconnect(client_id)
    except Exception as e:
        if client_id:
            await manager.disconnect(client_id)
        raise


@router.get("/ws/status")
async def websocket_status():
    """
    Get WebSocket connection status.
    
    Returns:
        Current WebSocket manager status
    """
    manager = get_websocket_manager()
    return {
        "active_connections": len(manager.active_connections),
        "subscriptions": {
            data_type: {
                identifier: len(clients)
                for identifier, clients in identifiers.items()
            }
            for data_type, identifiers in manager.subscriptions.items()
        }
    }
