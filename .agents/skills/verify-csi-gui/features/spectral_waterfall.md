# Feature: Spectral Waterfall Matrix

## 1. Matrix Structure
- Horizontal axis: 52 active OFDM subcarriers (HT20 channel, indices -26..-1, 1..26).
- Vertical axis: Time history buffer maintaining the most recent 120 packets.
- Intensity: CSI amplitude ($|H_k| = \sqrt{I_k^2 + Q_k^2}$).

## 2. Palette & Rendering
- Rendered using the perceptual `plasma` colormap (dark purple = 0, orange/yellow = 100+).
- Dynamically scrolls downwards at 30-50 FPS.
- Dead subcarriers (indices 21 to 30) appear as zero-energy bands; active multipath variations display distinct vertical perturbation stripes during human locomotion.
