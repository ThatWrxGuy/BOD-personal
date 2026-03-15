# PSIE Security

This document describes the security architecture and features of the Personal Strategic Intelligence Engine.

## Overview

PSIE implements a comprehensive security model that covers authentication, authorization, secrets management, and connector security.

## Authentication

### JWT Tokens

PSIE uses JWT (JSON Web Tokens) for authentication:

```python
from app.identity.token_service import get_token_service

token_service = get_token_service()

# Create token
token = token_service.create_access_token(
    user_id=user.id,
    username=user.username,
    role=user.role,
    permissions=user.permissions
)

# Verify token
user_info = token_service.get_user_from_token(token)
```

### Token Structure

```json
{
  "sub": "user-uuid",
  "username": "john",
  "role": "operator",
  "permissions": ["view_dashboard", "approve_decision"],
  "iat": 1234567890,
  "exp": 1234571490,
  "type": "access"
}
```

### Token Expiration

Default: 60 minutes (configurable via `ACCESS_TOKEN_EXPIRE_MINUTES`)

### Login Flow

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john",
    "password": "secretpassword"
  }'
```

Response:
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "user": {
    "id": "...",
    "username": "john",
    "role": "operator"
  }
}
```

## Authorization

### Roles

| Role | Description |
|------|-------------|
| Owner | Full system access |
| Administrator | User and system management |
| Operator | Operational actions |
| Viewer | Read-only access |
| Auditor | Audit log access |

### Permissions

Permissions are grouped by domain:

**System**
- `view_dashboard`
- `view_system_health`

**Signals**
- `view_signals`
- `create_signal`
- `manage_signals`

**Debate**
- `view_debates`
- `participate_in_debate`
- `create_debate`

**Governance**
- `view_governance`
- `approve_decision`
- `reject_decision`
- `manage_governance`

**Execution**
- `view_execution`
- `execute_action`
- `approve_execution`
- `view_execution_history`

**Learning**
- `view_learning_data`
- `manage_learning`

**Connectors**
- `view_connectors`
- `manage_connectors`

**Administration**
- `manage_users`
- `manage_roles`
- `view_audit_logs`
- `manage_settings`

### Checking Permissions

```python
from app.identity.rbac_engine import RBACEngine

rbac = RBACEngine(session)

# Check single permission
has_permission = await rbac.check_permission(user, "execute_action")

# Check multiple permissions (all required)
has_all = await rbac.check_permissions(user, ["execute_action", "approve_execution"])

# Check any permission (at least one required)
has_any = await rbac.check_any_permission(user, ["execute_action", "approve_execution"])
```

### Permission Dependencies

Some permissions depend on others:

- `approve_execution` requires `execute_action`
- `manage_governance` requires `approve_decision`

## Secrets Management

### Secret Manager

All secrets are accessed through the centralized secret manager:

```python
from app.security.secret_manager import get_secret_manager

secret_manager = get_secret_manager()

# Check if secret exists
has_key = secret_manager.has_secret("OPENAI_API_KEY")

# Get secret value
api_key = secret_manager.get_secret("OPENAI_API_KEY")
```

### Environment Variables

Secrets are loaded from environment variables:

| Secret | Description |
|--------|-------------|
| `SECRET_KEY` | Application secret key |
| `OPENAI_API_KEY` | OpenAI API key |
| `ANTHROPIC_API_KEY` | Anthropic API key |
| `GOOGLE_CLIENT_ID` | Google OAuth client ID |
| `SCHWAB_CLIENT_ID` | Schwab API client ID |

### Secret Redaction

Credentials are automatically redacted in logs and responses:

```python
from app.security.credential_redactor import redact_credentials

# Redact secrets from response
safe_response = redact_credentials({
    "api_key": "sk-1234567890",
    "user": "john"
})
# Result: {"api_key": "[REDACTED]", "user": "john"}
```

## Connector Security

### Disabled by Default

All connectors are disabled by default:

```python
# Check connector status
response = await client.get("/security/connectors/openai_llm")
# {
#   "connector_id": "openai_llm",
#   "is_enabled": false,
#   "is_validated": false,
#   "is_ready": false
# }
```

### Validation Required

Connectors must be validated before use:

```bash
curl -X POST http://localhost:8000/security/connectors/openai_llm/validate
```

This checks that all required secrets are present.

### Enable Process

1. Configure required secrets in environment
2. Validate connector configuration
3. Enable connector
4. (Optional) Test connector

```bash
# 1. Validate
curl -X POST http://localhost:8000/security/connectors/openai_llm/validate

# 2. Enable
curl -X POST http://localhost:8000/security/connectors/openai_llm/enable
```

### Risk Levels

| Level | Description | Example |
|-------|-------------|---------|
| Low | Read-only data | Alpha Vantage |
| Medium | Limited write | OpenAI, Todoist |
| High | Sensitive data | Gmail, Google Calendar |
| Critical | Financial transactions | Schwab, Interactive Brokers |

### Financial Connectors

Financial connectors require additional security:

```python
# Check required permissions for financial connector
connector = CONNECTOR_REGISTRY["schwab_financial"]
# {
#   "required_permissions": ["manage_connectors", "execute_financial_action"]
# }
```

## Audit Logging

### Access Audit

All authentication events are logged:

```python
# Automatic logging on login
log = AccessAuditLog(
    user_id=user.id,
    action="login_success",
    resource="auth",
    success=True
)
```

### Connector Audit

All connector actions are logged:

```python
log = ConnectorAuditLog(
    connector_id="openai_llm",
    action="enabled",
    status="success"
)
```

### Viewing Audit Logs

```bash
# Access logs
curl http://localhost:8000/admin/audit-logs

# Connector logs
curl http://localhost:8000/security/audit/connectors
```

## Security Configuration

### Development vs Production

| Setting | Development | Production |
|---------|-------------|------------|
| Authentication | Optional | Required |
| CORS | Permissive | Strict |
| Secret Key | Any | Must change |
| Connectors | Warnings | Must validate |

### Production Requirements

In production, the following are enforced:

1. **Secret Key**: Must not be the default value
2. **Authentication**: Must be enabled
3. **CORS**: Must not be wildcard
4. **Manual Approval**: Must be enabled for execution

### Environment Variables

```env
# Required in production
SECRET_KEY=your-secure-random-key
APP_ENV=production

# Enable auth
ENABLE_AUTH=true

# Configure CORS
CORS_ORIGINS=https://your-domain.com
```

## API Security

### Authentication

Protected endpoints require a Bearer token:

```bash
curl http://localhost:8000/api/protected \
  -H "Authorization: Bearer eyJ..."
```

### Public Endpoints

These endpoints don't require authentication:

- `/health`
- `/health/config-readiness`
- `/docs`
- `/auth/login`
- `/auth/register`

### Permission Enforcement

Sensitive endpoints require specific permissions:

```python
from app.identity.rbac_engine import require_permission

@app.get("/execution/execute")
@require_permission("execute_action")
async def execute_action():
    ...
```

## Best Practices

### Password Security

- Use strong, unique passwords
- Never commit passwords to version control
- Use a password manager

### API Keys

- Rotate API keys periodically
- Use environment variables, not hardcoded values
- Never expose keys in logs or error messages

### Access Control

- Grant minimum necessary permissions
- Use role-based access
- Review permissions regularly

### Monitoring

- Monitor audit logs for suspicious activity
- Set up alerts for failed login attempts
- Review connector access patterns
