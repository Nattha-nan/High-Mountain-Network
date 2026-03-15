**Mountain Network Project Comparison Report**
*Conceptual Draft · Architectural Spec · Deployment Model*

**Executive Overview**
Three stages of the Mountain Network Project were evaluated across six metrics to ensure consistency and technical integrity.

| **Metric** | **Conceptual Draft** | **Architectural Spec** | **Deployment Model** |
| ------ | ------ | ------ | ------ |
| **Consistency** | 1.0 (Baseline) | 0.9 (Adds OSPF) | 0.85 (Dockerized) |
| **Formula Drift** | Basic Graph Theory | Adds Queuing Theory | Adds Energy Model |
| **Terminology** | Layer A/B/C | Access/Backbone | Containers/Endpoints |
| **Implementability**| High (Theory) | Medium (Complex) | High (Tested) |

**Key Findings**
1. **Consistency:** The transition from Layer A/B/C in the concept to Access/Backbone/Gateway in the architecture remains stable.
2. **Metric Expansion:** The Deployment Model successfully introduces measurable KPIs (Packet Delivery Ratio, Energy Level) that were only qualitative in the Conceptual Draft.
3. **Resilience Gap:** The Architectural Spec identifies the need for OSPF convergence testing, which is successfully implemented in the `demo.py` script of the Deployment Model.

**Conclusion**
The Deployment Model is the strongest artifact, providing a functional 13-node simulation that validates the theoretical connectivity claims made in the early stages.

*Report prepared: March 2026*