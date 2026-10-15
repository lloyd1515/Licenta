# Scene briefs (what to draw). Times: see cues.json (per scene: dur + sentences [start, end, text]).

Absolute offset of each scene inside this project's index.html: offsets.json (use it for `snapshot` times: absolute = offset + relative).

## intro: cold open (dur 12.0)
Dark room seen from the front: floor line, three small violet boards (rounded rects with a tiny antenna) on the left wall, right wall, back. Faint violet wave arcs pulse between them all the time.
- S0 "Someone just fell in this room.": a simple stick figure (white strokes, SVG) standing mid-room tips over and lies flat on the floor (0.8 s fall, ease in). The arcs between boards wobble hard at the fall moment.
- S1 "No camera saw it.": a camera icon appears top-right, crossed out (red line).
- S2 "Nobody wore a sensor.": a wristband/watch icon next to it, crossed out.
- S3 "The Wi-Fi did.": the wave arcs flash accent blue; label "Wi-Fi" near them.
- S4 "In nine minutes…the line of code that rang this alarm.": a red banner slides down from the top: "FALL DETECTED" (Inter 700, white on #ff8f87-ish red with dark text if contrast needs), then a thin code line fades in under it in mono: `state = FallState.ALARM`.

## a1-care: why care (dur 13.5)
- S0 "Picture an older person who lives alone.": a simple house outline; a figure with a walking stick inside.
- S1 "They fall, and the phone is across the room.": figure falls; a phone icon far to the right, a dashed distance arrow between them, label "out of reach".
- S2 "Cameras feel like spying, and a wristband gets left on the nightstand.": two small cards slide in: camera icon "feels like spying", wristband on a nightstand "left behind" (both muted, with a small amber ✕).
- S3 "can the room itself notice the fall?": everything dims, the house outline glows accent blue, big question text "Can the room notice?".

## a1-pond: ripples in a pond (dur 28.1) — the key analogy, make it beautiful
- S0 "Think of a pond.": top-down pond (dark teal ellipse).
- S1 "Drop a stone…bounce off everything they meet.": a stone drops; concentric ripple rings expand (SVG circles, animated r + opacity), reflecting off a reed (small vertical shape) — show a second ring set starting at the reed.
- S2 "Someone on the far bank can tell a reed is there, just from how the ripples arrive.": an eye icon on the far bank; the arriving ripple pattern drawn as a small wiggly line next to the eye.
- S3 "Radio waves do the same thing in a room.": morph: pond → room rectangle, ripples → wave arcs (violet).
- S4 "Three small boards keep sending Wi-Fi messages to each other": three violet boards in a triangle; small dots (messages) fly along the three edges both ways.
- S5 "a body in the way changes how each wave arrives.": a person walks into the triangle; the dots/arcs near them bend; a small "received" meter next to one board starts wobbling.
- S6 "We never look at the person. We watch the ripples wobble.": person fades to 20% opacity; the meter's wiggly line enlarges.
- S7 "…is called CSI.": term card: "CSI" (accent, mono, 96px) + "= the radio's report of how each wave arrived".

## a1-stations: 52 radio stations (dur 21.6)
- S0 "And Wi-Fi is not one wave.": one fat wave line.
- S1 "It is 52 narrow waves sent side by side, like 52 radio stations.": the wave splits into a row of 52 thin vertical bars (an equalizer look), label "52 stations"; a tiny radio-dial icon.
- S2 "For every message, the board measures how loud each station arrived.": bars take different heights (seeded); a message dot arrives, bars re-settle.
- S3 "So every message gives us 52 volume numbers, and about 33 messages arrive every second.": bars animate (new heights) rapidly; counter "≈ 33 messages / second" ticks; small mono row "52 numbers × 33 per second".
- S4 "Each of those narrow waves is called a subcarrier.": one bar highlights accent; term card "subcarrier = one narrow wave (one station)".

## a1-shape: what a fall looks like (dur 22.8)
- S0 "Now squeeze all those numbers into one wiggly line, and compare three rooms.": 52 bars collapse into one line; three cards side by side appear: "Empty room", "Walking", "A fall".
- S1 "An empty room: calm.": card 1 draws a nearly flat line (left→right draw).
- S2 "Someone walking: busy all the time.": card 2 draws a busy line.
- S3 "A fall: busy, then one sharp jerk, then flat, because the person is lying still.": card 3 draws busy → one tall spike (red) → flat (blue), annotated "jerk" and "still".
- S4 "That shape is everything.": cards 1-2 dim; card 3 scales up to center.
- S5 "The whole program hunts for one sharp jerk, followed by stillness.": labels "1 sharp jerk" + "then stillness" with arrows to spike and flat part.
- S6 "Let's follow one real fall through the code.": a small "→ code" arrow / the line slides right as transition.

## a2-envelope: the letter (dur 16.7)
- S0 "…like a letter in an envelope.": an envelope icon flies in from the left (from a violet board) and lands center.
- S1 "138 bytes in total.": the envelope opens; a row of 138 small tiles spills out (two rows OK), counter "138 bytes".
- S2 "The first 10 are the address…which board sent it, how strong it was, and when.": the first 10 tiles turn violet, label "address (10)"; three tags pop in on their words: "which board", "how strong", "when".
- S3 "The other 128 are the letter itself: the readings.": the other 128 tiles turn accent blue, label "readings (128)".

## a2-arrow: why two numbers (dur 19.4)
- S0 "Why two numbers per reading?": two tiles "30" and "−40" side by side.
- S1 "Draw each pair as an arrow on graph paper.": a grid (graph paper, faint lines) fades in, origin dot.
- S2 "A pair of 30 and minus 40 means: 30 steps right, 40 steps down.": a dashed horizontal segment grows 30 units right (label "30 right"), then a dashed vertical segment 40 units down (label "40 down"), then the arrow from origin to the tip draws (accent).
- S3 "The arrow's length is 50, from the classic three, four, five triangle.": the triangle fills faintly; label "50" on the hypotenuse; small side note "3-4-5 ×10".
- S4 "That length is how loud the station arrived.": the arrow's length morphs into a vertical volume bar of the same length, label "loudness = 50".
- S5 "The direction we simply throw away.": the arrow's angle marker fades and gets a ✕ (muted, not red).

## a2-eq: the equalizer (dur 14.3)
- S0 "think of the equalizer on a music player.": a music-player equalizer with ~7 vertical sliders labelled from "slow" (left) to "fast" (right), and a noisy wiggly line above it.
- S1 "Slide down the very slow drift, like a room warming up.": leftmost sliders slide down; label "slow drift (room warming)"; the line's slow wander flattens.
- S2 "Slide down the very fast hiss from the electronics.": rightmost sliders slide down; label "fast hiss (electronics)"; the line's jitter disappears.
- S3 "Keep only the middle: wobbles about as fast as a human body moves.": middle sliders glow accent, label "body speed"; the line is now smooth with body-scale wobbles; a small walking-figure icon.

## a2-alarm: the careful smoke alarm (dur 16.6)
- S0 "But a jerk alone is not a fall.": a red spike icon with "≠ fall".
- S1 "You might just sit down hard.": a figure dropping onto a chair.
- S2 "So the detector works like a careful smoke alarm with stages.": a smoke alarm icon (round disc), then a horizontal row of five stage lights (circles with labels) appears under it.
- S3-S6 "Calm." / "Something is moving." / "A sudden jerk." / "Then: wait, and watch.": light each stage in turn on its sentence: green-ish "Calm", accent "Moving", amber "Jerk!", cyan "Watch…" (a small hourglass), each previous one dimming.
- S7 "Only if the person stays still does it ring.": the 5th light "ALARM" turns red and pulses; the smoke alarm disc shows ring waves.

## a3-kitchen: kitchen and dining room (dur 17.0)
- S0 "Think of a restaurant.": a restaurant cross-section: kitchen (left, behind a wall) and dining room (right), a hatch in the wall between.
- S1 "The kitchen does the heavy cooking in the back, so the dining room never freezes.": a cook with pans busy in the kitchen (small motion loop); in the dining room a diner, label "never freezes".
- S2 "In the app, the kitchen is a worker called FrameSource. It runs the whole pipeline we just saw,": label kitchen "FrameSource" (mono, accent); inside the kitchen a mini pipeline strip: "packets → clean → motion line → detector".
- S3 "and passes every finished result through a hatch, with a bell, to the window you look at.": a plate slides through the hatch, a bell icon rings (small ring lines), the dining room turns into an app window outline labelled "the window".

## outro: the whole idea (dur 10.0)
- S0 "Ripples, radio stations, letters, a spreadsheet, three clean ups, one steep moment, and a careful alarm.": a left→right row (two rows if needed) of 7 small icons appearing one per word group in time with the sentence: ripples, radio dial, envelope, grid, broom ×3 (or "3 clean-ups"), steep slope, smoke alarm. Each with a 1-2 word label.
- S1 "That is the whole idea.": the row connects with a thin accent line; title "How Wi-Fi notices a fall" fades in above.
