# Testing Plan: Ubertooth Standalone App

**Date**: 2026-04-14  
**Hardware required**: Ubertooth One connected via USB  
**Prerequisites**: WinUSB driver installed via Zadig, app running in dev mode  

**How to start the app**:
```bash
cd ubertooth-standalone
CARGO_TARGET_DIR=../ubertooth-windows-host/apps/desktop/src-tauri/target npm run tauri:dev
```

---

## Automated Results (completed by Claude)

### Unit Tests — 21/21 PASS ✅
```
cargo test — finished in 2.61s
safety::tests::tx_tools_recognised                    ok
safety::tests::rx_tools_not_tx                        ok
safety::tests::antenna_required_for_tx_without_confirmation  ok
safety::tests::antenna_ok_for_tx_with_confirmation    ok
safety::tests::antenna_not_required_for_rx_tools      ok
safety::tests::dfu_blocked_without_confirmation       ok
safety::tests::dfu_allowed_with_confirmation          ok
safety::tests::non_dfu_tools_not_blocked              ok
safety::tests::fresh_tracker_is_zero                  ok
safety::tests::records_sessions_and_accumulates       ok
safety::tests::duty_cycle_blocked_at_limit            ok
safety::tests::duty_cycle_blocked_over_limit          ok
safety::tests::duty_cycle_ok_just_under_limit         ok
commands::tests::unknown_command_rejected             ok
commands::tests::valid_flag_accepted                  ok
commands::tests::invalid_flag_rejected                ok
commands::tests::value_after_flag_not_treated_as_flag ok
commands::tests::multiple_valid_flags_accepted        ok
commands::tests::specan_range_flags_accepted          ok
commands::tests::empty_args_always_valid              ok
commands::tests::all_eight_commands_known             ok
```

---

## Section 1 — Startup & Device Detection

### T-01: App launches without errors ✅ PASS (automated)
- App compiled (7.75s), `ubertooth-standalone.exe` started, no panics in terminal
- Vite dev server started at http://127.0.0.1:1421

### T-02: Device detected on startup ⬜ NEEDS GEMINI
- **Action**: Ubertooth One is connected before app starts
- **Expected**: Device card shows green dot + device name + PnP device ID
- **Pass if**: `is_present: true` — green dot visible

### T-03: Device absent shows correct state ⬜ NEEDS GEMINI
- **Action**: Unplug Ubertooth, wait up to 10 seconds
- **Expected**: Device card switches to red dot + "No device found"
- **Pass if**: State updates within one 5-second poll cycle

### T-04: Device reconnect detected ⬜ NEEDS GEMINI
- **Action**: Replug Ubertooth after T-03
- **Expected**: Device card returns to green dot within 10 seconds
- **Pass if**: Green dot returns without restarting the app

---

## Section 2 — Command Panel & Output

### T-05: Command dropdown populates ⬜ NEEDS GEMINI
- **Action**: Open the dropdown in the Command card
- **Expected**: Shows 8 entries: ubertooth-btle, ubertooth-scan, ubertooth-util, ubertooth-rx, ubertooth-follow, ubertooth-afh, ubertooth-specan, ubertooth-dfu
- **Pass if**: All 8 appear with descriptions

### T-06: ubertooth-util -v shows firmware version ⬜ NEEDS GEMINI
- **Action**: Select `ubertooth-util`, type `-v` in args, click Run
- **Expected**: Output console shows firmware version string (e.g. `ubertooth-util 2020-12-R1`)
- **Pass if**: Version line appears in console, status tag shows "done" after exit

### T-07: Live output streaming ⬜ NEEDS GEMINI
- **Action**: Select `ubertooth-btle`, type `-f` in args, click Run
- **Expected**: BLE advertisement lines appear progressively (not all at once at end)
- **Pass if**: Lines appear one-by-one as they arrive

### T-08: Stop button kills the process ⬜ NEEDS GEMINI
- **Action**: Start `ubertooth-btle -f`, wait 2 seconds, click Stop
- **Expected**: Output stops, console prints "■ Stopped.", status tag returns to idle
- **Pass if**: No further lines appear after Stop

### T-09: Run button disabled while running ⬜ NEEDS GEMINI
- **Action**: Start any command, observe Run button
- **Expected**: Run button is greyed out
- **Pass if**: Run button has `disabled` attribute

### T-10: Missing binary shows clear error ⬜ NEEDS GEMINI (optional)
- **Action**: Temporarily rename `ubertooth-util.exe` in resources/, try to run it
- **Expected**: Error banner: "Binary 'ubertooth-util.exe' not found in resources/"
- **Pass if**: Error banner visible, no crash

---

## Section 3 — Safety Guards

### T-11: Antenna checkbox hidden for safe commands ⬜ NEEDS GEMINI
- **Action**: Select `ubertooth-util` in dropdown
- **Expected**: Antenna checkbox row NOT visible
- **Pass if**: `#antenna-row` has `display: none`

### T-12: Antenna guard blocks TX without confirmation ✅ PASS (unit test)
- Covered by `safety::tests::antenna_required_for_tx_without_confirmation`
- Error message verified: contains "requires an antenna"

### T-13: TX with antenna confirmed passes ✅ PASS (unit test)
- Covered by `safety::tests::antenna_ok_for_tx_with_confirmation`

### T-14: DFU modal appears before ubertooth-dfu ⬜ NEEDS GEMINI
- **Action**: Select `ubertooth-dfu`, click Run
- **Expected**: Modal with "⚠ Firmware Flash Warning" appears
- **Pass if**: Modal visible, background dimmed

### T-15: DFU cancel aborts command ⬜ NEEDS GEMINI
- **Action**: T-14 → click Cancel
- **Expected**: Modal closes, error banner "DFU cancelled.", no subprocess spawned
- **Pass if**: Console shows no "▶ ubertooth-dfu" line

### T-16: DFU confirm proceeds ⬜ NEEDS GEMINI
- **Action**: T-14 → click "Yes, flash firmware"
- **Expected**: Modal closes, command attempts to run
- **Pass if**: No DFU-cancelled error, "▶ ubertooth-dfu" appears in console

### T-17: Duty-cycle baseline is 0 ✅ PASS (unit test)
- Covered by `safety::tests::fresh_tracker_is_zero`
- Covered by `safety::tests::duty_cycle_blocked_at_limit`
- Covered by `safety::tests::records_sessions_and_accumulates`

---

## Section 4 — Argument Validation

### T-18: Invalid flag rejected ✅ PASS (unit test)
- Covered by `commands::tests::invalid_flag_rejected`
- Error message verified: contains the bad flag name

### T-19: Valid flag accepted ✅ PASS (unit test)
- Covered by `commands::tests::valid_flag_accepted`

### T-20: Multiple valid flags accepted ✅ PASS (unit test)
- Covered by `commands::tests::multiple_valid_flags_accepted`

### T-21: Value after flag not treated as flag ✅ PASS (unit test)
- Covered by `commands::tests::value_after_flag_not_treated_as_flag`
- "-c 37": "37" is not rejected

---

## Section 5 — Console & UX

### T-22: Clear button empties console ⬜ NEEDS GEMINI
- **Action**: Run a command, wait for output, click Clear
- **Expected**: Console area is empty
- **Pass if**: No lines remain in `#console`

### T-23: Error state clears on next Run ⬜ NEEDS GEMINI
- **Action**: Trigger invalid arg error, fix args, click Run
- **Expected**: Error banner disappears when Run is clicked
- **Pass if**: Error banner `display: none` on next run

### T-24: command-done updates status tag ⬜ NEEDS GEMINI
- **Action**: Run `ubertooth-util -v`, wait for exit
- **Expected**: Status tag changes "running" → "idle"
- **Pass if**: Tag reads "idle" after process exits

---

## Section 6 — Packaging

### T-25: tauri build produces MSI ⬜ NEEDS GEMINI (optional)
- **Action**:
  ```bash
  CARGO_TARGET_DIR=../ubertooth-windows-host/apps/desktop/src-tauri/target npm run tauri:build
  ```
- **Expected**: `src-tauri/target/release/bundle/msi/*.msi` exists, size > 1 MB
- **Pass if**: MSI file present

### T-26: No ubertooth-windows-host references ✅ PASS (automated)
- `grep -r "ubertooth-windows-host" ubertooth-standalone/` → exit 1 (zero matches)

---

## Summary

| Status | Count | Tests |
|--------|-------|-------|
| ✅ PASS (automated) | 10 | T-01, T-12, T-13, T-17, T-18, T-19, T-20, T-21, T-26 + 21 unit tests |
| ⬜ NEEDS GEMINI | 16 | T-02–T-11, T-14–T-16, T-22–T-25 |
| ❌ FAIL | 0 | — |

**Minimum pass for thesis demo**: T-02, T-06, T-07, T-08, T-14, T-15 still pending — all require the live GUI window.
