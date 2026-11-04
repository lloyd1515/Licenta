# Jurnal studiu `src/`

Reguli: un fișier sau un concept pe mesaj, quiz text cu variante A/B/C, nu se editează `src/`.

## Plan (de la simplu la complex)

### Nivel 1 — constante și fișiere de pornire
1. `src/csi/room.py`
2. `src/csi/__init__.py`, `src/csi/gui/__init__.py` (goale)
3. `src/firmware/esp32_csi_node/CMakeLists.txt`, `main/CMakeLists.txt`, `sdkconfig.defaults`
4. `src/simulation-remotion/package.json`, `tsconfig.json`, `src/index.ts`, `src/Root.tsx`, `src/MainScene.tsx`

### Nivel 2 — logică scurtă
5. `src/csi/record.py`
6. `src/csi/localization.py`
7. `src/csi/udp_sim.py`
8. `src/csi/dsp.py`
9. `src/csi/gui/__main__.py`
10. `src/csi/gui/screenshots.py`
11. `src/simulation-remotion/src/layout.ts`, `HumanModel.tsx`, `SubcarrierStrings.tsx`

### Nivel 3 — date și algoritmi
12. `src/csi/packets.py`
13. `src/csi/simulator.py`
14. `src/csi/fall_detector.py`
15. `src/firmware/esp32_csi_node/main/main.c`
16. `src/csi/gui/frame_source.py`
17. `src/csi/gui/frames.py`
18. `src/csi/gui/charts.py`
19. `src/simulation-remotion/src/SummaryCards.tsx`, `SecurityCamera.tsx`

### Nivel 4 — fișiere mari și integrare
20. `src/csi/gui/status_panel.py`
21. `src/csi/gui/room_map.py`
22. `src/csi/gui/theme.py`
23. `src/csi/gui/main_window.py`
24. `src/csi/figures.py`
25. `src/simulation-remotion/src/Scene3D.tsx`, `Hud.tsx`, `timeline.ts`
26. `src/tests/test_udp_transport.py`

Nu se citesc complet: `sdkconfig` (1906 linii, generat de ESP-IDF), `src/csi/data/*.npz` (date binare).

## Sesiuni

### 2026-11-03 — pas 1 `room.py`
- Explicat: constantele camerei și `extra_path_m`.
- Quiz: `extra_path_m` pentru un punct pe linia directă TX–RX. Răspuns corect: B (0 m).
- Status: în curs (aștept răspunsul).
- Întrebare: de ce `CENTER_FREQ_HZ`? Răspuns: dă `WAVELENGTH_M` (12.3 cm) și frecvența fiecărei subpurtătoare (`simulator.py:40`). Quiz pas 1 încă deschis.
- Întrebare: de ce `WAVELENGTH_M`? Răspuns: convertește distanța și viteza în fază/Doppler; folosit în `simulator.py:111,120`, `room_map.py:134-137` (Fresnel), `charts.py:87`.
- Cerere: explicație linie cu linie pentru `room.py`, cu motivul fiecărei alegeri. Dat: tuple vs list, dict pentru noduri, `axis=-1` pentru un punct sau un vector de puncte (`simulator.py:109`), indicele 0 exclus (DC), 312.5 kHz = 20 MHz / 64. Quiz pas 1 încă deschis.
- 2026-11-04: pagină ilustrată pentru `room.py` (GSAP 3.12.5, SVG): https://claude.ai/artifact/CRnjoz6vygTaiZSnVRLoyV. Conține elipsa de drum în plus egal și prima zonă Fresnel. Quiz pas 1 încă deschis.
- 2026-11-04: pagini ilustrate pentru toate cele 44 de fișiere din `src/`, în `docs/learning/ilustrat/` (index: `ilustrat/index.html`; room.py rămâne `room-ilustrat.html`). Date reale generate din cod în `ilustrat/assets/data/*.js`.
- Constatări verificate pe date, notate în pagini: coloanele CSI 21–30 sunt ~0 în toate capturile (feliile din packets.py par să păstreze subpurtătoare de gardă, după ordinea LLTF din ESP-IDF); capturile au doar nodurile 1 și 2, analiza folosește doar nodul 1; Doppler real ≤ 16.8 Hz (rata 33.5 Hz), deci linia de 35 Hz nu e atinsă în replay; panta maximă în test C 18.9 vs prag 17.5; poziția și înălțimea din GUI sunt ilustrative (din stare); replay rulează ~1.5× mai repede; vTaskDelay(1) la 100 Hz → max ~100 cadre/s, nu 250 Hz ca în README; valorile din video Remotion sunt scrise de mână.
