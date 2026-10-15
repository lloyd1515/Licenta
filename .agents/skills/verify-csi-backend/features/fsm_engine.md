# Feature: Analytical FSM Fall Detection Engine

## 1. Mathematical State Machine (RT-Fall Contract)

The FSM models the temporal phases of a human fall:

```
[0: CALM] --- (activity > Th_act) ---> [1: WALKING]
   ^                                        |
   | (calm timeout)          (active links >= 2 & deriv > 17.5)
   |                                        v
[1: WALKING] <--- (recovery) --------- [2: IMPACT]
                                            |
                                            v
                                      [3: DORMANCY]
                                            |
                              (elapsed >= 2.5s & var < 0.20)
                                            v
                                      [4: ALARM]
```

## 2. Activity Gate
In an empty room, standard deviation of PC1 is $< 11.0$ ADC counts ($< 0.20$ in normalized simulation). The activity gate prevents false alarms by locking the FSM deterministically in State 0.

## 3. Kinetic Impact Threshold
Normalized derivative $\left|\frac{d}{dt} \frac{s}{\max |s|}\right|$ scales as $2\pi f_D$.
Ordinary walking gait generates maximum derivatives $\le 16.7$.
Gravitational fall impact produces rapid collapse with derivative $> 17.5$.

## 4. Post-Impact Dormancy Verification
Following impact, the FSM monitors a $2.5\text{ s}$ observation window.
If normalized variance $\sigma^2_{\text{post}} < 0.20$, prolonged immobility is confirmed, transitioning to State 4 (ALARM).
If the subject resumes movement ($\sigma^2_{\text{post}} \ge 0.20$), the FSM aborts the alarm and returns to State 1 (WALKING).
