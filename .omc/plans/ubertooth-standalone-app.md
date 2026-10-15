# Plan: Ubertooth Standalone App (Independent de ubertooth-windows-host)

**Data**: 2026-04-13  
**Obiectiv**: Aplicație Windows standalone (.msi / .exe) care nu depinde de repo-ul ubertooth-windows-host și nu necesită Node.js instalat pe mașina țintă.

---

## Rezumat Requirements

| # | Requirement | Criteriu de acceptare |
|---|-------------|----------------------|
| R1 | Nu există nicio referință la ubertooth-windows-host în codul nou | `grep -r "ubertooth-windows-host"` returnează 0 rezultate |
| R2 | Nu necesită Node.js pe mașina țintă | Rulează pe Windows fresh (fără Node, fără npm) |
| R3 | Interfațează cu hardware Ubertooth One via USB | `ubertooth-util -v` returnează firmware version când hardware e conectat |
| R4 | Distribuibil ca installer MSI sau .exe portabil | `tauri build` generează `ubertooth-app_x.x.x_x64_en-US.msi` |
| R5 | Logica reimplementată original (nu copiată) | Fiecare modul e scris de la zero, cu citare în bibliografie |
| R6 | Bundlează binarele oficiale ubertooth-*.exe | Binarele din greatscottgadgets/ubertooth sunt prezente în pachet |

---

## Arhitectura Nouă

```
ubertooth-standalone/          ← proiect NOU, independent
├── src-tauri/                 ← Rust backend (Tauri)
│   ├── src/
│   │   ├── main.rs            ← entry point + Tauri commands
│   │   ├── discovery.rs       ← PnP USB discovery (PowerShell WMI)
│   │   ├── runner.rs          ← spawn ubertooth-*.exe, stream output
│   │   ├── safety.rs          ← antenna check, duty-cycle guard
│   │   └── commands/          ← un modul per comandă (scan, btle, etc.)
│   ├── resources/             ← binare bundlate
│   │   ├── ubertooth-btle.exe
│   │   ├── ubertooth-util.exe
│   │   ├── ubertooth-scan.exe
│   │   ├── ubertooth-rx.exe
│   │   ├── ubertooth-follow.exe
│   │   ├── ubertooth-tx.exe
│   │   ├── ubertooth-afh.exe
│   │   ├── ubertooth-dump.exe
│   │   ├── ubertooth-specan.exe
│   │   ├── ubertooth-dfu.exe
│   │   ├── libbtbb.dll
│   │   ├── libubertooth.dll
│   │   └── libusb-1.0.dll
│   └── tauri.conf.json
├── src/                       ← React frontend (sau HTML/JS simplu)
│   ├── App.tsx
│   ├── components/
│   └── hooks/
└── package.json
```

**Flux de date**:
```
React UI → api.invoke("run_command") → Rust handler
  → discovery.rs (PowerShell PnP)
  → runner.rs (spawn ubertooth-btle.exe din resources/)
  → stream stdout lines → Tauri event "command-output"
  → React UI updates live
```

---

## Decizii de Design

### De ce Rust (nu Node.js reimplementat)?
- Elimină Node.js ca dependency complet — un singur binar Rust
- Tauri este oricum Rust; logica din Node CLI se mapează natural în Rust
- Performanță mai bună pentru I/O streaming de pachete BLE
- `.exe` final mai mic (nu include Node runtime de ~45MB)

### De ce păstrăm ubertooth-*.exe oficiale?
- Acele binare sunt din **greatscottgadgets/ubertooth** (GPLv2), NU din ubertooth-windows-host
- Le putem include direct (cu citare sursei în bibliografie)
- Reimplementarea driverului USB la nivel de kernel e out-of-scope pentru teză

### De ce React frontend?
- Corespunde stack-ului existent din teză (Python + React + FastAPI)
- shadcn/ui + Tremor disponibile

---

## Pași de Implementare

### Faza 0: Audit & Setup (0.5 zile)
- [ ] **0.1** Listează toate comenzile folosite efectiv din ubertooth-windows-host (ex: `btle`, `scan`, `util`) — exclude ce nu e folosit
- [ ] **0.2** Documentează protocoalele de siguranță din ubertooth-windows-host (duty cycle, antenna check) — înțelege logica, NU copia codul
- [ ] **0.3** Creează proiect Tauri 2.x fresh: `npm create tauri-app@latest ubertooth-standalone`
- [ ] **0.4** Copiază binarele din `ubertooth-windows-host/build/windows-flash-tools/` în `src-tauri/resources/`

**Verificare 0**: `cargo tauri dev` pornește aplicația goală fără erori.

---

### Faza 1: discovery.rs — Detectare Hardware USB (1 zi)
- [ ] **1.1** Implementează `discover_devices()` în Rust:
  - Rulează PowerShell cu query WMI `Win32_PnPEntity` (VID: `1D50`, PID: `6002` / DFU: `6003`)
  - Parsează JSON output
  - Returnează `Vec<UbertoothDevice>` cu: name, status, pnpDeviceId, isPresent
- [ ] **1.2** Expune ca Tauri command: `#[tauri::command] fn detect_devices() -> Vec<UbertoothDevice>`
- [ ] **1.3** Test manual: `ubertooth-util -v` cu device conectat → device apare în UI

**Surse de inspirație (de citat)**: greatscottgadgets/ubertooth wiki, WMI/PowerShell MSDN docs  
**Verificare 1**: Device detectat în UI când conectat, mesaj clar când lipsă.

---

### Faza 2: runner.rs — Subprocess Manager (1 zi)
- [ ] **2.1** Implementează `run_ubertooth_tool()`:
  - Rezolvă calea la binar din `resources/` relativ la `.exe`-ul aplicației
  - Spawn subprocess cu `Command::new(binary_path).args(args).stdout(Stdio::piped())`
  - Stream output line-by-line → emit Tauri event `"command-output"` cu payload `{line, is_stderr}`
  - Returnează exit code + posibilitate de `kill()` (pentru stop)
- [ ] **2.2** Job tracking: `HashMap<JobId, Child>` în Tauri state pentru a putea opri procese
- [ ] **2.3** Tauri commands: `start_command(tool, args) -> JobId`, `stop_command(job_id)`

**Verificare 2**: `ubertooth-util -v` pornit din UI → output apare live în frontend.

---

### Faza 3: safety.rs — Protocoale de Siguranță (0.5 zile)
- [ ] **3.1** Antenna guard: comenzile TX (`ubertooth-tx`, `ubertooth-ego`, `ubertooth-ducky`) necesită flag explicit de confirmare în UI (checkbox "Am antena atașată")
- [ ] **3.2** Duty-cycle guard: max 60 secunde de TX per rolling window de 60 minute; UI afișează un timer
- [ ] **3.3** Write guard: `ubertooth-dfu` (flash firmware) necesită confirmare separată în dialog modal

**Verificare 3**: Dacă trimiți comandă TX fără confirmare antenna → eroare UI, subprocess nu pornește.

---

### Faza 4: commands/ — Wrappere per Comandă (1 zi)
Implementează un modul Rust per comandă, cu argumentele validate:

| Modul | Tool | Argumente principale |
|-------|------|---------------------|
| `btle.rs` | `ubertooth-btle` | `-f` (follow), `-c` (channel), `-q` (quiet) |
| `scan.rs` | `ubertooth-scan` | `-t` (timeout) |
| `util.rs` | `ubertooth-util` | `-v` (version), `-U` (channel) |
| `rx.rs` | `ubertooth-rx` | `-c`, `-e` (PCAP export) |
| `follow.rs` | `ubertooth-follow` | LAP address |
| `afh.rs` | `ubertooth-afh` | `-t` (time) |
| `specan.rs` | `ubertooth-specan` | `-l` (low), `-u` (high) |
| `dfu.rs` | `ubertooth-dfu` | `-d` (firmware file) |

- [ ] **4.1** Fiecare modul validează argumentele înainte de spawn (nu lasă shell injection)
- [ ] **4.2** Tauri command unificat: `execute_command(command_name: String, args: Vec<String>) -> JobId`

**Verificare 4**: `ubertooth-btle -f` capturează pachete BLE → linii apar în UI.

---

### Faza 5: React Frontend (1 zi)
- [ ] **5.1** `DeviceStatus` component — apelează `detect_devices()` la mount, polling la 5s
- [ ] **5.2** `CommandPanel` component — dropdown comandă + argumente + buton Run/Stop
- [ ] **5.3** `OutputConsole` component — subscribes la `command-output` Tauri event, afișează live
- [ ] **5.4** Safety dialogs — antenna confirmation + duty-cycle timer vizibil
- [ ] **5.5** Error states — device lipsă, comandă eșuată, duty-cycle depășit

**Verificare 5**: Golden path complet — conectez Ubertooth, pornesc `btle -f`, văd pachete, opresc.

---

### Faza 6: Build & Packaging (0.5 zile)
- [ ] **6.1** Configurare `tauri.conf.json`:
  - `resources: ["resources/*"]` — include toate binarele + DLL-uri
  - `bundle.windows.wix.language: "ro-RO"` (opțional)
  - `identifier: "ro.vlads.ubertooth-standalone"`
- [ ] **6.2** Verifică că DLL-urile sunt lângă exe-ul final în bundle
- [ ] **6.3** Build: `npm run tauri build` → generează `target/release/bundle/msi/*.msi`
- [ ] **6.4** Test pe VM Windows fresh (fără Node, fără Rust, fără drivere pre-instalate)

**Verificare 6**: Instalare MSI pe VM fresh → aplicație pornește, detectează hardware, capturează pachete.

---

## Riscuri și Mitigări

| Risc | Probabilitate | Mitigare |
|------|--------------|----------|
| Binarele ubertooth-*.exe necesită libusb pe care nu îl găsesc | Medie | Testează că `libusb-1.0.dll`, `libbtbb.dll`, `libubertooth.dll` sunt în același folder cu exe-urile; ajustează PATH în Rust runner |
| WinUSB driver lipsă pe mașina țintă | Medie | Adaugă instrucțiuni în UI ("Install WinUSB driver via Zadig") sau bundlează `libwdi` installer separat |
| Anti-plagiat: logică similară cu ubertooth-windows-host | Medie | Documentează în bibliografie că implementarea e inspirată din ubertooth-windows-host (citat) dar rescrisă în Rust |
| Tauri 2.x breaking changes față de 1.x | Mică | Folosește `cargo tauri info` pentru a verifica versiunile |

---

## Verificare Finală (Definition of Done)

- [ ] `grep -r "ubertooth-windows-host" ubertooth-standalone/` → 0 rezultate
- [ ] MSI instalat pe Windows fresh (VM fără Node.js) → app pornește
- [ ] Device detection funcționează (Ubertooth conectat)
- [ ] `ubertooth-btle -f` capturează pachete live în UI
- [ ] TX commands blochează fără confirmare antenna
- [ ] Duty-cycle timer funcționează
- [ ] `ubertooth-dfu` necesită confirmare modal
- [ ] Bibliografie conține: greatscottgadgets/ubertooth, Tauri docs, WMI MSDN, libusb, libbtbb

---

## Timeline Estimat

| Faza | Efort |
|------|-------|
| Faza 0 — Audit & Setup | 0.5 zile |
| Faza 1 — USB Discovery | 1 zi |
| Faza 2 — Subprocess Runner | 1 zi |
| Faza 3 — Safety Guards | 0.5 zile |
| Faza 4 — Command Wrappers | 1 zi |
| Faza 5 — React Frontend | 1 zi |
| Faza 6 — Build & Packaging | 0.5 zile |
| **Total** | **~5.5 zile** |

---

## Note Antiplagiat

Logica de PnP discovery (PowerShell WMI query cu `Win32_PnPEntity`, filtrare VID/PID `1D50:6002`) e **inspirată** din ubertooth-windows-host (MIT License). Reimplementarea e în Rust, nu JavaScript. Sursa trebuie citată în bibliografie:

> *ubertooth-windows-host*, open-source Windows host tools for Ubertooth One, https://github.com/[autor]/ubertooth-windows-host

Binarele `ubertooth-*.exe` și DLL-urile provin din proiectul oficial **greatscottgadgets/ubertooth** (GPLv2) și trebuie citate separat.
