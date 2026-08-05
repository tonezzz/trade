
---

**Last Updated:** 2026-08-05
# Trade API Deployment Documentation

## Overview

The Trade API FastAPI backend has been successfully deployed to the web server at `http://tony-omen.local:8080/apps/trade/api`. The deployment uses Docker containers integrated with the existing Caddy reverse proxy infrastructure.

## Database Setup

### Automated Setup Wizard

The project includes an automated database setup wizard that simplifies initial configuration:

```bash
# Run the database setup wizard
python3 cli.py setup
```

The wizard will:
1. Prompt you to choose between PostgreSQL or SQLite
2. Collect database connection parameters
3. Test the database connection
4. Create the database if it doesn't exist
5. Initialize the database schema with all required tables
6. Save configuration to `.env` file
7. Verify the setup was successful

This replaces the manual database setup process and provides a user-friendly guided experience.

## Deployment Architecture

### Components

1. **Docker Container**: `trade-api` - FastAPI application running in a Docker container
2. **Reverse Proxy**: Caddy web server routes requests to the trade-api container
3. **Database**: PostgreSQL database (existing) at `postgres:5432` with database name `trade`
4. **Network**: Docker network integration with existing web stack

### Deployment Method

**Option A: Docker Container (Implemented)** ✅

The FastAPI application is deployed as a Docker container within the existing web stack. This approach was chosen because:
- Consistent with existing infrastructure (all other services use Docker)
- Easy to manage and scale
- Integrated with existing Docker Compose setup
- Automatic restart on failure
- Simple environment variable management

## Configuration Changes

### 1. Dockerfile Created

**File**: `/home/tony/CascadeProjects/trade/Dockerfile`

```dockerfile
FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y gcc postgresql-client && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ ./src/
COPY config/ ./config/
EXPOSE 8000
CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2. Docker Compose Updated

**File**: `/home/tony/CascadeProjects/chaba/stacks/web/docker-compose.yml`

Added the `trade-api` service:

```yaml
trade-api:
  container_name: trade-api
  build:
    context: /home/tony/CascadeProjects/trade
    dockerfile: Dockerfile
  restart: unless-stopped
  environment:
    - DB_HOST=postgres
    - DB_PORT=5432
    - DB_NAME=trade
    - DB_USER=chaba
    - DB_PASSWORD=chabapass
  networks:
    - default
  depends_on:
    postgres:
      condition: service_healthy
```

### 3. Caddy Configuration Updated

**File**: `/home/tony/CascadeProjects/chaba/stacks/web/Caddyfile`

Added routing rules for the trade API:

```caddy
@trade_noslash path /apps/trade
redir @trade_noslash /apps/trade/ 308

handle_path /apps/trade/api/* {
    reverse_proxy trade-api:8000
}
```

## Access URLs

### API Endpoints

- **API Root**: `http://tony-omen.local:8080/apps/trade/api`
- **Health Check**: `http://tony-omen.local:8080/apps/trade/api/api/health`
- **Swagger UI**: `http://tony-omen.local:8080/apps/trade/api/docs`
- **ReDoc**: `http://tony-omen.local:8080/apps/trade/api/redoc`
- **OpenAPI Schema**: `http://tony-omen.local:8080/apps/trade/api/openapi.json`

### Example API Calls

```bash
# Root endpoint
curl http://tony-omen.local:8080/apps/trade/api/

# Health check
curl http://tony-omen.local:8080/apps/trade/api/api/health

# Available currencies
curl http://tony-omen.local:8080/apps/trade/api/api/available/currencies

# Available commodities
curl http://tony-omen.local:8080/apps/trade/api/api/available/commodities

# Exchange rates for EUR (paginated)
curl "http://tony-omen.local:8080/apps/trade/api/api/exchange_rates/EUR?limit=5"

# Dollar index data
curl "http://tony-omen.local:8080/apps/trade/api/api/dollar_index?limit=5"

# Commodity prices
curl "http://tony-omen.local:8080/apps/trade/api/api/commodity_prices/OIL?limit=5"
```

## Management

### Using the Deployment Script

A deployment script has been created for easy management:

**File**: `/home/tony/CascadeProjects/trade/deploy.sh`

```bash
# Start the service
./deploy.sh start

# Stop the service
./deploy.sh stop

# Restart the service
./deploy.sh restart

# Rebuild the service (after code changes)
./deploy.sh rebuild

# View logs
./deploy.sh logs

# Check status
./deploy.sh status
```

### Manual Docker Commands

```bash
# Navigate to web stack directory
cd /home/tony/CascadeProjects/chaba/stacks/web

# Start the service
docker compose up -d trade-api

# Stop the service
docker compose stop trade-api

# Restart the service
docker compose restart trade-api

# Rebuild the service
docker compose build --no-cache trade-api
docker compose up -d trade-api

# View logs
docker logs -f trade-api

# Check container status
docker ps | grep trade-api
```

### Caddy Configuration Reload

After modifying the Caddyfile, reload the configuration:

```bash
docker exec web caddy reload --config /etc/caddy/Caddyfile
```

## Testing Results

### ✅ Health Check

```bash
curl http://tony-omen.local:8080/apps/trade/api/api/health
```

Response:
```json
{
  "status": "warning",
  "timestamp": "2026-08-04T03:15:39.387072",
  "checks": {
    "database_connection": true,
    "database_tables": true,
    "data_freshness": true,
    "data_volume": true,
    "data_quality": true,
    "system_resources": true
  },
  "issues": [],
  "warnings": [
    "commodity_prices data is 8 days old (consider updating)",
    "High CPU usage: 99.6%",
    "High memory usage: 80.8%"
  ]
}
```

### ✅ Database Connection

Successfully retrieved data from the database:
- 22 currencies available
- 1 commodity (OIL) available
- Exchange rate data accessible (7,063 EUR records)
- Database connection working through Docker network

### ✅ Swagger UI

Swagger UI is accessible at `http://tony-omen.local:8080/apps/trade/api/docs` and returns HTTP 200.

## Database Configuration

The application connects to the PostgreSQL database using the following configuration:

- **Host**: `postgres` (Docker network hostname)
- **Port**: `5432`
- **Database**: `trade`
- **User**: `chaba`
- **Password**: `chabapass`

The database connection is configured via environment variables in the Docker Compose file.

## Troubleshooting

### Container Not Starting

```bash
# Check container logs
docker logs trade-api

# Check if postgres is healthy
docker ps | grep postgres
```

### API Not Accessible

```bash
# Check if Caddy configuration is loaded
docker exec web caddy validate --config /etc/caddy/Caddyfile

# Check if container is running
docker ps | grep trade-api

# Test direct container access
docker exec trade-api curl http://localhost:8000/
```

### Database Connection Issues

```bash
# Test database connectivity from container
docker exec trade-api pg_isready -h postgres -U chaba

# Check database exists
docker exec postgres psql -U chaba -d trade -c "\dt"
```

### Caddy Routing Issues

```bash
# Reload Caddy configuration
docker exec web caddy reload --config /etc/caddy/Caddyfile

# Check Caddy logs
docker logs web | tail -50
```

## Future Enhancements

### Potential Improvements

1. **Health Check Endpoint**: Add a dedicated health check endpoint to the Docker container
2. **Resource Limits**: Configure resource limits for the container in docker-compose.yml
3. **Monitoring**: Integrate with existing monitoring (NetData)
4. **SSL/TLS**: Add HTTPS support if needed
5. **Authentication**: Add API authentication if required
6. **Rate Limiting**: Implement rate limiting in Caddy
7. **Caching**: Add response caching for frequently accessed data

### Scaling Considerations

If the API needs to handle higher load:
1. Add multiple replicas using Docker Compose scale
2. Add load balancing in Caddy configuration
3. Consider horizontal scaling with Kubernetes
4. Implement connection pooling
5. Add Redis caching layer

## Security Considerations

### Current Security Posture

- Database credentials stored in environment variables
- No authentication required for API endpoints
- CORS enabled for all origins (configure for production)
- Container runs as root (consider non-root user)

### Recommendations for Production

1. **Authentication**: Implement API key or OAuth authentication
2. **CORS**: Restrict CORS to specific origins
3. **Environment Variables**: Use Docker secrets or vault for sensitive data
4. **Container Security**: Run as non-root user
5. **Network Security**: Implement network policies
6. **HTTPS**: Enable SSL/TLS encryption
7. **Rate Limiting**: Add rate limiting to prevent abuse
8. **Input Validation**: Ensure all inputs are properly validated

## Maintenance

### Regular Tasks

1. **Monitor Logs**: Check logs for errors or warnings
2. **Health Checks**: Regularly test the health endpoint
3. **Database Maintenance**: Monitor database size and performance
4. **Update Dependencies**: Keep Python packages updated
5. **Security Updates**: Apply security patches promptly

### Backup Strategy

- Database backups handled by existing PostgreSQL backup strategy
- Application code stored in Git repository
- Docker images can be rebuilt from source

## Summary

The Trade API has been successfully deployed using Docker containers integrated with the existing Caddy reverse proxy infrastructure. The deployment follows the established patterns in the web stack and provides:

- ✅ Reliable service management with automatic restart
- ✅ Easy scaling and management
- ✅ Integration with existing monitoring and logging
- ✅ Consistent configuration management
- ✅ Simple deployment and update process

The API is now accessible at `http://tony-omen.local:8080/apps/trade/api` with full Swagger UI documentation available at `/docs`.
