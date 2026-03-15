# PSIE Observability

This document describes the observability capabilities of the Personal Strategic Intelligence Engine.

## Overview

PSIE includes comprehensive observability features to help operators understand system behavior, monitor health, track performance, and diagnose issues.

## Health Monitoring

### Components

The health monitor checks the following components:

| Component | Status | Description |
|-----------|--------|-------------|
| Application | ✅ | Checks configuration and runtime state |
| Database | ✅ | Database connectivity |
| Event Bus | ✅ | Event messaging system |
| Workflow Engine | ✅ | Workflow orchestration |
| Connectors | ✅ | External integrations readiness |
| LLM Providers | ✅ | AI provider configuration |
| Security | ✅ | Security configuration |

### Health Endpoints

```bash
# Get overall health
curl http://localhost:8000/observability/health

# Get specific component health
curl http://localhost:8000/observability/health/database
```

## Metrics

### Metric Domains

| Domain | Description |
|--------|-------------|
| system | System-level metrics |
| workflow | Workflow orchestration metrics |
| execution | Execution engine metrics |
| connector | Connector metrics |
| security | Security activity metrics |
| agent | Board agent metrics |
| api | API request metrics |

### Metrics Endpoints

```bash
# Get all metrics
curl http://localhost:8000/observability/metrics

# Get domain-specific metrics
curl http://localhost:8000/observability/metrics/workflows
curl http://localhost:8000/observability/metrics/executions
curl http://localhost:8000/observability/metrics/connectors
curl http://localhost:8000/observability/metrics/security
curl http://localhost:8000/observability/metrics/agents
curl http://localhost:8000/observability/metrics/api
```

### Metric Types

- **Counter**: Incrementing values (e.g., requests, errors)
- **Gauge**: Point-in-time values (e.g., queue depth)
- **Histogram**: Distribution of values (e.g., latency)

## Workflow Metrics

| Metric | Description |
|--------|-------------|
| workflows_started | Total workflows started |
| workflows_completed | Total workflows completed |
| workflows_failed | Total workflows failed |
| workflow_duration_ms | Workflow duration histogram |

## Execution Metrics

| Metric | Description |
|--------|-------------|
| executions_requested | Total execution requests |
| executions_approved | Approved executions |
| executions_rejected | Rejected executions |
| executions_completed | Completed executions |
| executions_failed | Failed executions |
| execution_duration_ms | Execution duration histogram |

## Connector Metrics

| Metric | Description |
|--------|-------------|
| connector_validations | Validation attempts |
| connector_enabled | Enable actions |
| connector_disabled | Disable actions |
| connector_access_granted | Successful accesses |
| connector_access_denied | Blocked accesses |
| connector_errors | Error count |

## Security Metrics

| Metric | Description |
|--------|-------------|
| login_attempts | Total login attempts |
| login_success | Successful logins |
| login_failed | Failed logins |
| unauthorized_access | Auth failures |
| forbidden_access | Permission denials |

## API Metrics

| Metric | Description |
|--------|-------------|
| api_requests | Total API requests |
| api_latency_ms | Request latency histogram |
| api_errors | Error responses |

## Alerts

### Alert Types

- **workflow_failure**: Workflow failed repeatedly
- **connector_degradation**: Connector health degraded
- **security_alert**: Security issue detected
- **execution_failure**: Execution failed
- **worker_failure**: Background worker issue

### Alert Endpoints

```bash
# List alerts
curl http://localhost:8000/observability/alerts

# Resolve an alert
curl -X POST http://localhost:8000/observability/alerts/{alert_id}/resolve
```

## Tracing

### Correlation IDs

Each workflow and event carries a correlation ID that allows tracing through the system.

```bash
# Get trace for correlation ID
curl http://localhost:8000/observability/traces/{correlation_id}
```

### Trace Information

The trace endpoint returns:
- Workflow details
- All events in the workflow
- Timestamps for each event

## Observability in Code

### Recording Metrics

```python
from app.observability import increment, record_duration, set_gauge
from app.observability.metrics_service import MetricDomain

# Increment a counter
increment("workflows_started", domain=MetricDomain.WORKFLOW)

# Record duration
record_duration("api_request_ms", 125.5, domain=MetricDomain.API)

# Set gauge
set_gauge("queue_depth", 10, domain=MetricDomain.SYSTEM)
```

### Health Checks

```python
from app.observability import get_health_monitor

health_monitor = await get_health_monitor(session)
health = await health_monitor.check_all_health()
```

## Permission Requirements

| Endpoint | Required Permission |
|----------|-------------------|
| GET /observability/health | None (public) |
| GET /observability/metrics | None (public) |
| GET /observability/metrics/* | view_observability |
| GET /observability/alerts | view_alerts |
| POST /observability/alerts/*/resolve | manage_alerts |

## Health Statuses

| Status | Description |
|--------|-------------|
| healthy | Component is operating normally |
| degraded | Component is operating with issues |
| unavailable | Component is not available |
| misconfigured | Component is misconfigured |

## Best Practices

1. **Monitor Health**: Check `/observability/health` regularly
2. **Track Alerts**: Review alerts to identify issues early
3. **Use Correlation IDs**: Use correlation IDs to trace workflows
4. **Review Metrics**: Monitor metrics for trends and anomalies
5. **Check Security**: Review security metrics for suspicious activity

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /observability/health | Get system health |
| GET | /observability/health/{component} | Get component health |
| GET | /observability/metrics | Get all metrics |
| GET | /observability/metrics/{domain} | Get domain metrics |
| GET | /observability/alerts | List alerts |
| POST | /observability/alerts/{id}/resolve | Resolve alert |
| GET | /observability/traces/{correlation_id} | Get trace |
