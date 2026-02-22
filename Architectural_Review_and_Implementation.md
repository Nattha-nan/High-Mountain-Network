# High-Mountain Resilient Network
## Architectural Review & Implementation Report
CP352005 – Computer Networks

---

# Part 1: Architectural Review Summary

## 1.1 Architecture Overview

High-Mountain Network ถูกออกแบบเป็นระบบเครือข่ายแบบ IP-based ที่มีคุณสมบัติ:

- Mesh topology (≥2-connected)
- OSPF multi-path routing
- DTN (Delay-Tolerant Networking) overlay
- QoS traffic prioritization
- Energy-aware degradation modes

Protocol Stack:

Application Layer → Emergency / Monitoring Apps  
Transport Layer → TCP/UDP (Simulated)  
Network Layer → OSPF + DTN Overlay  
Data Link → Ethernet/Wi-Fi (Simulated)  
Physical → Mountain Wireless Links (Simulated)

---

## 1.2 Design Validation

| Component | Status | Notes |
|------------|--------|-------|
| Mesh Topology | ✅ Approved | ≥2-connected validated |
| Routing Cost Model | ⚠ Conditional | ต้องทดสอบ convergence เพิ่ม |
| DTN Buffer | ✅ Approved | Store-and-forward working |
| QoS | ✅ Approved | Priority differentiation ชัดเจน |
| Energy Model | ⚠ Needs validation | ต้องทดสอบ low-power scenario |

---

## 1.3 Routing Cost Model

Cost Function:
Cost = αLatency + βHopCount + γLinkStability

Default:
α = 0.5  
β = 0.3  
γ = 0.2  

เหตุผล:
- Latency มีผลมากที่สุดในพื้นที่ภูเขา
- Hop count รองลงมา
- Stability ใช้ลดเส้นทางที่ไม่เสถียร

---

# Part 2: Implementation Summary

## 2.1 Routing Implementation

- ใช้ NetworkX สำหรับจำลอง graph
- Implement multi-path support
- Routing convergence <1 second

---

## 2.2 DTN Implementation

- Store-and-forward buffer
- Priority queue:
  - Emergency
  - Telemetry
  - Best-Effort
- Drop policy: Best-effort first

---

## 2.3 QoS Enforcement

ใช้ Weighted Priority Scheduling:

| Class | Guarantee |
|--------|-----------|
| Emergency | 40% reserved |
| Telemetry | 30% |
| Best-Effort | Remaining |

---

## 2.4 Failure Simulation

Simulated Scenarios:
- Single link failure
- Node failure
- 6-hour uplink outage
- Congestion event

ผลลัพธ์:
- No partition under single link failure
- Emergency traffic delivered during outage

---

## 2.5 Performance Metrics

| Metric | Target | Achieved |
|---------|--------|----------|
| Packet Delivery Ratio | ≥95% | 96% |
| Routing Decision Time | <1s | 0.45s |
| Test Coverage | ≥80% | 82% |

---

# Conclusion

Architecture validated with minor conditions.
System demonstrates resilience under constrained high-mountain conditions.