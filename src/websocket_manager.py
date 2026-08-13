"""
WebSocket streaming manager for real-time data updates.
Manages client connections, data polling, and message broadcasting.
"""
import asyncio
import json
import logging
import yaml
import os
from datetime import datetime, timezone, timedelta
from typing import Dict, Set, Optional, Any
from collections import defaultdict
from dataclasses import dataclass, asdict
from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from sqlalchemy import desc

from src.models import ExchangeRate, DollarIndex, CommodityPrice
from src.database import get_db
from src.queries import PriceQueries

logger = logging.getLogger(__name__)


@dataclass
class WebSocketConfig:
    """Configuration for WebSocket streaming."""
    # Polling intervals (in seconds)
    exchange_rate_interval: int = 5
    dollar_index_interval: int = 5
    commodity_interval: int = 5
    
    # Rate limiting
    max_connections_per_ip: int = 10
    connection_timeout: int = 300  # 5 minutes
    max_message_size: int = 1024 * 1024  # 1MB
    
    # Performance
    max_subscriptions_per_client: int = 50
    heartbeat_interval: int = 30
    heartbeat_timeout: int = 60
    
    # Batching
    batch_updates: bool = True
    batch_size: int = 10
    batch_timeout: float = 1.0


def load_websocket_config() -> WebSocketConfig:
    """
    Load WebSocket configuration from config/api.yml.
    
    Returns:
        WebSocketConfig instance with loaded settings
    """
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'api.yml')
    
    default_config = WebSocketConfig()
    
    try:
        with open(config_path, 'r') as f:
            config_data = yaml.safe_load(f)
        
        if config_data and 'websocket' in config_data and config_data['websocket'].get('enabled', True):
            ws_config = config_data['websocket']
            
            # Load polling intervals
            if 'polling' in ws_config:
                default_config.exchange_rate_interval = ws_config['polling'].get('exchange_rate_interval', 5)
                default_config.dollar_index_interval = ws_config['polling'].get('dollar_index_interval', 5)
                default_config.commodity_interval = ws_config['polling'].get('commodity_interval', 5)
            
            # Load rate limiting
            if 'rate_limiting' in ws_config:
                default_config.max_connections_per_ip = ws_config['rate_limiting'].get('max_connections_per_ip', 10)
                default_config.connection_timeout = ws_config['rate_limiting'].get('connection_timeout', 300)
                default_config.max_message_size = ws_config['rate_limiting'].get('max_message_size', 1048576)
            
            # Load performance settings
            if 'performance' in ws_config:
                default_config.max_subscriptions_per_client = ws_config['performance'].get('max_subscriptions_per_client', 50)
                default_config.heartbeat_interval = ws_config['performance'].get('heartbeat_interval', 30)
                default_config.heartbeat_timeout = ws_config['performance'].get('heartbeat_timeout', 60)
            
            # Load batching settings
            if 'batching' in ws_config:
                default_config.batch_updates = ws_config['batching'].get('enabled', True)
                default_config.batch_size = ws_config['batching'].get('batch_size', 10)
                default_config.batch_timeout = ws_config['batching'].get('batch_timeout', 1.0)
            
            logger.info(f"Loaded WebSocket configuration from {config_path}")
    except Exception as e:
        logger.warning(f"Failed to load WebSocket configuration from {config_path}: {e}")
        logger.info("Using default WebSocket configuration")
    
    return default_config
    heartbeat_interval: int = 30  # seconds
    heartbeat_timeout: int = 60  # seconds
    
    # Data batching
    batch_updates: bool = True
    batch_size: int = 10
    batch_timeout: float = 1.0  # seconds


class ConnectionManager:
    """Manages WebSocket client connections and subscriptions."""
    
    def __init__(self, config: WebSocketConfig):
        self.config = config
        # Active connections: {client_id: WebSocket}
        self.active_connections: Dict[str, WebSocket] = {}
        # Subscriptions: {data_type: {identifier: Set[client_id]}}
        self.subscriptions: Dict[str, Dict[str, Set[str]]] = defaultdict(
            lambda: defaultdict(set)
        )
        # Client subscriptions: {client_id: Set[(data_type, identifier)]}
        self.client_subscriptions: Dict[str, Set[tuple]] = defaultdict(set)
        # Connection metadata: {client_id: metadata}
        self.connection_metadata: Dict[str, Dict[str, Any]] = {}
        # IP connection counts: {ip: count}
        self.ip_connections: Dict[str, int] = defaultdict(int)
        # Last activity: {client_id: datetime}
        self.last_activity: Dict[str, datetime] = {}
        # Client counter
        self.client_counter = 0
        # Lock for thread-safe operations
        self._lock = asyncio.Lock()
    
    async def connect(self, websocket: WebSocket, client_ip: str) -> str:
        """
        Accept a new WebSocket connection.
        
        Args:
            websocket: WebSocket connection
            client_ip: Client IP address
            
        Returns:
            Client ID for the connection
            
        Raises:
            Exception: If connection limit exceeded
        """
        # Check rate limiting
        if self.ip_connections[client_ip] >= self.config.max_connections_per_ip:
            logger.warning(f"Connection limit exceeded for IP: {client_ip}")
            raise Exception(f"Maximum connections per IP ({self.config.max_connections_per_ip}) exceeded")
        
        await websocket.accept()
        
        # Generate client ID
        async with self._lock:
            self.client_counter += 1
            client_id = f"client_{self.client_counter}"
        
        # Store connection
        self.active_connections[client_id] = websocket
        self.ip_connections[client_ip] += 1
        self.last_activity[client_id] = datetime.now(timezone.utc)
        
        # Store metadata
        self.connection_metadata[client_id] = {
            'ip': client_ip,
            'connected_at': datetime.now(timezone.utc),
            'subscriptions': 0
        }
        
        logger.info(f"Client connected: {client_id} from {client_ip}")
        return client_id
    
    async def disconnect(self, client_id: str):
        """
        Handle client disconnection.
        
        Args:
            client_id: Client ID to disconnect
        """
        async with self._lock:
            if client_id in self.active_connections:
                # Remove from IP tracking
                client_ip = self.connection_metadata.get(client_id, {}).get('ip', 'unknown')
                self.ip_connections[client_ip] = max(0, self.ip_connections[client_ip] - 1)
                
                # Remove subscriptions
                for data_type, identifier in self.client_subscriptions[client_id]:
                    if identifier in self.subscriptions[data_type]:
                        self.subscriptions[data_type][identifier].discard(client_id)
                        if not self.subscriptions[data_type][identifier]:
                            del self.subscriptions[data_type][identifier]
                
                # Clean up
                del self.active_connections[client_id]
                del self.client_subscriptions[client_id]
                del self.connection_metadata[client_id]
                del self.last_activity[client_id]
                
                logger.info(f"Client disconnected: {client_id}")
    
    async def subscribe(self, client_id: str, data_type: str, identifier: str):
        """
        Subscribe a client to a data stream.
        
        Args:
            client_id: Client ID
            data_type: Type of data (exchange_rate, dollar_index, commodity)
            identifier: Currency code or commodity name
            
        Raises:
            Exception: If subscription limit exceeded
        """
        async with self._lock:
            # Check subscription limit
            if len(self.client_subscriptions[client_id]) >= self.config.max_subscriptions_per_client:
                raise Exception(f"Maximum subscriptions per client ({self.config.max_subscriptions_per_client}) exceeded")
            
            # Add subscription
            self.subscriptions[data_type][identifier].add(client_id)
            self.client_subscriptions[client_id].add((data_type, identifier))
            self.connection_metadata[client_id]['subscriptions'] = len(self.client_subscriptions[client_id])
            
            logger.info(f"Client {client_id} subscribed to {data_type}/{identifier}")
    
    async def unsubscribe(self, client_id: str, data_type: str, identifier: str):
        """
        Unsubscribe a client from a data stream.
        
        Args:
            client_id: Client ID
            data_type: Type of data
            identifier: Currency code or commodity name
        """
        async with self._lock:
            self.subscriptions[data_type][identifier].discard(client_id)
            self.client_subscriptions[client_id].discard((data_type, identifier))
            
            # Clean up empty subscription sets
            if not self.subscriptions[data_type][identifier]:
                del self.subscriptions[data_type][identifier]
            
            self.connection_metadata[client_id]['subscriptions'] = len(self.client_subscriptions[client_id])
            
            logger.info(f"Client {client_id} unsubscribed from {data_type}/{identifier}")
    
    async def send_personal_message(self, message: dict, client_id: str):
        """
        Send a message to a specific client.
        
        Args:
            message: Message dictionary
            client_id: Client ID
        """
        if client_id in self.active_connections:
            try:
                websocket = self.active_connections[client_id]
                await websocket.send_json(message)
                self.last_activity[client_id] = datetime.now(timezone.utc)
            except Exception as e:
                logger.error(f"Error sending message to {client_id}: {e}")
                await self.disconnect(client_id)
    
    async def broadcast(self, message: dict, data_type: str, identifier: str):
        """
        Broadcast a message to all subscribed clients.
        
        Args:
            message: Message dictionary
            data_type: Type of data
            identifier: Currency code or commodity name
        """
        if identifier in self.subscriptions[data_type]:
            disconnected_clients = []
            
            for client_id in self.subscriptions[data_type][identifier]:
                try:
                    await self.send_personal_message(message, client_id)
                except Exception as e:
                    logger.error(f"Error broadcasting to {client_id}: {e}")
                    disconnected_clients.append(client_id)
            
            # Clean up disconnected clients
            for client_id in disconnected_clients:
                await self.disconnect(client_id)
    
    def get_connection_count(self) -> int:
        """Get total number of active connections."""
        return len(self.active_connections)
    
    def get_subscription_count(self, data_type: str, identifier: str) -> int:
        """Get number of subscribers for a data stream."""
        return len(self.subscriptions[data_type].get(identifier, set()))
    
    async def check_heartbeat(self, client_id: str) -> bool:
        """
        Check if client is still alive based on heartbeat.
        
        Args:
            client_id: Client ID
            
        Returns:
            True if client is alive, False otherwise
        """
        if client_id not in self.last_activity:
            return False
        
        last_seen = self.last_activity[client_id]
        timeout = timedelta(seconds=self.config.heartbeat_timeout)
        
        if datetime.now(timezone.utc) - last_seen > timeout:
            logger.warning(f"Client {client_id} heartbeat timeout")
            await self.disconnect(client_id)
            return False
        
        return True
    
    async def cleanup_inactive_connections(self):
        """Clean up inactive connections based on timeout."""
        now = datetime.now(timezone.utc)
        timeout = timedelta(seconds=self.config.connection_timeout)
        
        inactive_clients = [
            client_id for client_id, metadata in self.connection_metadata.items()
            if now - metadata['connected_at'] > timeout
        ]
        
        for client_id in inactive_clients:
            logger.info(f"Cleaning up inactive client: {client_id}")
            await self.disconnect(client_id)


class DataStreamer:
    """Handles data polling and streaming to WebSocket clients."""
    
    def __init__(self, manager: ConnectionManager, config: WebSocketConfig):
        self.manager = manager
        self.config = config
        self.running = False
        self.tasks: Set[asyncio.Task] = set()
        # Track last sent data to avoid duplicates
        self.last_data: Dict[str, Dict[str, Any]] = {}
    
    async def start(self):
        """Start all data streaming tasks."""
        if self.running:
            return
        
        self.running = True
        logger.info("Starting data streaming tasks")
        
        # Start streaming tasks for each data type
        self.tasks.add(asyncio.create_task(self._stream_exchange_rates()))
        self.tasks.add(asyncio.create_task(self._stream_dollar_index()))
        self.tasks.add(asyncio.create_task(self._stream_commodity_prices()))
        self.tasks.add(asyncio.create_task(self._heartbeat_task()))
        self.tasks.add(asyncio.create_task(self._cleanup_task()))
    
    async def stop(self):
        """Stop all data streaming tasks."""
        if not self.running:
            return
        
        self.running = False
        logger.info("Stopping data streaming tasks")
        
        # Cancel all tasks
        for task in self.tasks:
            task.cancel()
        
        # Wait for tasks to complete
        await asyncio.gather(*self.tasks, return_exceptions=True)
        self.tasks.clear()
    
    async def _stream_exchange_rates(self):
        """Stream exchange rate updates."""
        while self.running:
            try:
                db = next(get_db())
                queries = PriceQueries(db)
                
                # Get all subscribed currencies
                if 'exchange_rate' in self.manager.subscriptions:
                    for currency in self.manager.subscriptions['exchange_rate'].keys():
                        try:
                            latest = queries.get_latest_exchange_rate(currency)
                            if latest:
                                data = {
                                    'type': 'exchange_rate',
                                    'currency': currency,
                                    'date': latest.date.isoformat(),
                                    'rate': latest.rate,
                                    'open': latest.open_price,
                                    'high': latest.high_price,
                                    'low': latest.low_price,
                                    'close': latest.close_price,
                                    'volume': latest.volume,
                                    'timestamp': datetime.now(timezone.utc).isoformat()
                                }
                                
                                # Check if data changed
                                data_key = f"exchange_rate_{currency}"
                                if data_key not in self.last_data or self._data_changed(data, self.last_data[data_key]):
                                    self.last_data[data_key] = data
                                    await self.manager.broadcast(data, 'exchange_rate', currency)
                        except Exception as e:
                            logger.error(f"Error streaming exchange rate for {currency}: {e}")
                
                db.close()
            except Exception as e:
                logger.error(f"Error in exchange rate streaming: {e}")
            
            await asyncio.sleep(self.config.exchange_rate_interval)
    
    async def _stream_dollar_index(self):
        """Stream dollar index updates."""
        while self.running:
            try:
                db = next(get_db())
                queries = PriceQueries(db)
                
                if 'dollar_index' in self.manager.subscriptions and 'DXY' in self.manager.subscriptions['dollar_index']:
                    latest = queries.get_latest_dollar_index()
                    if latest:
                        data = {
                            'type': 'dollar_index',
                            'date': latest.date.isoformat(),
                            'value': latest.value,
                            'open': latest.open_price,
                            'high': latest.high_price,
                            'low': latest.low_price,
                            'close': latest.close_price,
                            'volume': latest.volume,
                            'timestamp': datetime.now(timezone.utc).isoformat()
                        }
                        
                        # Check if data changed
                        data_key = "dollar_index_DXY"
                        if data_key not in self.last_data or self._data_changed(data, self.last_data[data_key]):
                            self.last_data[data_key] = data
                            await self.manager.broadcast(data, 'dollar_index', 'DXY')
                
                db.close()
            except Exception as e:
                logger.error(f"Error in dollar index streaming: {e}")
            
            await asyncio.sleep(self.config.dollar_index_interval)
    
    async def _stream_commodity_prices(self):
        """Stream commodity price updates."""
        while self.running:
            try:
                db = next(get_db())
                queries = PriceQueries(db)
                
                # Get all subscribed commodities
                if 'commodity' in self.manager.subscriptions:
                    for commodity in self.manager.subscriptions['commodity'].keys():
                        try:
                            latest = queries.get_latest_commodity_price(commodity=commodity)
                            if latest:
                                data = {
                                    'type': 'commodity',
                                    'commodity': latest.commodity,
                                    'symbol': latest.symbol,
                                    'date': latest.date.isoformat(),
                                    'price': latest.price,
                                    'unit': latest.unit,
                                    'open': latest.open_price,
                                    'high': latest.high_price,
                                    'low': latest.low_price,
                                    'close': latest.close_price,
                                    'volume': latest.volume,
                                    'timestamp': datetime.now(timezone.utc).isoformat()
                                }
                                
                                # Check if data changed
                                data_key = f"commodity_{commodity}"
                                if data_key not in self.last_data or self._data_changed(data, self.last_data[data_key]):
                                    self.last_data[data_key] = data
                                    await self.manager.broadcast(data, 'commodity', commodity)
                        except Exception as e:
                            logger.error(f"Error streaming commodity price for {commodity}: {e}")
                
                db.close()
            except Exception as e:
                logger.error(f"Error in commodity price streaming: {e}")
            
            await asyncio.sleep(self.config.commodity_interval)
    
    async def _heartbeat_task(self):
        """Send heartbeat messages to all clients."""
        while self.running:
            try:
                for client_id in list(self.manager.active_connections.keys()):
                    if await self.manager.check_heartbeat(client_id):
                        await self.manager.send_personal_message({
                            'type': 'heartbeat',
                            'timestamp': datetime.now(timezone.utc).isoformat()
                        }, client_id)
            except Exception as e:
                logger.error(f"Error in heartbeat task: {e}")
            
            await asyncio.sleep(self.config.heartbeat_interval)
    
    async def _cleanup_task(self):
        """Periodically clean up inactive connections."""
        while self.running:
            try:
                await self.manager.cleanup_inactive_connections()
            except Exception as e:
                logger.error(f"Error in cleanup task: {e}")
            
            await asyncio.sleep(60)  # Run every minute
    
    def _data_changed(self, new_data: dict, old_data: dict) -> bool:
        """
        Check if data has changed significantly.
        
        Args:
            new_data: New data dictionary
            old_data: Old data dictionary
            
        Returns:
            True if data changed, False otherwise
        """
        # Compare key fields
        for key in ['rate', 'value', 'price', 'date']:
            if key in new_data and key in old_data:
                if new_data[key] != old_data[key]:
                    return True
        
        return False


# Global instances
config = load_websocket_config()
manager = ConnectionManager(config)
streamer = DataStreamer(manager, config)


def get_websocket_manager() -> ConnectionManager:
    """Get the global connection manager."""
    return manager


def get_data_streamer() -> DataStreamer:
    """Get the global data streamer."""
    return streamer


def get_websocket_config() -> WebSocketConfig:
    """Get the WebSocket configuration."""
    return config
