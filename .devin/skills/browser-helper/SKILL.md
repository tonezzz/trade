# Browser Helper Skill

## Description
A skill for automating repetitive browser-based tasks like password retrieval, configuration verification, and web page testing using the playlive MCP server.

## Capabilities
- Navigate to web pages and verify content
- Extract configuration values from web interfaces
- Test web applications and APIs
- Handle login flows and authentication
- Verify database and service configurations
- Automate repetitive web-based tasks

## Use Cases
- **Password Retrieval**: Navigate to admin panels to find database credentials
- **Configuration Verification**: Check web interfaces for service status
- **API Testing**: Test web endpoints and verify responses
- **Service Monitoring**: Check dashboard pages for system status
- **Form Automation**: Fill out web forms and submit data

## Usage
Invoke this skill when you need to:
- Navigate to a web page to find configuration information
- Test a web application or API
- Verify that a service is running correctly
- Automate repetitive web-based configuration tasks

## Example
```
"Use browser helper to navigate to http://playlive.local and find the PostgreSQL password"
"Verify that the API server is running at http://localhost:8000"
"Check the admin panel for database credentials"
```

## MCP Server
Uses `playlive.tony-dell` MCP server for browser automation with Playwright/Chrome.