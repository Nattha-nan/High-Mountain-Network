### Annotations on Mountain Network Project (MNP)
##### A Critical Reading of the Lifecycle Documents

This document reviews the five core artifacts of the Mountain Network Project. It tracks the evolution from the **Conceptual Phase** to the **Full Containerized Deployment**, assessing each for technical robustness and complexity.

--------------------------------------------------------------------------------

#### Section I: Conceptual Framework (01_conceptual.pdf)
##### Summary
· Identifies the "Digital Divide" in mountain regions caused by unstable power and intermittent links.
· Defines the 3-Layer Architecture: Access (Village/Sensors), Backbone (Summits/Relays), and Gateway.
· Establishes the 3-level QoS: Emergency > Telemetry > Normal.
##### Annotations
· 1. The 3-layer separation is a sound architectural choice, allowing for modular scaling. (Robustness tag)
· 2. The QoS mapping (40/30/30) is well-defined but lacks a formal derivation for the "Telemetry" weight in high-congestion scenarios.

--------------------------------------------------------------------------------

#### Section II: Mathematical Formalization (02_formalization.pdf)
##### Summary
· Grounds the project in **Graph Theory** ($\kappa(G) \geq 2$) and **Percolation Theory**.
· Proposes an **Epidemiological Model (SIR)** for understanding how emergency alerts spread through the mesh.
· Defines an **Energy Model** where $E_{total} = \sum (P_{idle} + P_{tx} \cdot t_{tx} + P_{rx} \cdot t_{rx})$.
##### Annotations
· 1. The use of $\kappa(G) \geq 2$ as a design constraint is excellent for academic validation. (Abstraction tag)
· 2. The SIR model for message spread is an innovative way to treat network flooding, though its implementation in Week 3 needs further proof. (Complexity layer tag)

--------------------------------------------------------------------------------

#### Section III: Architecture & Deployment (03_arch & 05_deploy)
##### Summary
· Specifies a 13-node system deployed via `docker-compose`.
· Features a Python-based monitoring layer (`monitor.py`) for real-time anomaly detection.
· Provides REST API endpoints for node health checks (e.g., `localhost:9001/health`).
##### Annotations
· 1. The choice of Docker/Podman provides high **Reproducibility**. (Robustness tag)
· 2. The isolation of nodes into virtual bridge networks (`backbone_net`, `sensor_net`) correctly simulates physical separation.

--------------------------------------------------------------------------------

#### Overall Project Assessment
##### Strengths
1. **Clear Lifecycle:** From Graph Theory to Docker deployment.
2. **Resilience Focus:** DTN and Mesh are well-integrated.
3. **Evaluation Metrics:** Use of Packet Delivery Ratio and Latency.
##### Weaknesses
1. **Power Modeling:** The simulation of "Energy Drain" is currently scripted rather than dynamic based on traffic.
2. **Scalability:** 13 nodes are sufficient for a lab, but the OSPF convergence time for 100+ nodes is unaddressed.

*End of Annotations.*
