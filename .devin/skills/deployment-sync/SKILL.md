# Deployment Sync Skill

## Description
A specialized skill for handling web deployment tasks, including investigating deployment paths, synchronizing files between development and production directories, verifying deployments, and debugging web issues.

## Capabilities

### 1. Investigate Deployment Paths
- Check web server configuration files (Caddyfile, nginx.conf, Apache configs)
- Identify actual file serving locations vs development directories
- Verify symbolic links and mount points
- Check Docker volume mounts and container mappings
- Analyze routing rules and path mappings
- Document the complete deployment architecture

### 2. Handle File Synchronization
- Sync files between development and deployment directories
- Handle permission issues automatically (use sudo when needed)
- Maintain file integrity across locations
- Create backup copies before overwriting
- Preserve file ownership and permissions when possible
- Handle symbolic link creation and maintenance
- Support rsync, cp, and other sync methods

### 3. Verify Deployments
- Test URL accessibility with curl
- Check file availability at deployed paths
- Validate configuration changes
- Check file permissions and ownership
- Verify web server is running and accessible
- Test static file serving
- Validate routing and path mappings

### 4. Debug Web Issues
- Investigate 404 errors by checking file existence
- Check file permissions and ownership
- Test static file serving
- Verify web server is running and accessible
- Analyze server logs for errors
- Check configuration syntax and validity
- Test network connectivity and port availability

## Use Cases
- **Deployment Path Investigation**: Understand how files are served and where they should be deployed
- **File Synchronization**: Keep development and production directories in sync
- **Post-Deployment Verification**: Confirm deployment was successful and files are accessible
- **Debugging 404 Errors**: Investigate why files aren't being served correctly
- **Permission Issues**: Fix file ownership and permission problems
- **Configuration Validation**: Ensure web server configuration is correct
- **Docker Deployment Issues**: Troubleshoot container volume mount problems

## Usage
Invoke this skill when you need to:
- Investigate why web files aren't being served correctly
- Sync development files to production directories
- Verify a deployment was successful
- Debug 404 errors or permission issues
- Understand the deployment architecture
- Fix file synchronization issues

## Example
```
"Investigate the deployment path for tradecanvas-ui at http://tony-omen.local:8080/apps/trade/tradecanvas-ui/
Development files are in /home/tony/CascadeProjects/trade/tradecanvas-ui/
Identify the mismatch and implement a solution to sync the files."
```

```
"Debug why the compare.html page returns 404 at http://tony-omen.local:8080/apps/trade/tradecanvas-ui/compare.html
Check file existence, permissions, and web server configuration."
```

```
"Sync the latest changes from /home/tony/CascadeProjects/trade/tradecanvas-ui/ to the deployment directory
Create backups before overwriting and verify the deployment works correctly."
```

## Investigation Process

### Step 1: Identify Web Server Configuration
1. Locate and read web server configuration files
2. Identify the document root and path mappings
3. Check for Docker volume mounts or container mappings
4. Document the serving architecture

### Step 2: Compare Development vs Deployment
1. List files in development directory
2. List files in deployment directory
3. Identify missing or outdated files
4. Check file permissions and ownership
5. Verify symbolic links if present

### Step 3: Implement Synchronization
1. Create backup of deployment directory
2. Copy/sync files from development to deployment
3. Fix permissions if needed (use sudo when required)
4. Verify file integrity after sync

### Step 4: Verify Deployment
1. Test URL accessibility with curl
2. Check specific files are accessible
3. Verify web server is running
4. Test routing and path mappings
5. Check server logs for errors

## Common Issues and Solutions

### Issue: Files not being served (404 errors)
**Investigation:**
- Check if files exist in deployment directory
- Verify web server configuration path mappings
- Check file permissions (must be readable by web server user)
- Verify web server is running

**Solution:**
- Sync files from development to deployment
- Fix permissions with chmod/chown
- Update web server configuration if paths changed
- Restart web server if needed

### Issue: Permission denied errors
**Investigation:**
- Check file ownership and permissions
- Identify web server user (www-data, nginx, caddy, etc.)
- Verify directory permissions

**Solution:**
- Use sudo to change ownership: `sudo chown -R user:group /path`
- Fix permissions: `sudo chmod -R 755 /path`
- Ensure web server user has read access

### Issue: Outdated files in production
**Investigation:**
- Compare file timestamps between development and deployment
- Identify which files need updating
- Check if there's a build process required

**Solution:**
- Sync files using rsync: `rsync -av --delete dev/ deploy/`
- Run build process if needed
- Clear any caches

### Issue: Docker volume mount problems
**Investigation:**
- Check docker-compose.yml for volume mappings
- Verify host directory exists and has correct permissions
- Check container logs for mount errors

**Solution:**
- Fix volume mappings in docker-compose.yml
- Ensure host directories exist with correct permissions
- Restart containers after configuration changes

## Tools and Commands

### File Operations
- `ls -la` - List files with permissions and ownership
- `diff -r` - Compare directories recursively
- `rsync -av` - Sync directories preserving attributes
- `cp -r` - Copy directories recursively
- `chmod` - Change file permissions
- `chown` - Change file ownership

### Web Server Operations
- `curl -I` - Test URL accessibility (headers only)
- `curl` - Test URL and get content
- `systemctl status caddy` - Check Caddy service status
- `systemctl restart caddy` - Restart Caddy service
- `docker ps` - Check running containers
- `docker logs` - Check container logs

### Docker Operations
- `docker-compose config` - Verify docker-compose configuration
- `docker volume ls` - List Docker volumes
- `docker inspect` - Check container details including mounts

## Best Practices

1. **Always create backups** before overwriting files
2. **Use rsync with --delete** to keep directories in sync
3. **Check permissions** after file operations
4. **Test URLs** after making changes
5. **Document the deployment architecture** for future reference
6. **Use sudo only when needed** to avoid permission issues
7. **Verify web server configuration** after making changes
8. **Check logs** when debugging issues

## Integration with Other Skills

This skill works well with:
- **trade-verify**: For comprehensive system health checks
- **remote-access**: For deployment on remote machines
- **config-helper**: For configuration file management
- **browser-helper**: For UI testing after deployment

## Notes

- This skill focuses on static file deployment and web server configuration
- For application deployment (Docker containers, databases), consider using other specialized skills
- Always test changes in a safe environment before production
- Keep documentation of deployment paths and configurations
