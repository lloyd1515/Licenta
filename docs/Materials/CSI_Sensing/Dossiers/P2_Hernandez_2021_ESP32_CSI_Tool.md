# [P2] Wi-Fi Sensing on the Edge: Who and Where are You?

- **Autori:** Steven M. Hernandez, Eyuphan Bulut
- **Publicație:** *IEEE Internet of Things Journal (IoT-J)*, Vol. 9, Nr. 10, pp. 7000–7014, Mai 2021
- **DOI:** [10.1109/JIOT.2021.3116035](https://doi.org/10.1109/JIOT.2021.3116035)
- **Preprint arXiv:** [arXiv:2109.11718](https://arxiv.org/abs/2109.11718)
- **Fișier PDF Local:** [`docs/Materials/CSI_Sensing/PDFs/P2_Hernandez_2021_WiFi_Sensing_Edge.pdf`](file:///home/vlads4r4/dev/Licenta/docs/Materials/CSI_Sensing/PDFs/P2_Hernandez_2021_WiFi_Sensing_Edge.pdf)
- **Cod BibTeX:** `@article{hernandez2021wifi, ...}` în `references_csi.bib`

---

## 1. Contribuție & Specificație Hardware ESP32

Articolul introduce primul cadru sistematic de extragere CSI pe microcontrollere comerciale cu cost redus (**ESP32**, nucleu Xtensa LX6 dual-core @ 240 MHz):

1. **Formatul Pachetului CSI ESP32 (HT20 802.11n):**
   - Pachete brute de 138 octeți: 10 octeți header de control + 128 octeți date I/Q (64 purtătoare $\times$ 2 octeți signed integer).
   - Dintre cele 64 de purtătoare, **52 sunt active** (indicii $[-26 \dots -1]$ și $[1 \dots 26]$).
   - Purtătoarea centrală DC (index 0) și cele 11 purtătoare marginale de gardă sunt nule sau nesigure.

2. **Cerința de Cadență (Sampling Rate $f_s$):**
   - Articolul specifică o rată de eșantionare recomandată de **$f_s \ge 100\text{ Hz}$** pentru a capta fidel dinamica rapidă a mișcării umane fără distorsiuni sau aliere.

---

## 2. Limita Hardware Identificată în Proiect: UART vs. UDP

- **Limitare actuală pe UART:**
  - Plăcile transmit cadre seriale la 921600 baud.
  - În hardware-ul testat, rata efectivă obținută este de **$33.5 - 52.5\text{ Hz}$** (a se vedea raportul JSON `audit_p2_esp32_subcarriers`).
  - La $f_s \approx 33.5\text{ Hz}$, frecvența maximă Nyquist observabilă fără aliere este:
    $$f_{\text{Nyquist}} = \frac{f_s}{2} \approx 16.75\text{ Hz}$$
- **Soluția UDP:**
  - În loc să se scrie pe UART binar linie cu linie, firmware-ul ESP32 configurează un socket UDP broadcast/unicast prin interfața Wi-Fi nativă (sau DMA SPI).
  - Permite transmiterea directă a pachetelor CSI la debite de peste **150–200 Hz**, depășind cu mult pragul de 100 Hz impus de Hernandez & Bulut.
