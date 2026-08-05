
---

**Last Updated:** 2026-08-05
# WebSocket API Documentation

## Overview

The Trading Data API now supports real-time data streaming via WebSocket connections. This allows clients to receive live updates for exchange rates, dollar index (DXY), and commodity prices without the need for continuous polling.

## Features

- **Real-time streaming**: Receive live price updates as they become available
- **Multiple data types**: Support for exchange rates, dollar index, and commodity prices
- **Connection management**: Automatic handling of connections, disconnections, and reconnections
- **Rate limiting**: Built-in protection against connection abuse
- **Heartbeat mechanism**: Keep-alive messages to detect inactive connections
- **Configurable polling intervals**: Adjust update frequency based on your needs
- **Production-ready**: Error handling, logging, and monitoring

## WebSocket Endpoints

### Exchange Rates

**Endpoint**: `ws://localhost:8000/ws/exchange_rates/{currency}`

**Description**: Subscribe to real-time exchange rate updates for a specific currency.

**Parameters**:
- `currency` (path): Currency code (e.g., EUR, GBP, JPY, CAD, AUD)

**Example**:
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/exchange_rates/EUR');
```

**Message Format**:
```json
{
  "type": "exchange_rate",
  "currency": "EUR",
  "date": "2024-01-15",
  "rate": 0.9234,
  "open": 0.9210,
  "high": 0.9250,
  "low": 0.9200,
  "close": 0.9234,
  "volume": null,
  "timestamp": "2024-01-15T10:30:00.000000",
  "message": "Connected to exchange rate stream"
}
```

### Dollar Index (DXY)

**Endpoint**: `ws://localhost:8000/ws/dollar_index`

**Description**: Subscribe to real-time Dollar Index (DXY) updates.

**Parameters**: None

**Example**:
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/dollar_index');
```

**Message Format**:
```json
{
  "type": "dollar_index",
  "date": "2024-01-15",
  "value": 103.45,
  "open": 103.20,
  "high": 103.60,
  "low": 103.10,
  "close": 103.45,
  "volume": null,
  "timestamp": "2024-01-15T10:30:00.000000",
  "message": "Connected to dollar index stream"
}
```

### Commodity Prices

**Endpoint**: `ws://localhost:8000/ws/commodity_prices/{commodity}`

**Description**: Subscribe to real-time commodity price updates.

**Parameters**:
- `commodity` (path): Commodity name (e.g., GOLD, SILVER, OIL, COPPER)

**Example**:
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/commodity_prices/GOLD');
```

**Message Format**:
```json
{
  "type": "commodity",
  "commodity": "GOLD",
  "symbol": "XAUUSD",
  "date": "2024-01-15",
  "price": 2025.50,
  "unit": "oz",
  "open": 2020.00,
  "high": 2030.00,
  "low": 2018.00,
  "close": 2025.50,
  "volume": null,
  "timestamp": "2024-01-15T10:30:00.000000",
  "message": "Connected to GOLD stream"
}
```

## Client Messages

Clients can send the following messages to the server:

### Ping

Keep the connection alive and check server responsiveness.

```json
{
  "action": "ping"
}
```

**Response**:
```json
{
  "type": "pong",
  "timestamp": "2024-01-15T10:30:00.000000"
}
```

### Unsubscribe

Unsubscribe from the current data stream and close the connection.

```json
{
  "action": "unsubscribe"
}
```

**Response**:
```json
{
  "type": "info",
  "message": "Unsubscribed from EUR"
}
```

## Configuration

WebSocket settings are configured in `config/api.yml`:

```yaml
websocket:
  enabled: true
  
  # Polling intervals (in seconds)
  polling:
    exchange_rate_interval: 5
    dollar_index_interval: 5
    commodity_interval: 5
  
  # Rate limiting
  rate_limiting:
    max_connections_per_ip: 10
    connection_timeout: 300  # 5 minutes
    max_message_size: 1048576  # 1MB
  
  # Performance settings
  performance:
    max_subscriptions_per_client: 50
    heartbeat_interval: 30  # seconds
    heartbeat_timeout: 60  # seconds
  
  # Data batching
  batching:
    enabled: true
    batch_size: 10
    batch_timeout: 1.0  # seconds
```

### Configuration Options

| Setting | Description | Default |
|---------|-------------|---------|
| `enabled` | Enable/disable WebSocket functionality | `true` |
| `exchange_rate_interval` | Polling interval for exchange rates (seconds) | `5` |
| `dollar_index_interval` | Polling interval for DXY (seconds) | `5` |
| `commodity_interval` | Polling interval for commodities (seconds) | `5` |
| `max_connections_per_ip` | Maximum WebSocket connections per IP address | `10` |
| `connection_timeout` | Connection timeout in seconds | `300` |
| `max_message_size` | Maximum message size in bytes | `1048576` |
| `max_subscriptions_per_client` | Maximum subscriptions per client | `50` |
| `heartbeat_interval` | Heartbeat send interval (seconds) | `30` |
| `heartbeat_timeout` | Heartbeat timeout before disconnect (seconds) | `60` |
| `batch_updates` | Enable data batching | `true` |
| `batch_size` | Number of updates to batch | `10` |
| `batch_timeout` | Maximum time to wait for batch (seconds) | `1.0` |

## Usage Examples

### JavaScript (Browser)

```javascript
// Connect to exchange rate stream
const ws = new WebSocket('ws://localhost:8000/ws/exchange_rates/EUR');

ws.onopen = function() {
    console.log('Connected to exchange rate stream');
};

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Received update:', data);
    
    // Handle different message types
    if (data.type === 'exchange_rate') {
        updateUI(data);
    } else if (data.type === 'heartbeat') {
        // Heartbeat received, connection is alive
    }
};

ws.onerror = function(error) {
    console.error('WebSocket error:', error);
};

ws.onclose = function() {
    console.log('Connection closed');
    // Implement reconnection logic
    setTimeout(() => {
        reconnect();
    }, 5000);
};

function reconnect() {
    const ws = new WebSocket('ws://localhost:8000/ws/exchange_rates/EUR');
    // ... (same as above)
}

function updateUI(data) {
    // Update your trading UI with new data
    document.getElementById('rate').textContent = data.rate;
    document.getElementById('timestamp').textContent = data.timestamp;
}
```

### Python

```python
import asyncio
import websockets
import json

async def exchange_rate_client(currency: str):
    uri = f"ws://localhost:8000/ws/exchange_rates/{currency}"
    
    async with websockets.connect(uri) as websocket:
        print(f"Connected to {currency} stream")
        
        while True:
            try:
                message = await websocket.recv()
                data = json.loads(message)
                
                if data['type'] == 'exchange_rate':
                    print(f"{currency}: {data['rate']} at {data['timestamp']}")
                elif data['type'] == 'heartbeat':
                    print("Heartbeat received")
                    
            except websockets.exceptions.ConnectionClosed:
                print("Connection closed, reconnecting...")
                break

# Run the client
asyncio.run(exchange_rate_client('EUR'))
```

### Using the Example Client

The project includes a comprehensive WebSocket client for testing:

```bash
# Test exchange rates
python examples/websocket_client.py exchange EUR 30

# Test dollar index
python examples/websocket_client.py dxy 30

# Test commodity prices
python examples/websocket_client.py commodity GOLD 30

# Test multiple streams simultaneously
python examples/websocket_client.py multiple

# Test unsubscribe functionality
python examples/websocket_client.py unsubscribe EUR

# Check WebSocket server status
python examples/websocket_client.py status
```

## Connection Status

You can check the current WebSocket connection status via HTTP:

**Endpoint**: `GET http://localhost:8000/ws/status`

**Response**:
```json
{
  "active_connections": 5,
  "subscriptions": {
    "exchange_rates": {
      "EUR": 2,
      "GBP": 1,
      "JPY": 1
    },
    "dollar_index": {
      "DXY": 3
    },
    "commodities": {
      "GOLD": 2,
      "SILVER": 1
    }
  },
  "timestamp": "2024-01-15T10:30:00.000000"
}
```

## Error Handling

### Connection Errors

The WebSocket server may close connections with the following close codes:

| Code | Description |
|------|-------------|
| 1008 | Policy violation (e.g., invalid currency) |
| 1011 | Internal server error |

### Reconnection Strategy

Implement exponential backoff for reconnection:

```javascript
let reconnectAttempts = 0;
const maxReconnectAttempts = 5;
const baseReconnectDelay = 1000; // 1 second

function reconnect() {
    if (reconnectAttempts >= maxReconnectAttempts) {
        console.error('Max reconnection attempts reached');
        return;
    }
    
    const delay = baseReconnectDelay * Math.pow(2, reconnectAttempts);
    console.log(`Reconnecting in ${delay}ms...`);
    
    setTimeout(() => {
        reconnectAttempts++;
        // Attempt to reconnect
        const ws = new WebSocket('ws://localhost:8000/ws/exchange_rates/EUR');
        // ... (connection logic)
    }, delay);
}
```

## Integration with Trading UI

The WebSocket endpoints are designed for integration with the trading UI at `http://tony-omen.local:8080/apps/trade`.

### Example Integration

```javascript
class TradingDataStreamer {
    constructor(baseUrl) {
        this.baseUrl = baseUrl;
        this.connections = new Map();
    }
    
    subscribeToCurrency(currency, callback) {
        const ws = new WebSocket(`${this.baseUrl}/ws/exchange_rates/${currency}`);
        
        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.type === 'exchange_rate') {
                callback(data);
            }
        };
        
        this.connections.set(`exchange_rate_${currency}`, ws);
        return ws;
    }
    
    subscribeToDXY(callback) {
        const ws = new WebSocket(`${this.baseUrl}/ws/dollar_index`);
        
        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.type === 'dollar_index') {
                callback(data);
            }
        };
        
        this.connections.set('dollar_index', ws);
        return ws;
    }
    
    subscribeToCommodity(commodity, callback) {
        const ws = new WebSocket(`${this.baseUrl}/ws/commodity_prices/${commodity}`);
        
        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.type === 'commodity') {
                callback(data);
            }
        };
        
        this.connections.set(`commodity_${commodity}`, ws);
        return ws;
    }
    
    unsubscribe(key) {
        const ws = this.connections.get(key);
        if (ws) {
            ws.send(JSON.stringify({ action: 'unsubscribe' }));
            this.connections.delete(key);
        }
    }
    
    unsubscribeAll() {
        this.connections.forEach((ws, key) => {
            this.unsubscribe(key);
        });
    }
}

// Usage in trading UI
const streamer = new TradingDataStreamer('ws://localhost:8000');

// Subscribe to EUR
streamer.subscribeToCurrency('EUR', (data) => {
    updateEURChart(data);
});

// Subscribe to DXY
streamer.subscribeToDXY((data) => {
    updateDXYChart(data);
});

// Subscribe to GOLD
streamer.subscribeToCommodity('GOLD', (data) => {
    updateGoldChart(data);
});
```

## Performance Considerations

### Connection Pooling

- Each WebSocket connection maintains its own database session
- Connections are automatically cleaned up after timeout
- Use a single connection per data type when possible

### Update Frequency

- Default polling interval is 5 seconds
- Adjust based on your data freshness requirements
- Higher frequency increases server load

### Bandwidth

- Each message is approximately 200-300 bytes
- Monitor total bandwidth usage with multiple connections
- Consider data batching for high-frequency updates

## Security

### CORS

WebSocket connections respect CORS settings configured in `config/api.yml`:

```yaml
cors:
  enabled: true
  allow_origins:
    - "http://localhost:8080"
    - "http://tony-omen.local:8080"
    - "http://127.0.0.1:8080"
```

### Rate Limiting

- Maximum 10 connections per IP address
- Connection timeout after 5 minutes of inactivity
- Maximum 50 subscriptions per client

### Authentication

Currently, WebSocket endpoints do not require authentication. For production use, consider implementing:

1. Token-based authentication in the WebSocket handshake
2. API key validation
3. IP whitelisting

## Troubleshooting

### Connection Refused

**Problem**: Cannot connect to WebSocket server

**Solutions**:
1. Ensure the API server is running: `python scripts/run_api.py`
2. Check the correct port (default: 8000)
3. Verify WebSocket is enabled in configuration

### No Updates Received

**Problem**: Connected but not receiving data

**Solutions**:
1. Check if data exists in the database for the requested currency/commodity
2. Verify polling interval in configuration
3. Check server logs for errors

### Frequent Disconnections

**Problem**: Connection keeps dropping

**Solutions**:
1. Check heartbeat timeout settings
2. Verify network stability
3. Check server logs for error messages
4. Implement reconnection logic in client

### Rate Limit Errors

**Problem**: Connection rejected due to rate limiting

**Solutions**:
1. Reduce number of connections from your IP
2. Increase `max_connections_per_ip` in configuration
3. Implement connection pooling in your client

## Monitoring

### Server Logs

WebSocket operations are logged with the following levels:

- `INFO`: Connection events, subscription changes
- `WARNING`: Rate limiting, heartbeat timeouts
- `ERROR`: Connection errors, data streaming errors

### Connection Metrics

Monitor the `/ws/status` endpoint to track:
- Active connections
- Subscription counts per data type
- Connection trends over time

## API Documentation

WebSocket endpoints are documented in the interactive API documentation:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Support

For issues or questions about WebSocket functionality:

1. Check this documentation
2. Review the example client in `examples/websocket_client.py`
3. Check server logs for error messages
4. Consult the main API documentation in `docs/API_GUIDE.md`

## Future Enhancements

Planned improvements to the WebSocket system:

1. **Authentication**: Token-based authentication for secure connections
2. **Filtering**: Client-side filtering of data fields
3. **Historical Data**: Option to request historical data on connection
4. **Aggregation**: Real-time aggregation of multiple data points
5. **Alerts**: Configurable price alerts pushed via WebSocket
6. **Backpressure**: Flow control for high-frequency updates
