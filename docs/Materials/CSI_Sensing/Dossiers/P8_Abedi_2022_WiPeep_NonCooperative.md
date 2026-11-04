# [P8] Non-Cooperative Wi-Fi Localization (Wi-Peep)

- **Autori:** Ali Abedi, Deepak Vasisht
- **Publicație:** *ACM MobiCom 2022*, pp. 707–720, Oct. 2022
- **DOI:** [10.1145/3495243.3560530](https://doi.org/10.1145/3495243.3560530)
- **Preprint arXiv:** [arXiv:2209.05607](https://arxiv.org/abs/2209.05607)
- **Fișier PDF Local:** lipsă. Fișierul vechi conținea alt articol (eliminat 2026-11-04). Articol înrudit al aceluiași prim autor: [`docs/Materials/CSI_Sensing/sources-2026-10-21/Abedi_2023_WiFi_Physical_Layer_Stays_Awake.pdf`](file:///home/vlads4r4/dev/Licenta/docs/Materials/CSI_Sensing/sources-2026-10-21/Abedi_2023_WiFi_Physical_Layer_Stays_Awake.pdf)
- **Cod BibTeX:** `@inproceedings{abedi2022wipeep, ...}` în `references_csi.bib`

---

## 1. Contribuție & Inovație Tehnică

1. **Localizare Non-Cooperativă pe Timp de Răspuns Hardware (ToF):**
   - Dispozitivele Wi-Fi (inclusiv cele securizate cu WPA2/WPA3 care nu transmit CSI voluntar) răspund automat la pachetele de control 802.11 (de exemplu, cadre ACK / CTS sau probe requests) la nivel hardware în câteva zeci de nanosecunde.
   - Analizând variațiile infime de timp de propagare ToF (Time of Flight), atacatorul sau observatorul poate localiza fizic dispozitivul în interiorul clădirii cu precizie sub-metrică chiar și fără asociere în rețea.

2. **Relevanță pentru Arhitectura de Licență:**
   - Confirmă de ce un nod pasiv (sau un nod sniffer precum Ubertooth / ESP32 promiscuu) poate audita prezența și mișcarea fără a stabili o conexiune client-server autentificată.
