# ADR-002: In-Memory Storage with PostgreSQL Readiness

## Status

**Accepted**

## Date

2026-06-30

## Context

The CNSS receives traffic statistics from the TP and must serve them to the web dashboard. The system needs to store the latest statistics and make them available for fast retrieval.

### Quality Requirements Addressed

- **QR-001:** Dashboard metric update delay ≤1 second

### Alternatives Considered

1. **Full PostgreSQL persistence** — Provides durability and historical querying, but adds latency and complexity.
2. **Redis in-memory store** — Fast and supports expiration, but adds another dependency.
3. **In-memory only (current)** — Simplest and fastest, but data is lost on restart.
4. **SQLite** — Lightweight and persistent, but not suitable for concurrent write access in a containerized environment.

## Decision

Use **in-memory storage** for the current implementation, with **PostgreSQL readiness** for future persistence.

- The CNSS stores only the latest `Packet` object in a global variable (`last_info`).
- The CNSS serves `GET /packets` directly from this in-memory variable.
- The Docker Compose stack includes a PostgreSQL container (`db`) and the CNSS has Alembic migrations ready, but the CNSS does not yet write to the database.
- The `Packet` schema is designed to be compatible with both in-memory and SQL storage.

## Consequences

### Positive

- **Low latency:** Memory access is sub-millisecond, supporting QR-001 (≤1s update delay).
- **Simplicity:** No ORM, no connection pooling, no transaction management. Easy to understand and debug.
- **Fast development:** The team can iterate quickly without worrying about database schema changes.
- **PostgreSQL readiness:** The infrastructure (container, migrations) is in place, so enabling persistence is a future increment.

### Negative

- **No durability:** Data is lost when the CNSS container restarts. Historical analysis is not possible.
- **No historical data:** The dashboard shows only the latest snapshot, not trends over time.
- **Shared state:** The global `last_info` variable creates shared state that complicates testing (tests must reset it).
- **Scalability limit:** The current design cannot support multiple CNSS instances sharing state.

### Trade-offs

- **Durability vs. Latency:** We prioritized low latency for real-time dashboard updates over data durability. For a monitoring tool, the latest data is more important than historical data.
- **Simplicity vs. Scalability:** The in-memory approach is simple and works for a single instance. Future scaling would require moving to a shared store (Redis or PostgreSQL).

## Related ADRs

- [ADR-001](ADR-001-async-http-communication.md) — HTTP communication benefits from fast in-memory storage.
- [ADR-003](ADR-003-scapy-packet-capture.md) — The TP generates data that the CNSS stores.

## References

- [docs/quality-requirements.md](../../quality-requirements.md) — QR-001
- `src/cnss/app/main.py` — Implementation of in-memory storage
- `src/cnss/app/schemes/packet.py` — Packet schema
- `src/cnss/alembic.ini` — Alembic migrations for PostgreSQL readiness
