# Feature: Room Map & 2D Kinematic Tracking

## 1. Geometric Coordinate Space
- Monitored area: 5m x 5m coordinate frame ($x \in [-2.5, 2.5]$, $y \in [-2.5, 2.5]$ meters).
- Node positions:
  - Node 1: $(-2.0, 1.2)\text{ m}$
  - Node 2: $(2.0, 1.2)\text{ m}$
  - Node 3: $(0.0, -2.0)\text{ m}$

## 2. Dynamic Fresnel Mesh Rendering
- Direct LOS vectors connect node pairs ($L_{12}, L_{23}, L_{31}$).
- 1st Fresnel zone boundaries rendered as confocal ellipses ($r_1 = \frac{1}{2}\sqrt{\lambda D}$).
- Link line width and color adapt dynamically:
  - Blue (`#38BDF8`): Quiescent / CALM ($\text{Activity} < 0.2$).
  - Green (`#34D399`): Walking perturbation ($0.2 \le \text{Activity} < 0.7$).
  - Red (`#EF4444`): Violent collapse / Impact ($\text{Activity} \ge 0.7$).

## 3. 2D Target Avatar
- Rendered as circular target with outer pulsing aura.
- Directional arrow projects kinematic velocity vector $(v_x, v_y)$.
- Avatar color reflects current FSM state:
  - Cyan: Standing / Calm.
  - Green: Walking in room.
  - Amber: Impact event.
  - Red: Fallen / Emergency.
