# Feature: Emergency Alert Banner

## 1. Trigger Conditions
Activated when `alarm_active == True` or `fsm_state == 4` (confirmed dormancy post-impact).

## 2. Visual Styling
- Container: High-contrast red background (`#DC2626`) with pulsing warning border (`#EF4444`).
- Icon: Warning triangle (`⚠️`).
- Typography: Bold uppercase 14pt sans-serif font.
- Content:
  - Exact event notification: `ALERTĂ DE CĂDERE DETECTATĂ!`
  - Target location and status: `PERSOANĂ LA SOL`
  - Total decision latency: `LATENȚĂ: <T_decizie> s` (typically 2.4 - 2.8s, accounting for the 2.5s physical dormancy verification window).

## 3. Interaction
- Provides "DEZACTIVEAZĂ ALARMA" (Dismiss) button.
- Clicking resets the backend FSM engine to State 0 (CALM) and clears the alert banner.
