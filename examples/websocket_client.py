"""
WebSocket client example for testing real-time data streaming.
This script demonstrates how to connect to the WebSocket endpoints and receive live updates.
"""
import asyncio
import json
import websockets
from datetime import datetime
from typing import Optional


class WebSocketClient:
    """WebSocket client for connecting to the trading API."""
    
    def __init__(self, uri: str, port: int = 8000):
        """
        Initialize WebSocket client.
        
        Args:
            uri: WebSocket URI path (e.g., /ws/exchange_rates/EUR)
            port: Server port (default: 8000)
        """
        self.uri = f"ws://localhost:{port}{uri}"
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self.connected = False
        self.message_count = 0
    
    async def connect(self):
        """Connect to the WebSocket server."""
        try:
            print(f"Connecting to {self.uri}...")
            self.websocket = await websockets.connect(self.uri)
            self.connected = True
            print(f"Connected successfully at {datetime.utcnow().isoformat()}")
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from the WebSocket server."""
        if self.websocket:
            await self.websocket.close()
            self.connected = False
            print(f"Disconnected at {datetime.utcnow().isoformat()}")
    
    async def send_message(self, message: dict):
        """
        Send a message to the server.
        
        Args:
            message: Message dictionary
        """
        if self.websocket and self.connected:
            try:
                await self.websocket.send(json.dumps(message))
                print(f"Sent: {message}")
            except Exception as e:
                print(f"Error sending message: {e}")
    
    async def receive_messages(self, duration: int = 60):
        """
        Receive messages from the server for a specified duration.
        
        Args:
            duration: Duration in seconds to listen for messages
        """
        if not self.websocket or not self.connected:
            print("Not connected to server")
            return
        
        print(f"Listening for messages for {duration} seconds...")
        print("-" * 80)
        
        try:
            # Set timeout for the receive loop
            end_time = asyncio.get_event_loop().time() + duration
            
            while asyncio.get_event_loop().time() < end_time:
                try:
                    # Wait for message with timeout
                    message = await asyncio.wait_for(
                        self.websocket.recv(),
                        timeout=1.0
                    )
                    
                    data = json.loads(message)
                    self.message_count += 1
                    
                    # Pretty print the message
                    print(f"[{self.message_count}] {datetime.utcnow().strftime('%H:%M:%S')}")
                    print(json.dumps(data, indent=2))
                    print("-" * 80)
                    
                except asyncio.TimeoutError:
                    # Send periodic ping to keep connection alive
                    await self.send_message({"action": "ping"})
                    continue
                    
        except websockets.exceptions.ConnectionClosed:
            print("Connection closed by server")
        except Exception as e:
            print(f"Error receiving messages: {e}")
        
        print(f"Received {self.message_count} messages total")


async def test_exchange_rates(currency: str = "EUR", duration: int = 30):
    """
    Test exchange rate WebSocket endpoint.
    
    Args:
        currency: Currency code (e.g., EUR, GBP, JPY)
        duration: Duration in seconds to listen
    """
    print(f"\n{'='*80}")
    print(f"Testing Exchange Rates WebSocket: {currency}")
    print(f"{'='*80}\n")
    
    uri = f"/ws/exchange_rates/{currency}"
    client = WebSocketClient(uri)
    
    if await client.connect():
        try:
            await client.receive_messages(duration)
        finally:
            await client.disconnect()


async def test_dollar_index(duration: int = 30):
    """
    Test Dollar Index WebSocket endpoint.
    
    Args:
        duration: Duration in seconds to listen
    """
    print(f"\n{'='*80}")
    print(f"Testing Dollar Index WebSocket (DXY)")
    print(f"{'='*80}\n")
    
    uri = "/ws/dollar_index"
    client = WebSocketClient(uri)
    
    if await client.connect():
        try:
            await client.receive_messages(duration)
        finally:
            await client.disconnect()


async def test_commodity_prices(commodity: str = "GOLD", duration: int = 30):
    """
    Test commodity price WebSocket endpoint.
    
    Args:
        commodity: Commodity name (e.g., GOLD, SILVER, OIL)
        duration: Duration in seconds to listen
    """
    print(f"\n{'='*80}")
    print(f"Testing Commodity Prices WebSocket: {commodity}")
    print(f"{'='*80}\n")
    
    uri = f"/ws/commodity_prices/{commodity}"
    client = WebSocketClient(uri)
    
    if await client.connect():
        try:
            await client.receive_messages(duration)
        finally:
            await client.disconnect()


async def test_multiple_streams():
    """Test multiple WebSocket streams simultaneously."""
    print(f"\n{'='*80}")
    print(f"Testing Multiple WebSocket Streams Simultaneously")
    print(f"{'='*80}\n")
    
    # Create multiple clients
    clients = [
        WebSocketClient("/ws/exchange_rates/EUR"),
        WebSocketClient("/ws/dollar_index"),
        WebSocketClient("/ws/commodity_prices/GOLD"),
    ]
    
    # Connect all clients
    tasks = []
    for client in clients:
        if await client.connect():
            tasks.append(client.receive_messages(duration=30))
    
    # Run all clients simultaneously
    if tasks:
        await asyncio.gather(*tasks)
    
    # Disconnect all clients
    for client in clients:
        await client.disconnect()


async def test_unsubscribe(currency: str = "EUR"):
    """
    Test unsubscribe functionality.
    
    Args:
        currency: Currency code
    """
    print(f"\n{'='*80}")
    print(f"Testing Unsubscribe Functionality: {currency}")
    print(f"{'='*80}\n")
    
    uri = f"/ws/exchange_rates/{currency}"
    client = WebSocketClient(uri)
    
    if await client.connect():
        try:
            # Listen for a few messages
            print("Listening for initial messages...")
            await client.receive_messages(duration=10)
            
            # Send unsubscribe
            print("\nSending unsubscribe request...")
            await client.send_message({"action": "unsubscribe"})
            
            # Wait a bit to see if connection closes
            await asyncio.sleep(2)
            
        finally:
            await client.disconnect()


async def check_websocket_status():
    """Check WebSocket server status via HTTP endpoint."""
    import aiohttp
    
    print(f"\n{'='*80}")
    print(f"Checking WebSocket Server Status")
    print(f"{'='*80}\n")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:8000/ws/status") as response:
                if response.status == 200:
                    data = await response.json()
                    print("WebSocket Server Status:")
                    print(json.dumps(data, indent=2))
                else:
                    print(f"Failed to get status: HTTP {response.status}")
    except Exception as e:
        print(f"Error checking status: {e}")


def main():
    """Main function to run WebSocket client tests."""
    import sys
    
    print("\n" + "="*80)
    print("WebSocket Client Test Suite")
    print("="*80)
    
    if len(sys.argv) < 2:
        print("\nUsage: python websocket_client.py <test_type> [args]")
        print("\nTest types:")
        print("  exchange <currency> <duration>  - Test exchange rates (default: EUR, 30s)")
        print("  dxy <duration>                  - Test dollar index (default: 30s)")
        print("  commodity <name> <duration>     - Test commodity prices (default: GOLD, 30s)")
        print("  multiple                        - Test multiple streams simultaneously")
        print("  unsubscribe <currency>          - Test unsubscribe functionality")
        print("  status                          - Check WebSocket server status")
        print("\nExamples:")
        print("  python websocket_client.py exchange EUR 30")
        print("  python websocket_client.py dxy 60")
        print("  python websocket_client.py commodity GOLD 45")
        print("  python websocket_client.py multiple")
        print("  python websocket_client.py status")
        return
    
    test_type = sys.argv[1].lower()
    
    if test_type == "exchange":
        currency = sys.argv[2] if len(sys.argv) > 2 else "EUR"
        duration = int(sys.argv[3]) if len(sys.argv) > 3 else 30
        asyncio.run(test_exchange_rates(currency, duration))
    
    elif test_type == "dxy":
        duration = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        asyncio.run(test_dollar_index(duration))
    
    elif test_type == "commodity":
        commodity = sys.argv[2] if len(sys.argv) > 2 else "GOLD"
        duration = int(sys.argv[3]) if len(sys.argv) > 3 else 30
        asyncio.run(test_commodity_prices(commodity, duration))
    
    elif test_type == "multiple":
        asyncio.run(test_multiple_streams())
    
    elif test_type == "unsubscribe":
        currency = sys.argv[2] if len(sys.argv) > 2 else "EUR"
        asyncio.run(test_unsubscribe(currency))
    
    elif test_type == "status":
        asyncio.run(check_websocket_status())
    
    else:
        print(f"Unknown test type: {test_type}")
        print("Run without arguments to see usage")


if __name__ == "__main__":
    main()
