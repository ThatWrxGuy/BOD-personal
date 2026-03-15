# Worker Scheduling Documentation

This document outlines the worker scheduling for the BOD Strategic Intelligence Engine.

## Overview

Workers run in the background to perform periodic tasks, continuous monitoring, and event-driven processing.

## Worker Schedule

### Continuous Workers

| Worker | Frequency | Purpose |
|--------|----------|---------|
| Strategy Loop | Continuous | Main strategic reasoning loop |
| Signal Processor | Continuous | Process incoming signals |
| Event Bus | Continuous | Handle async events |

### Periodic Workers

| Worker | Frequency | Duration | Dependencies |
|--------|-----------|----------|--------------|
| Forecast Engine | Weekly | ~30s | Domain data |
| Strategy Simulation | Weekly | ~2min | Forecast output |
| Monte Carlo | Weekly | ~5min | Strategy definitions |
| Domain Optimization | Daily | ~1min | Domain scores |
| Intervention Evaluation | Daily | ~30s | Intervention history |
| Health Monitor | Hourly | ~10s | System health |

### Event-Driven Workers

| Worker | Trigger | Purpose |
|--------|---------|---------|
| Intervention Engine | Risk threshold | Execute interventions |
| Command Router | User command | Process user requests |
| Learning Engine | New outcomes | Update learned patterns |

## Timing Considerations

### Recommended Offsets

To prevent collisions, workers should be offset:

- `Forecast Engine`: Sunday 02:00 UTC
- `Strategy Simulation`: Sunday 04:00 UTC  
- `Monte Carlo`: Sunday 06:00 UTC
- `Domain Optimization`: Daily 01:00 UTC
- `Intervention Evaluation`: Daily 03:00 UTC
- `Health Monitor`: Every hour at :15

### Collision Prevention

- Monte Carlo should run after Strategy Simulation
- Strategy Simulation should run after Forecast
- Intervention Evaluation should run after Intervention Engine

## Current Status

Worker scheduling is managed via:

- `app/core/scheduler.py` - Main scheduler
- `app/workers/` - Individual worker implementations

## Configuration

Workers can be configured in `config/workers.yaml`:

```yaml
workers:
  forecast:
    enabled: true
    schedule: "0 2 * * 0"  # Weekly Sunday 02:00
    timeout: 300
  
  simulation:
    enabled: true
    schedule: "0 4 * * 0"  # Weekly Sunday 04:00
    timeout: 600
  
  monte_carlo:
    enabled: true
    schedule: "0 6 * * 0"  # Weekly Sunday 06:00
    timeout: 1800
```

## Monitoring

Worker execution is logged and can be monitored via:

- Executive Command Center dashboard
- Health monitor endpoint
- Log aggregation

## Future Improvements

Planned enhancements:
- Dynamic scheduling based on system load
- Dependency-aware scheduling
- Priority-based worker queuing

---

*Last Updated: 2026-03-12*
