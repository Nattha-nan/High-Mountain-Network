# Mountain Network Project — 4-Week Implementation Plan

## Project Context
Undergraduate Computer Networks Term Project  
Duration: 4 Weeks  
Team Members: 5

---

# Week 1 — Design & Planning Phase

## Goals
- Finalize architecture
- Assign roles
- Create topology diagram

## Tasks
1. Literature review (DTN, mesh topology, QoS)
2. Define network topology (>= 4 nodes mesh)
3. Define traffic classes
4. Select tools (e.g., Packet Tracer, GNS3, NS-3, Linux VMs)
5. Create architecture diagram

## Deliverables
- Architecture diagram
- Task allocation sheet
- Simulation plan

## Role Assignment
- Member 1: Backbone topology & routing
- Member 2: Access layer configuration
- Member 3: DTN simulation design
- Member 4: QoS implementation
- Member 5: Documentation & testing coordination

---

# Week 2 — Core Network Implementation

## Goals
- Build mesh backbone
- Implement routing redundancy

## Tasks
1. Configure routing (OSPF or static multi-path)
2. Verify >=2-connected property
3. Test link failure scenarios
4. Document routing tables

## Testing
- Disconnect one link
- Measure convergence time

## Deliverables
- Routing configuration files
- Failure test results

---

# Week 3 — DTN & QoS Integration

## Goals
- Implement disruption handling
- Implement traffic prioritization

## Tasks
1. Simulate uplink outage
2. Implement store-and-forward mechanism
3. Configure traffic priority queues
4. Measure packet delay differences

## Testing
- 6-hour simulated disruption (logical simulation acceptable)
- Emergency vs Best-effort comparison

## Deliverables
- Buffer simulation logs
- QoS performance tables

---

# Week 4 — Validation & Presentation

## Goals
- Full system testing
- Prepare final documentation

## Tasks
1. Run integrated failure scenarios
2. Collect performance metrics
3. Analyze resilience behavior
4. Write final report
5. Prepare presentation slides

## Final Demonstration Must Show
- Mesh resilience
- DTN buffering
- QoS prioritization
- Power degradation mode

---

# Risk Management

## Technical Risks
- Routing misconfiguration
- Simulation tool limitations
- Time constraints

## Mitigation
- Keep topology small (4–5 nodes)
- Use incremental testing
- Maintain shared documentation

---

# Assessment Alignment

This plan ensures:
- Application of TCP/IP principles
- Use of routing protocols
- Demonstration of resilience
- Performance evaluation using measurable metrics
- Team collaboration

---

# Suggested Tools

- Cisco Packet Tracer or GNS3
- Linux VMs
- Python (for log analysis)
- Wireshark (traffic inspection)
- Draw.io or Lucidchart (diagram)

---

# Expected Outcome After 4 Weeks

Students will demonstrate:
- Practical understanding of layered architecture
- Resilient network design principles
- Traffic engineering fundamentals
- Disruption-tolerant communication concepts

The final output should resemble a small-scale resilient network prototype suitable for academic evaluation.

