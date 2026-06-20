# Sprint 3 Retrospective

**Date:** 2026-06-20

## What went well

1. **MVP V1 successfully demonstrated** — Working packet capture and counting with real-time statistics display on web interface.
2. **Protocol analysis verified** — TCP, UDP, and ICMP counters correctly reflect actual network traffic.
3. **Fast iteration** — Core functionality implemented and tested within sprint timeline.

## What did not go well

2. **File-based communication** — Current approach tightly couples TP and CN, limits distributed deployment and creates timing inconsistencies.
3. **Testing environment challenges** — Background network activity on host OS makes accurate validation difficult; clean test environment not yet prepared.

## Action points

1. **UI fixes** — Swap metric prominence; add separate incoming/outgoing counters.
2. **Select and prototype network communication** — Replace file transfer with HTTP/REST or WebSockets between TP and CN.
