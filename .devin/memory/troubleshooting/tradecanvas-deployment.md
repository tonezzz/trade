# TradeCanvas Deployment Issues and Solutions

**Category:** troubleshooting  
**Date:** 2026-08-04  
**Session:** TradeCanvas UI deployment  
**Tags:** deployment, caddy, tradecanvas, api, websocket

## Context

During deployment of the enhanced TradeCanvas UI, several configuration and routing issues were encountered that prevented the UI from loading data and connecting to WebSocket.

## Problems Encountered

### 1. API Endpoint Path Error
**Problem**: UI was calling `/apps/trade/api/api/exchange_rates/THB` (double `/api`) resulting in 404 errors.

**Root Cause**: The `app.js` file had incorrect API base URL: `http://tony-omen.local:8080/apps/trade/api/api`

**Solution**: Changed API base URL to `http://tony-omen.local:8080/apps/trade/api`

### 2. WebSocket Path Error  
**Problem**: WebSocket connection failed with path `/apps/trade/api/ws`

**Root Cause**: Caddy configuration routes WebSocket at `/apps/trade/ws/*`, not `/apps/trade/api/ws`

**Solution**: Changed WebSocket URL to `ws://tony-omen.local:8080/apps/trade/ws`

### 3. Caddy Configuration Syntax Error
**Problem**: Caddy failed to start with error: "request matchers may not be defined globally, they must be in a site block"

**Root Cause**: Match directives like `@tradecanvas_ui_noslash` were placed outside the site block (`:8080 { ... }`)

**Solution**: Moved match directives inside the appropriate site block in Caddyfile

### 4. File Locking Issues
**Problem**: Could not directly edit Caddyfile inside container due to file locking

**Root Cause**: Caddyfile is host-mounted from `/home/tony/CascadeProjects/chaba/stacks/web/Caddyfile`

**Solution**: Edit the host file directly instead of trying to edit inside container

## Key Learnings

1. **Caddy Site Block Structure**: Match directives must be inside site blocks, not globally
2. **Host-Mounted Config Files**: When files are host-mounted, edit the host file, not the container file
3. **API Route Consistency**: Ensure frontend API URLs match Caddy route configuration exactly
4. **WebSocket Path Configuration**: WebSocket endpoints often have different routing than REST API endpoints

## Caddy Configuration Pattern

```caddy
:8080 {
    # Match directives must be inside site block
    @matcher_name path /path/to/resource
    redir @matcher_name /path/to/resource/ 308
    
    handle_path /path/to/resource/* {
        root * /srv/public/path/to/resource
        file_server
    }
}
```

## API/WebSocket Routing Pattern

```caddy
# REST API routing
handle /apps/trade/api/* {
    uri strip_prefix /apps/trade
    reverse_proxy trade-api:8000
}

# WebSocket routing  
handle /apps/trade/ws/* {
    uri strip_prefix /apps/trade
    reverse_proxy trade-api:8000
}
```

## Prevention

1. **Test API endpoints** before updating frontend code
2. **Validate Caddy configuration** using `caddy validate --config /etc/caddy/Caddyfile`
3. **Check file mounts** with `docker inspect` to understand file locations
4. **Review Caddy logs** immediately after restart for syntax errors

## Related Memories
- [Caddy Configuration Best Practices](../workflows/caddy-configuration.md) - (to be created)
- [API Integration Patterns](../insights/api-integration.md) - (to be created)

## Related Documentation
- [Caddyfile](/home/tony/CascadeProjects/chaba/stacks/web/Caddyfile) - Current Caddy configuration
- [TradeCanvas Integration](../../docs/features/ui/TRADECANVAS_INTEGRATION.md) - UI integration docs
- [Deployment Guide](../../docs/core/DEPLOYMENT.md) - General deployment information

---

**Last Updated:** 2026-08-04