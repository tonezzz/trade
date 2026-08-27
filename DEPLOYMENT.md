# TradeCanvas UI Deployment

## Overview
TradeCanvas UI is a web-based trading interface that serves static files through Caddy web server. This document explains the deployment architecture and file synchronization process.

## Deployment Architecture

### Development Location
- **Path**: `/home/tony/CascadeProjects/trade/tradecanvas-ui/`
- **Purpose**: Active development directory where files are edited and tested
- **Contains**: All source files including development-only files (NAVIGATION.md, ssot.ui.yml)

### Production Location
- **Path**: `/home/tony/CascadeProjects/chaba-tony-dell/stacks/web/public/apps/trade/tradecanvas-ui/`
- **Purpose**: Production directory served by Caddy web server
- **Mapped to**: Docker volume at `/srv/public/apps/trade/tradecanvas-ui/`
- **URL**: `http://100.68.142.13:8080/apps/trade/tradecanvas-ui/`

### Web Server Configuration
- **Server**: Caddy running in Docker container
- **Config File**: `/home/tony/CascadeProjects/chaba-tony-dell/stacks/web/Caddyfile`
- **Port**: 8080
- **Routing Rule**: 
  ```
  handle_path /apps/trade/tradecanvas-ui/* {
      root * /srv/public/apps/trade/tradecanvas-ui
      file_server
  }
  ```

## File Synchronization

### Files to Sync
The following files need to be synchronized from development to production:
- `app.js` - Main application logic
- `compare.html` - Compare page
- `compare.js` - Compare page JavaScript
- `favicon.svg` - Site icon
- `index.html` - Main dashboard page
- `nav.js` - Navigation JavaScript
- `styles.css` - Stylesheet
- `test.html` - Test page
- `ui-renderer.js` - UI rendering logic

### Files NOT to Sync
Development-only files that should not be deployed:
- `NAVIGATION.md` - Documentation
- `ssot.ui.yml` - Configuration file

### Sync Methods

#### Manual Sync
```bash
# Copy individual files
cp /home/tony/CascadeProjects/trade/tradecanvas-ui/app.js \
   /home/tony/CascadeProjects/chaba-tony-dell/stacks/web/public/apps/trade/tradecanvas-ui/

# Fix permissions
sudo chown tony:tony /home/tony/CascadeProjects/chaba-tony-dell/stacks/web/public/apps/trade/tradecanvas-ui/*
```

#### Automated Sync Script
Use the provided sync script:
```bash
./sync-tradecanvas-ui.sh
```

The script:
1. Creates a timestamped backup
2. Copies only the necessary files
3. Fixes permissions automatically
4. Tests the deployment

#### Using rsync
```bash
rsync -av --exclude='NAVIGATION.md' --exclude='ssot.ui.yml' \
  /home/tony/CascadeProjects/trade/tradecanvas-ui/ \
  /home/tony/CascadeProjects/chaba-tony-dell/stacks/web/public/apps/trade/tradecanvas-ui/
```

## Verification

### Test URL Accessibility
```bash
# Test main page
curl -I http://100.68.142.13:8080/apps/trade/tradecanvas-ui/

# Test specific files
curl -I http://100.68.142.13:8080/apps/trade/tradecanvas-ui/compare.html
curl -I http://100.68.142.13:8080/apps/trade/tradecanvas-ui/app.js
```

### Check File Contents
```bash
# Compare development vs production
diff /home/tony/CascadeProjects/trade/tradecanvas-ui/compare.html \
     /home/tony/CascadeProjects/chaba-tony-dell/stacks/web/public/apps/trade/tradecanvas-ui/compare.html
```

### Browser Testing
Open the following URLs in a browser:
- `http://100.68.142.13:8080/apps/trade/tradecanvas-ui/`
- `http://100.68.142.13:8080/apps/trade/tradecanvas-ui/compare.html`
- `http://100.68.142.13:8080/apps/trade/tradecanvas-ui/test.html`

## Troubleshooting

### 404 Errors
**Symptoms**: Files return 404 Not Found

**Solutions**:
1. Check if files exist in production directory
2. Verify Caddy configuration is correct
3. Check file permissions (must be readable by web server)
4. Restart Caddy if configuration changed

### Permission Issues
**Symptoms**: Access denied or permission errors

**Solutions**:
```bash
# Fix ownership
sudo chown -R tony:tony /home/tony/CascadeProjects/chaba-tony-dell/stacks/web/public/apps/trade/tradecanvas-ui/

# Fix permissions
chmod -R 644 /home/tony/CascadeProjects/chaba-tony-dell/stacks/web/public/apps/trade/tradecanvas-ui/*
chmod 755 /home/tony/CascadeProjects/chaba-tony-dell/stacks/web/public/apps/trade/tradecanvas-ui
```

### Outdated Files
**Symptoms**: Changes not appearing in production

**Solutions**:
1. Run sync script to update files
2. Clear browser cache
3. Check Caddy cache (restart if needed)

### Docker Volume Issues
**Symptoms**: Files not accessible from container

**Solutions**:
1. Check docker-compose.yml volume mappings
2. Verify host directory exists
3. Restart containers: `docker-compose restart web`

## Deployment Workflow

### Typical Development Cycle
1. Make changes in `/home/tony/CascadeProjects/trade/tradecanvas-ui/`
2. Test locally by opening files directly in browser
3. Run sync script: `./sync-tradecanvas-ui.sh`
4. Verify deployment: `curl -I http://100.68.142.13:8080/apps/trade/tradecanvas-ui/`
5. Test in browser at production URL

### Pre-Deployment Checklist
- [ ] All changes tested in development directory
- [ ] Sync script run successfully
- [ ] File permissions correct
- [ ] URLs accessible via curl
- [ ] Pages load correctly in browser
- [ ] No console errors in browser
- [ ] All functionality working as expected

## Future Improvements

### Potential Enhancements
1. **Automated sync**: Set up watch mode to auto-sync on file changes
2. **Build process**: Add minification/bundling for production
3. **CI/CD pipeline**: Automated testing and deployment
4. **Versioning**: Add version numbers to track deployments
5. **Rollback**: Easy rollback to previous versions
6. **Staging environment**: Separate staging for testing

### Symbolic Link Alternative
Consider using symbolic links instead of copying files:
```bash
# Create symbolic link (experimental)
ln -s /home/tony/CascadeProjects/trade/tradecanvas-ui/app.js \
      /home/tony/CascadeProjects/chaba-tony-dell/stacks/web/public/apps/trade/tradecanvas-ui/app.js
```

**Pros**: Changes immediately reflected, no sync needed
**Cons**: Development files exposed in production, potential permission issues

## Related Documentation
- [Deployment Sync Skill](.devin/skills/deployment-sync/SKILL.md) - Automated deployment investigation and sync
- [Caddy Configuration](/home/tony/CascadeProjects/chaba-tony-dell/stacks/web/Caddyfile) - Web server routing rules
- [AGENTS.md](AGENTS.md) - Sub-agent usage guidelines

## Support
For deployment issues, use the deployment-sync skill:
```
"Use deployment-sync to investigate and fix the TradeCanvas UI deployment issue"
```
