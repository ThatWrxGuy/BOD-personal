# System Overview

## Introduction

The Personal Strategic Intelligence Engine (PSIE) is a persistent, multi-agent system designed to act as a personal strategic board of directors. Unlike traditional AI assistants that provide single-perspective advice, PSIE leverages multiple specialized AI agents, each with a distinct constitution and area of expertise, to provide comprehensive, multi-faceted strategic guidance.

## Core Philosophy

The system operates on the principle that better decisions come from diverse, independent perspectives synthesized through structured deliberation. The user remains the CEO—ultimately responsible for all decisions—while the system provides the analytical infrastructure and advisory capacity of a board of directors.

## Key Capabilities

### Multi-Agent Analysis

The system instantiates six core board agents, each representing a different strategic perspective:

1. **Strategy Agent** - Long-range direction and positioning
2. **Finance Agent** - Resource allocation and financial implications
3. **Risk Agent** - Downside protection and risk assessment
4. **Health Agent** - Sustainability and performance capacity
5. **Operations Agent** - Implementation feasibility and execution
6. **Legacy Agent** - Values alignment and long-term meaning

### Structured Deliberation

Board meetings follow a rigorous workflow:

1. Context Assembly - Gathering relevant background
2. Independent Analysis - Each agent provides initial recommendations
3. Critique Round - Agents evaluate each other's recommendations
4. Synthesis - Combining inputs into a coherent recommendation
5. Documentation - All outputs are persisted for audit

### Persistent Memory

The system maintains:
- User profile and constitution
- Complete meeting history
- Decision records with outcome reviews
- Strategic insights extracted over time

## Architecture Highlights

### Modular Design

Each component is designed for separation:
- Agents are independently versioned
- Memory layer is abstracted
- LLM provider is swappable
- Workflows are configurable

### Audit Trail

Every recommendation includes:
- Which agent provided it
- What version of the agent's constitution was used
- Supporting reasoning
- Identified risks and tradeoffs
- Confidence score

### Future-Ready

The architecture supports:
- Prompt versioning and evaluation
- Agent performance tracking
- Controlled self-improvement
- Semantic memory extension (pgvector-ready)

## Use Cases

### Strategic Questioning

User submits a question like "Should I pursue this opportunity?" and receives a board-level analysis with multiple perspectives, critiques, and a synthesized recommendation.

### Recurring Reviews

Weekly or monthly strategic reviews are automatically scheduled, providing ongoing guidance and tracking progress against goals.

### Decision Tracking

After receiving recommendations, users log their actual decisions and later review outcomes, building a history of strategic decision-making.

## Limitations (V1)

The initial version does not include:
- Live brokerage or bank integrations
- Legal execution systems
- Voice interface
- Advanced analytics dashboards
- Mobile app packaging

These can be added in future versions while maintaining the core architecture.
