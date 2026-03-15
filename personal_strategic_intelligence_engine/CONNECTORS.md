# PSIE Connectors

This document describes the available connectors in the Personal Strategic Intelligence Engine, their configuration requirements, permissions, and risk profiles.

## Overview

PSIE supports integrations with various external services through a secure connector system. All connectors are **disabled by default** and must be explicitly enabled through the security API.

## Connector Domains

### LLM (Large Language Models)
- **Risk Level**: Medium
- **Default State**: Disabled
- **Purpose**: AI-powered reasoning and analysis

### Data
- **Risk Level**: Low
- **Default State**: Disabled
- **Purpose**: Market data, economic data feeds

### Email
- **Risk Level**: High
- **Default State**: Disabled
- **Purpose**: Email integration and notifications

### Calendar
- **Risk Level**: High
- **Default State**: Disabled
- **Purpose**: Calendar scheduling and management

### Tasks
- **Risk Level**: Medium
- **Default State**: Disabled
- **Purpose**: Task management integration

### Financial
- **Risk Level**: Critical
- **Default State**: Disabled
- **Purpose**: Brokerage and financial account integration

---

## Available Connectors

### LLM Connectors

#### OpenAI LLM
| Property | Value |
|----------|-------|
| ID | `openai_llm` |
| Domain | LLM |
| Risk Level | Medium |
| Required Secrets | `OPENAI_API_KEY` |
| Required Permissions | None |
| Description | OpenAI GPT models for AI reasoning |

**Environment Variables:**
```env
OPENAI_API_KEY=sk-...
```

---

#### Anthropic LLM
| Property | Value |
|----------|-------|
| ID | `anthropic_llm` |
| Domain | LLM |
| Risk Level | Medium |
| Required Secrets | `ANTHROPIC_API_KEY` |
| Required Permissions | None |
| Description | Anthropic Claude models for AI reasoning |

**Environment Variables:**
```env
ANTHROPIC_API_KEY=sk-ant-...
```

---

### Data Connectors

#### Alpha Vantage
| Property | Value |
|----------|-------|
| ID | `alphavantage_data` |
| Domain | Data |
| Risk Level | Low |
| Required Secrets | `ALPHAVANTAGE_API_KEY` |
| Required Permissions | `view_signals` |
| Description | Market data provider |

**Environment Variables:**
```env
ALPHAVANTAGE_API_KEY=...
```

---

#### Polygon
| Property | Value |
|----------|-------|
| ID | `polygon_data` |
| Domain | Data |
| Risk Level | Low |
| Required Secrets | `POLYGON_API_KEY` |
| Required Permissions | `view_signals` |
| Description | Market data provider |

**Environment Variables:**
```env
POLYGON_API_KEY=...
```

---

#### FRED
| Property | Value |
|----------|-------|
| ID | `fred_data` |
| Domain | Data |
| Risk Level | Low |
| Required Secrets | `FRED_API_KEY` |
| Required Permissions | `view_signals` |
| Description | Federal Reserve Economic Data |

**Environment Variables:**
```env
FRED_API_KEY=...
```

---

### Email Connectors

#### Gmail
| Property | Value |
|----------|-------|
| ID | `gmail_email` |
| Domain | Email |
| Risk Level | High |
| Required Secrets | `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` |
| Required Permissions | `manage_connectors` |
| Description | Gmail email integration |

**Environment Variables:**
```env
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/callback
GOOGLE_EMAIL_SENDER=your-email@gmail.com
```

---

### Calendar Connectors

#### Google Calendar
| Property | Value |
|----------|-------|
| ID | `google_calendar` |
| Domain | Calendar |
| Risk Level | High |
| Required Secrets | `GOOGLE_CALENDAR_CLIENT_ID`, `GOOGLE_CALENDAR_CLIENT_SECRET` |
| Required Permissions | `manage_connectors` |
| Description | Google Calendar integration |

**Environment Variables:**
```env
GOOGLE_CALENDAR_CLIENT_ID=...
GOOGLE_CALENDAR_CLIENT_SECRET=...
GOOGLE_CALENDAR_REDIRECT_URI=http://localhost:8000/auth/calendar/callback
GOOGLE_CALENDAR_ID=primary
```

---

### Task Connectors

#### Todoist
| Property | Value |
|----------|-------|
| ID | `todoist_tasks` |
| Domain | Tasks |
| Risk Level | Medium |
| Required Secrets | `TODOIST_API_TOKEN` |
| Required Permissions | `manage_connectors` |
| Description | Todoist task management |

**Environment Variables:**
```env
TODOIST_API_TOKEN=...
```

---

#### Notion
| Property | Value |
|----------|-------|
| ID | `notion_tasks` |
| Domain | Tasks |
| Risk Level | Medium |
| Required Secrets | `NOTION_API_KEY` |
| Required Permissions | `manage_connectors` |
| Description | Notion workspace integration |

**Environment Variables:**
```env
NOTION_API_KEY=secret_...
NOTION_DATABASE_ID=...
```

---

### Financial Connectors

#### Charles Schwab
| Property | Value |
|----------|-------|
| ID | `schwab_financial` |
| Domain | Financial |
| Risk Level | Critical |
| Required Secrets | `SCHWAB_CLIENT_ID`, `SCHWAB_CLIENT_SECRET` |
| Required Permissions | `manage_connectors`, `execute_financial_action` |
| Description | Schwab brokerage integration |

**Environment Variables:**
```env
SCHWAB_CLIENT_ID=...
SCHWAB_CLIENT_SECRET=...
SCHWAB_REDIRECT_URI=http://localhost:8000/auth/schwab/callback
```

⚠️ **Warning**: Financial connectors require explicit approval and are subject to strict governance controls.

---

#### Interactive Brokers
| Property | Value |
|----------|-------|
| ID | `ib_financial` |
| Domain | Financial |
| Risk Level | Critical |
| Required Secrets | `INTERACTIVE_BROKERS_HOST`, `INTERACTIVE_BROKERS_PORT` |
| Required Permissions | `manage_connectors`, `execute_financial_action` |
| Description | Interactive Brokers integration |

**Environment Variables:**
```env
INTERACTIVE_BROKERS_HOST=127.0.0.1
INTERACTIVE_BROKERS_PORT=7497
INTERACTIVE_BROKERS_ACCOUNT_ID=...
```

---

#### Coinbase
| Property | Value |
|----------|-------|
| ID | `coinbase_financial` |
| Domain | Financial |
| Risk Level | Critical |
| Required Secrets | `COINBASE_API_KEY`, `COINBASE_API_SECRET` |
| Required Permissions | `manage_connectors`, `execute_financial_action` |
| Description | Cryptocurrency exchange integration |

**Environment Variables:**
```env
COINBASE_API_KEY=...
COINBASE_API_SECRET=...
```

---

## Enabling Connectors

### Step 1: Configure Secrets

Add required environment variables to your `.env` file:

```env
# For OpenAI
OPENAI_API_KEY=sk-...
```

### Step 2: Validate Connector

```bash
curl -X POST http://localhost:8000/security/connectors/openai_llm/validate
```

### Step 3: Enable Connector

```bash
curl -X POST http://localhost:8000/security/connectors/openai_llm/enable
```

### Step 4: Check Readiness

```bash
curl http://localhost:8000/security/connectors/openai_llm
```

---

## Security Requirements

### Default Safety

- All connectors are **disabled by default**
- Financial connectors require `execute_financial_action` permission
- Connector usage requires authentication (if enabled)
- All connector actions are audited

### Permissions

| Connector Type | Required Permission |
|---------------|-------------------|
| LLM | None (default) |
| Data | `view_signals` |
| Email | `manage_connectors` |
| Calendar | `manage_connectors` |
| Tasks | `manage_connectors` |
| Financial | `manage_connectors`, `execute_financial_action` |

### Risk Levels

| Level | Description | Requirements |
|-------|-------------|--------------|
| Low | Read-only data access | Validation |
| Medium | Limited write access | Validation + Auth |
| High | Sensitive data access | Validation + Auth + Permission |
| Critical | Financial transactions | Validation + Auth + Admin Permission + Manual Approval |

---

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /security/connectors` | List all connectors |
| `GET /security/connectors/{id}` | Get connector details |
| `GET /security/connectors/{id}/readiness` | Check readiness |
| `POST /security/connectors/{id}/validate` | Validate configuration |
| `POST /security/connectors/{id}/enable` | Enable connector |
| `POST /security/connectors/{id}/disable` | Disable connector |
| `GET /security/audit/connectors` | View audit logs |
| `GET /security/secrets/readiness` | Check secrets status |

---

## Audit

All connector actions are logged to `connector_audit_logs` table:

- Connector enabled/disabled
- Validation attempts
- Access grants/denials
- Execution attempts

View logs:
```bash
curl http://localhost:8000/security/audit/connectors
```
