# Customer Meeting Summary

**Date:** 2026-06-20

**Participants:**
- Customer: Mikhail Kuskov
- Team: Aidar Badykov, Timur Likhunov, Victoria Kalka

**Artifacts demonstrated:**
- MVP V1 Traffic Processor running locally on VM
- Web interface showing packet counters
- Data flow and protocol analysis

**Discussion points:**
- Successfully demonstrated MVP V1 with packet counting functionality
- Tested with various network activities
- Identified need for network-based communication in future versions
- Discussed testing methodology for verifying packet counting accuracy

**Decisions:**
- MVP V1 is approved as is with minor UI improvements
- File-based communication is acceptable for MVP V1
- Network-based communication should be implemented in MVP V2

**Action points:**
1. **New task** Prepare a clean test environment and scripts for accurate packet counting verification
2. **UI changes:**
   - Swap prominence of "packets per second" and "total packets"
   - Add separate incoming/outgoing counters

**Risks:**
- File-based communication creates tight coupling between components
- Testing with accurate packet counting requires clean environment without background network activity
- Timing issues observed between file writes and reads

**Feedback:**
- Bidirectional traffic visualization provides more descriptive information
- Protocol analysis appears to work correctly based on demonstration

**Customer approvals:**
- MVP V1 functionality is approved
- File-based communication is acceptable for MVP V1 but must evolve

**Resulting changes:**
- **MVP V1**:
  - Bidirectional counters (incoming/outgoing)
  - Protocol analysis (TCP, UDP, ICMP)

- **MVP V2**:
  - Replace file-based communication

**Notes**
 - UI changes requested are non-blocking and can be implemented
