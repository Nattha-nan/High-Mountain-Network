# High-Mountain Resilient Network
## Sprint_Plan.md
รายวิชา CP352005 เครือข่ายคอมพิวเตอร์
ระยะเวลาโครงการ: 4 สัปดาห์
ทีม: 5 คน

---

# Sprint Overview

| Sprint | Theme | Core Output |
|--------|-------|------------|
| Week 1 | Architecture & Foundation | Mesh topology + Cost model |
| Week 2 | Routing Implementation | OSPF multi-path working |
| Week 3 | DTN & QoS Integration | Store-and-forward + Priority scheduling |
| Week 4 | Validation & Delivery | Tested system + Demo |

---

# Week 1 — Architecture & Foundation Sprint

## Objectives
- ออกแบบ ≥2-connected mesh topology
- กำหนด routing cost model
- นิยาม traffic classes
- เตรียม simulation framework

## Key Tasks

### Architect
- ออกแบบ topology (≥4 nodes)
- กำหนด cost function:
  Cost = αLatency + βHop + γLinkStability
- กำหนดค่า default (0.5, 0.3, 0.2)

### Engineer
- Setup Python + NetworkX
- สร้าง prototype graph
- ทดสอบ shortest path

### Specialist
- นิยาม Traffic Classes:
  - Emergency
  - Telemetry
  - Best-Effort
- ร่าง energy degradation mode

### DevOps
- Setup Git repository
- กำหนด branch strategy:
  - main
  - dev
  - feature/*
- เตรียม README

### Tester/QA
- สร้าง Master Test Plan
- กำหนด Failure Scenarios:
  - Single link failure
  - Node failure
  - Congestion

## Definition of Done (Week 1)
- Topology diagram เสร็จ
- Cost model ระบุชัดเจน
- Repo พร้อมใช้งาน
- Test plan ร่างเสร็จ

---

# Week 2 — Routing Implementation Sprint

## Objectives
- Implement OSPF multi-path
- ทดสอบ failover
- เริ่มพัฒนา DTN buffer

## Key Tasks

### Engineer
- Implement routing table
- รองรับ multi-path
- บันทึก routing decisions

### Architect
- Review routing logic
- ตรวจ convergence behavior

### Specialist
- Validate cost weights
- วิเคราะห์ latency model

### DevOps
- ดูแล merge + integration
- ตรวจ build consistency

### Tester/QA
- เขียน unit tests:
  - Routing correctness
  - Failover
- วัด convergence time

## Milestone
Single link failure → network must not partition

## Definition of Done (Week 2)
- Routing ทำงานจริง
- Failover สำเร็จ
- Unit tests ผ่าน

---

# Week 3 — DTN & QoS Integration Sprint

## Objectives
- เพิ่ม DTN store-and-forward
- Implement QoS priority
- จำลอง 6-hour outage

## Key Tasks

### Engineer
- สร้าง buffer queue
- Implement priority scheduling
- เชื่อม routing + DTN

### Specialist
- Validate:
  - Emergency ไม่ drop
  - Best-effort drop ก่อน
- ทดสอบ Low-power mode

### DevOps
- ดูแล integration stability
- Backup build ก่อน merge ใหญ่

### Tester/QA
- Run:
  - Uplink outage test
  - Congestion simulation
- วัด Packet Delivery Ratio

## Success Criteria
- Emergency packet delivered during outage
- QoS differentiation ชัดเจน

---

# Week 4 — Validation & Delivery Sprint

## Objectives
- ทดสอบครบทุก scenario
- ปรับ performance
- เตรียม demo และรายงาน

## Key Tasks

### Engineer
- Optimize routing (<1s decision)
- Code cleanup

### Architect
- ตรวจ final architecture consistency
- Approve release candidate

### Specialist
- วิเคราะห์:
  - Delivery ratio ≥95%
  - Energy-aware behavior

### DevOps
- Tag version v1.0
- Prepare submission ZIP

### Tester/QA
- Full regression test
- Coverage ≥80%
- จัดทำ test report

---

# Demo Requirements

Demo ต้องแสดง:

1. Mesh failover
2. DTN buffering
3. QoS prioritization
4. Power degradation mode
5. Packet delivery analysis

---

# Risk Control Plan

## หากล่าช้า
- ลดจำนวน node ≤5
- ตัด visualization ขั้นสูง

## หาก integration ล้มเหลว
- Rollback
- ทดสอบ layer-by-layer
- ใช้ mock interface

---

# Daily Standup Template

What I did yesterday:
-

What I will do today:
-

Blockers:
-

Progress:
- Routing: __%
- DTN: __%
- Testing: __%
- Documentation: __%

---

# Workload Estimation

6–10 ชั่วโมง / คน / สัปดาห์  
รวมประมาณ 120 ชั่วโมงตลอดโครงการ

---

# Final Deliverables

- Network topology diagram
- Simulation code
- Test report
- Architecture specification
- Implementation plan
- Demo presentation
