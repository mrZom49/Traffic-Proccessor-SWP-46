# Traffic Processor Architecture

This document is the canonical architecture index for the Traffic Processor (TP) system. It describes the current delivered architecture and links to supporting architecture artifacts.

## Overview

Traffic Processor is a network visibility and control tool that captures live packet counters, per-connection statistics, and traffic history, and supports blocking, tunneling, and failover behaviors. The system consists of two main components:

- **Traffic Processor (TP)** — A Python-based packet sniffer that captures network traffic, classifies packets, computes statistics, and sends data to the CNSS.
- **Control and Status Server (CNSS)** — A FastAPI web application that receives, stores, and serves traffic statistics via a REST API and a static web dashboard.

## Architecture Views

### Static View

The static view describes the system's component structure, interfaces, and relationships.

- **Diagram:** [component-diagram.puml](static-view/component-diagram.puml)
- **Rendered form:** The diagram is rendered as SVG [component-diagram.svg](static-view/component-diagram.svg)
- **Discussion:** See the [Static View](#static-view) section below.

### Dynamic View

The dynamic view describes key runtime interactions and workflows.

- **Diagram:** [sequence-diagram.puml](dynamic-view/sequence-diagram.puml)
- **Rendered form:** The diagram is rendered as SVG [sequence-diagram.svg](dynamic-view/sequence-diagram.svg)
- **Discussion:** See the [Dynamic View](#dynamic-view) section below.

### Deployment View

The deployment view describes the runtime deployment structure and environment boundaries.

- **Diagram:** [deployment-diagram.puml](deployment-view/deployment-diagram.puml)
- **Rendered form:** The diagram is rendered as SVG [deployment-diagram.svg](deployment-view/deployment-diagram.svg)
- **Discussion:** See the [Deployment View](#deployment-view) section below.

## Architecture Decision Records (ADRs)

The following ADRs document key architectural decisions:

| ADR | Title | Quality Requirements Addressed |
|-----|-------|-------------------------------|
| [ADR-001](adr/ADR-001-async-http-communication.md) | Use Asynchronous HTTP Communication Between TP and CNSS | QR-001, QR-003 |
| [ADR-002](adr/ADR-002-in-memory-storage.md) | In-Memory Storage with PostgreSQL Readiness | QR-001 |
| [ADR-003](adr/ADR-003-scapy-packet-capture.md) | Scapy as Packet Capture Library | QR-002, QR-003 |

These decisions address the quality requirements defined in [docs/quality-requirements.md](../quality-requirements.md).

---

## Static View

### Component Diagram

The component diagram below shows the main internal components of the system, external systems they interact with, and the communication paths between them.

![Component Diagram](static-view/component-diagram.svg)

**Source:** [component-diagram.puml](static-view/component-diagram.puml)

### What the Diagram Shows

The diagram illustrates:

- **Traffic Processor (TP)** — The core packet capture and analysis component. It consists of:
  - **Packet Sniffer** — Uses Scapy to capture packets from the network interface.
  - **Packet Classifier** — Classifies packets by protocol (TCP, UDP, ICMP, Other).
  - **Direction Tracker** — Determines whether packets are incoming or outgoing based on local IP/MAC.
  - **Statistics Calculator** — Computes packet rates (PPS, BPS) and aggregates counters.
  - **HTTP Sender** — Sends statistics batches to the CNSS via HTTP POST.

- **Control and Status Server (CNSS)** — The FastAPI web application. It consists of:
  - **API Endpoints** — `POST /` receives statistics, `GET /packets` retrieves the latest data.
  - **Packet Store** — Maintains the latest packet statistics in memory (with PostgreSQL readiness).
  - **Static Files** — Serves the web dashboard (HTML, CSS, JavaScript).

- **External Systems:**
  - **Network Interface** — The source of live packet data.
  - **End User** — Accesses the web dashboard to view traffic statistics.
  - **PostgreSQL** — Planned persistent storage for historical data.

### Coupling and Cohesion

The codebase exhibits **moderate coupling** with **good cohesion**:

- **TP** is a single cohesive class (`TrafficProcessor`) that encapsulates packet capture, classification, statistics, and HTTP sending. This is cohesive but somewhat monolithic — all responsibilities reside in one class.
- **CNSS** is well-separated into FastAPI routes (`main.py`), Pydantic schemas (`schemes/`), and configuration (`core/config.py`). This promotes separation of concerns.
- **Coupling** between TP and CNSS is through the HTTP API contract (the `Packet` schema). This is a loose, interface-based coupling that allows the two components to evolve independently as long as the schema remains compatible.
- The use of environment variables and configuration files (`config.py`, `.env_template`) supports runtime configurability without code changes.

### Maintainability Implications

- **Positive:** The clear separation between TP (data producer) and CNSS (data consumer) supports independent development and deployment. The API-driven communication enables future replacement of either component.
- **Positive:** The use of Pydantic schemas provides validation and clear data contracts, reducing integration errors.
- **Concern:** The TP class is large and handles multiple responsibilities (sniffing, classification, direction tracking, rate calculation, HTTP sending). This could be refactored into smaller, more focused classes to improve testability and maintainability.
- **Concern:** The CNSS currently stores only the latest packet in memory (`last_info` global). This is a simplification that limits historical analysis and creates shared state in tests.

### Quality Requirements Support and Constraints

| Quality Requirement | How the Structure Supports It | Constraints |
|---------------------|-------------------------------|-------------|
| **QR-001** (Dashboard update ≤1s) | HTTP sender posts every `delay` seconds (default 0.5s); FastAPI serves immediately from memory. | Network latency between TP and CNSS could add delay. |
| **QR-002** (Startup ≤500ms) | Minimal dependencies; Scapy loads quickly; no heavy initialization. | Interface detection and Scapy import may vary by environment. |
| **QR-003** (Throughput ≥1000 Kbps) | Scapy is efficient for packet capture; Python overhead is acceptable for moderate traffic. | High traffic may cause packet drops; the single-threaded design limits scalability. |

---

## Dynamic View

### Sequence Diagram

The sequence diagram below illustrates the end-to-end flow of a traffic statistics update from packet capture to dashboard display.

![Sequence Diagram](dynamic-view/sequence-diagram.svg)

**Source:** [sequence-diagram.puml](dynamic-view/sequence-diagram.puml)

### Scenario Represented

The diagram represents the **"Live Traffic Update"** scenario:

1. The TP captures packets from the network interface.
2. The TP classifies each packet and updates statistics.
3. On a scheduled interval (every `delay` seconds), the TP sends a batch of statistics via HTTP POST to the CNSS.
4. The CNSS receives the data, validates it against the `Packet` schema, and stores it in memory.
5. An end user accesses the web dashboard, which fetches the latest statistics via `GET /packets`.
6. The CNSS returns the stored data, and the dashboard renders it.

### Why This Scenario Is Important

This scenario is the **core value proposition** of the product: providing real-time network visibility. Its performance directly impacts user satisfaction and operational effectiveness. The flow involves multiple components and interactions, making it a good test of the system's integration and responsiveness.

### Architecture Decisions, Integration Boundaries, and Quality Requirements

| Aspect | Insight |
|--------|---------|
| **Architecture Decisions** | The choice of HTTP as the communication protocol (ADR-001) enables cross-platform compatibility and simple debugging. The in-memory storage (ADR-002) prioritizes low-latency dashboard updates over historical persistence. |
| **Integration Boundaries** | The HTTP API between TP and CNSS is the primary integration boundary. It is defined by the `Packet` schema, which must remain stable across versions. |
| **Quality Requirements** | This scenario directly tests **QR-001** (update delay ≤1s) and **QR-003** (throughput capacity). The sequence shows how delays in any step (network latency, processing time, API response) could affect the end-user experience. |

---

## Deployment View

### Deployment Diagram

The deployment diagram below shows the runtime deployment structure, including services, datastores, external platforms, and environment boundaries.

![Deployment Diagram](deployment-view/deployment-diagram.svg)

**Source:** [deployment-diagram.puml](deployment-view/deployment-diagram.puml)

### What the Diagram Shows

The diagram illustrates:

- **Deployment Nodes:**
  - **Docker Host** — The physical or virtual machine running Docker.
  - **Docker Compose** — Orchestrates three containers: `tproc` (TP), `cnss` (CNSS), and `db` (PostgreSQL).

- **Containers:**
  - **tproc** — Runs the Traffic Processor. Captures packets from the host's network interface (using `network_mode: host` or similar).
  - **cnss** — Runs the FastAPI server. Exposes ports `8000` (API) and serves static files.
  - **db** — Runs PostgreSQL (planned for persistent storage). Not yet fully integrated but included in the Compose stack.

- **External Systems:**
  - **End User** — Accesses the CNSS via HTTP.
  - **Network** — The source of live traffic.

- **Environment Boundaries:**
  - The Docker Compose network isolates the containers from each other and from the host.
  - The CNSS is exposed to the host on port 8000 for user access.

### Why This Deployment Model Was Chosen

- **Containerization with Docker** ensures consistency across development, testing, and production environments. It eliminates "works on my machine" issues.
- **Docker Compose** simplifies multi-container orchestration. It allows the team to start the entire stack with a single command (`docker compose up`).
- **Separation of concerns** — Each component runs in its own container, making it easy to update, scale, or replace individual services.
- **PostgreSQL readiness** — The Compose stack includes a PostgreSQL container, even though the CNSS currently uses in-memory storage. This prepares the system for future persistence without changing the deployment model.

### How the Current Deployment Supports or Constrains the Product

| Aspect | Support | Constraint |
|--------|---------|------------|
| **Development** | Fast iteration: `docker compose up` starts the full stack. Code changes are reflected on rebuild. | Requires Docker knowledge and a Docker-enabled environment. |
| **Testing** | CI runs a Docker Compose smoke test to validate the stack starts correctly. | The smoke test does not yet verify end-to-end packet delivery or database contents. |
| **Production** | Containerization simplifies deployment to any cloud or on-premise environment. | The current single-instance deployment does not support horizontal scaling or high availability. |
| **Observability** | Logs are available via `docker logs`. | No centralized logging or monitoring is configured. |

### Operational Considerations for the Customer

- **Deployment:** The customer must have Docker and Docker Compose installed. They run `docker compose up --build` in the `src/` folder.
- **Verification:** To verify TP is running, the customer can run `docker exec tproc cat /data/data.txt | head -3`.
- **Configuration:** Environment variables (`.env` file) control TP behavior (interface, URL, delay) and CNSS settings.
- **Network:** The TP container must have access to the host's network interface for packet capture. This may require privileged mode or specific Docker network settings.
- **Data Persistence:** Currently, data is not persisted across restarts. The customer should be aware that historical data is lost when containers are stopped.
- **Future:** The PostgreSQL container is ready for persistence, but the CNSS does not yet use it. The customer should monitor future releases for this capability.

---

## ADR Index

The following ADRs are maintained in [docs/architecture/adr/](adr/):

- [ADR-001: Use Asynchronous HTTP Communication Between TP and CNSS](adr/ADR-001-async-http-communication.md)
- [ADR-002: In-Memory Storage with PostgreSQL Readiness](adr/ADR-002-in-memory-storage.md)
- [ADR-003: Scapy as Packet Capture Library](adr/ADR-003-scapy-packet-capture.md)

Each ADR is linked from the relevant quality requirements in [docs/quality-requirements.md](../quality-requirements.md).
