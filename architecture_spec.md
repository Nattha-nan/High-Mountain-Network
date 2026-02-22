# Mountain Network Project — Architecture Specification

## 1. Project Overview
**Course:** Computer Networks (Undergraduate Level)  
**Duration:** 4 Weeks  
**Team Size:** 5 Members  

### Objective
Design and prototype a resilient high-mountain network using:
- IP-based 3-layer architecture
- Mesh backbone (>= 2-connected topology)
- Delay-Tolerant Networking (DTN) overlay
- QoS prioritization
- Basic AI-assisted monitoring (log-based analysis)

The system must tolerate intermittent connectivity, simulate power constraints, and prioritize emergency traffic.

---

## 2. Design Principles
- Follow TCP/IP layered architecture
- Avoid single point of failure
- Support disruption-tolerant communication
- Separate traffic classes
- Ensure scalability and modularity

---

## 3. High-Level Architecture

### Layer A — Access Layer
Purpose: Connect users and IoT nodes

Technologies (simulated or lab-based):
- Wi-Fi (router-based)
- VLAN separation
- Traffic classification

Traffic Classes:
1. Emergency (High Priority)
2. Telemetry (Medium Priority)
3. Best-Effort Internet (Low Priority)

---

### Layer B — Mountain Backbone
Purpose: Interconnect mountain nodes

Topology:
- Minimum 4 nodes
- >= 2-connected mesh topology
- Dynamic routing (OSPF simulation or static multi-path)

Design Requirements:
- No single link failure disconnects network
- At least 2 independent paths between core nodes

---

### Layer C — DTN Overlay
Purpose: Maintain service during uplink disruption

Features:
- Store-and-forward buffer
- Local caching node
- Message queue simulation

Simulation Method:
- Artificial link disconnection tests
- Log-based delivery verification

---

## 4. Resilience Model

### Link Failure Handling
- Mesh topology redundancy
- Automatic failover routing

### Node Failure Handling
- Critical nodes require >= 3 logical paths (simulated)

### Disruption Handling
- Buffer-based message retention
- Deferred synchronization

---

## 5. QoS and Traffic Engineering

Apply queuing model:
- Weighted Priority Queuing
- Emergency traffic guaranteed bandwidth

Performance Metrics:
- Packet delivery ratio
- Latency under failure
- Throughput under load

---

## 6. Energy Constraint Simulation

Simulate power-aware behavior:
- Reduced service mode
- Disable best-effort traffic in low-power scenario

Document assumed power model and system degradation behavior.

---

## 7. AI-Assisted Monitoring (Basic Level)

Scope (Undergraduate Level):
- Collect logs (latency, packet loss)
- Use simple script (Python) to detect anomalies
- No autonomous routing control

---

## 8. Testing Scenarios

1. Normal operation
2. Single link failure
3. Uplink outage (DTN validation)
4. Simulated power degradation

Each test must include:
- Before/After topology state
- Measured metrics
- Observations

---

## 9. Deliverables

- Network topology diagram
- Configuration files (if applicable)
- Test result tables
- Final report
- Presentation slides

---

## 10. Evaluation Criteria (Suggested)

- Correctness of architecture design
- Resilience demonstration
- Clarity of documentation
- Team collaboration
- Technical justification using networking principles

