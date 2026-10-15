# Scene plan (VIDEO)

Audience: total newcomer. Style: YouTube code explainer. EVERY code scene follows this pattern:

- Code card on the LEFT (x 60, about 1100 px wide, font 36-40); if a line is longer than ~60 characters, put the card on top at full width (font 30-34) and the callouts + picture below it. Exactly the lines listed below, verbatim, real indentation.
- Glow ONE line at a time, cued on the phrase that talks about it (`glow: [{line, from, until}]`), moving down the card as the narration moves.
- RIGHT side (x ~1200-1860): a plain-words callout for the glowing line (K.lines / K.text, 44 px+, max ~10 words, e.g. "`iq` = the 128 reading bytes, as numbers"), each replaced by the next with `until`. Write variable names with `K.mono`.
- Under or beside the callouts: a small LIVE picture that changes as the line runs (K.custom, drawn from t, or kit charts): see "picture" per scene. This is the "watch it happen" part; it must change on screen, not sit still.
- Nothing on screen holds more than ~5 s without something changing. Never open on an empty stage: the code card appears on the scene's first sentence.
- No zooms (no `inside`). Scenes run back-to-back with almost no gap, so draw from the first sentence.
- Numbers on screen only those spoken in the scene (listed below). No other values.

Module split: <builder A = keys …> · <builder B = keys …>. Overlay modules (intro, a<N>, outro) are placeholders: builders never touch them.

---

## EXAMPLE (from the Licenta video) c2-parse: open the envelope
Code `src/csi/packets.py:42-47`:
```python
def _parse(raw):
    _, node_id, rssi_dbm, timestamp_us, seq = struct.unpack(HEADER_FORMAT, raw[:HEADER_BYTES])
    iq = np.frombuffer(raw[HEADER_BYTES:PACKET_BYTES], dtype=np.int8)
    csi = iq[0::2] + 1j * iq[1::2]
    active = np.concatenate([csi[part] for part in ACTIVE_SUBCARRIERS])
    return Packet(node_id, rssi_dbm, timestamp_us, seq, active)
```
(font 32-34 if needed; line 1 is long.)
Glow: line 1 on "reads the address"; line 2 on "128 reading bytes"; line 3 on "paired up"; line 4 on "52 useful stations".
Callouts: `node_id` = which board · `rssi_dbm` = how strong · `timestamp_us` = when · `seq` = a counter; then `iq` = 128 small whole numbers; then `csi` = pairs: first + second × j; then `active` = keep 52 stations.
Picture: a row of 138 small tiles (10 address tiles in violet/muted, 128 reading tiles), the 10 lighting on line 1, the 128 on line 2; on line 3 the 128 tiles merge pairwise into 64; on line 4, 12 of the 64 fade, 52 remain (the count "52" appears on "52 useful stations").

