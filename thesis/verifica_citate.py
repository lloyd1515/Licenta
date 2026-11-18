# Verifică dacă fiecare fragment citat în capitolul 4 apare în PDF-ul local al sursei.
# Rulare: python3 thesis/verifica_citate.py
import re, subprocess, sys, pathlib
SRC = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else pathlib.Path(__file__).resolve().parent.parent / "docs/Materials/CSI_Sensing/sources-2026-10-21")
def text(rel):
    files = sorted((SRC / rel).glob('*.pdf')) if (SRC / rel).is_dir() else [SRC / rel]
    t = " ".join(subprocess.run(['pdftotext', str(f), '-'], capture_output=True, text=True).stdout for f in files)
    t = re.sub(r'-\s*\n\s*', '', t)          # hyphenation at line end
    t = re.sub(r'\s+', ' ', t).replace('–', '-').replace('−', '-')
    return t.lower()
checks = {
 'Tse_Viswanath_2005_Fundamentals_Wireless_Communication': [
   'the overall channel response can still vary with frequency due to the fact that different paths have different delays',
   'is actually done at the baseband', 'in-phase component i', 'quadrature component q',
   'when the path length changes by a quarter wavelength', 'delay spread and coherence bandwidth',
   'known sequence (called a pilot or training sequence)', 'uniformly separated by w/nc',
   'orthogonal frequency division multiplexing', 'coherence bandwidth',
   'any waveform band-limited to w/2 can be expanded', 'taken uniformly at integer multiples of 1/w'],
 'IEEE_1999_Std_802.11a_OFDM_PHY_5GHz.pdf': [
   'used for channel estimation and fine frequency acquisition in the receiver',
   'used for agc convergence, diversity selection, timing acquisition, and coarse frequency acquisition',
   '0.3125 mhz (=20 mhz/64)', 'a long ofdm training symbol consists of 53 subcarriers (including a zero value at dc)',
   'two periods of the long sequence are transmitted for improved channel estimation accuracy',
   'four subcarriers are inserted as pilots into positions -21, -7, 7, and 21',
   'associated with center frequency, is omitted and filled with zero value', 'ofdm training structure',
   'the coefficients 1 to 26 are mapped to the same numbered ifft inputs',
   'while the coefficients -26 to -1 are copied into ifft inputs',
   'the rest of the inputs, 27 to 37 and the 0 (dc) input, are set to zero',
   'capabilities of 6, 9, 12, 18, 24, 36, 48, and 54 mbit/s'],
 'Halperin_2011_Tool_Release_80211n_CSI.pdf': [
   'measures the channel state for each received packet during the packet preamble',
   'used in the equalizer to compensate for channel effects before demodulation',
   '56 subcarriers of a 20 mhz channel', 'differ in rssi by up to 13 db',
   'for each pair of transmit and receive antennas', 'frequency-selective fading'],
 'Wang_2015_Understanding_Modeling_WiFi_HAR_CARM.pdf': [
   'when the path length changes by one wavelength, the receiver experiences a phase shift of 2π',
   'wireless signals travel at the speed of light', '= 80 khz', 'measurement error as large as 0.5π',
   'phase changes caused by human reflection are much smaller than 0.5π',
   'static component hs (f ) is a constant vector',
   'the phase sanitization process also removes the phase shifts caused by body movements'],
 'Zeng_2019_FarSense_Respiration_CSI_Ratio.pdf': [
   'the paths can be grouped into static path and dynamic path', 'rotates 2π clockwise',
   'sampling frequency offset (sfo), carrier frequency offset (cfo) and packet detection delay (pdd)',
   'changes of a few centimeters in path length have very little effect'],
 'Wang_Mao_2020_PhaseBeat_Vital_Signs.pdf': [
   'the first approach is to make a linear transform of the phase values measured',
   'the other is to exploit the phase difference between two antennas',
   'the average phase value that they produce is always near zero',
   'thus, the true phase ∠csii cannot be obtained from the measured phase value',
   'packet boundary detection (pbd), the sampling frequency offset (sfo), and the central frequency offset (cfo)',
   'β is the initial phase offset due to the phase-locked loop (pll)'],
 'Chen_Liu_2018_TR_BREATH_Time_Reversal.pdf': [
   'real-valued agc gain', 'scales the input voltage into the dynamic range of the analog-to-digital converter',
   'local oscillators of the wifi transmitter and receiver', 'packet loss is unavoidable'],
 'Chen_Liu_2016_WiFi_TRIPS_Time_Reversal.pdf': [
   'csis are estimated from the long training preambles (ltp) on subcarrier level in frequency domain'],
 'Zhang_Wang_2015_Anti_Fall_CSI_Commodity_WiFi.pdf': [
   'additional signal paths are introduced by the scattering of human body',
   'involving both amplitude attenuation and phase shift in the csi streams'],
 'Espressif_ESP-IDF_v5.1.7_WiFi_Driver_2026-11-11.pdf': [
   '52 total, 48 usable', '56 total, 52 usable', 'the first one is imaginary part and the second one is real part',
   'estimated when packets are received from the transmitter', 'legacy long training field (lltf)',
   'space time block code ht-ltf (stbc-ht-ltf)', '0~31, -32~-1',
   'first four bytes of csi data is invalid due to a hardware limitation in esp32',
   'select wi-fi csi in menuconfig', 'set csi receiving callback function', 'configure csi by calling api',
   'enable csi by calling api', 'the total bytes of csi data will be fewer than that in the table',
   'the csi receiving callback function runs from wi-fi task',
   'post necessary data to a queue and handle it from a lower priority task',
   'it is suggested to enable sniffer mode to receive more csi data'],
}
bad = 0
for rel, phrases in checks.items():
    t = text(rel)
    for ph in phrases:
        ok = ph in t
        bad += not ok
        print(('OK   ' if ok else 'LIPSĂ'), rel.split('_20')[0][:28].ljust(28), ph[:90])
print('lipsă:', bad)
