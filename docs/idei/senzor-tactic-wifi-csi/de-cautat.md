# De căutat data viitoare

Aceste întrebări au rămas fără răspuns pe 2026-11-12. Ordinea este prioritatea pentru concept.

## Prioritate mare: baza științifică a conceptului

| # | Întrebare | Unde să cauți | Cuvinte de căutare |
|---|---|---|---|
| 1 | Există o lucrare cu ESP32 care măsoară CSI pasiv, din traficul unui AP străin, prin perete? | IEEE Xplore, arXiv, Google Scholar | `ESP32 passive CSI third-party access point through-wall`, `opportunistic CSI sensing commodity` |
| 2 | Lucrările UCL despre Wi-Fi pasiv după 2012: acuratețe, distanță, tip de perete | UCL Discovery, IEEE Xplore | `Chetty passive WiFi radar`, `Li Piechocki Woodbridge beacon through-the-wall` |
| 3 | Lucrarea Chen et al. (UCL): „în picioare”, „pe scaun”, „cădere” din Wi-Fi pasiv | UCL Discovery | `Chen Chetty passive WiFi fall detection deep learning` |
| 4 | Cât atenuează diferiți pereți semnalul de 2,4 GHz (cărămidă, BCA, beton armat, gips-carton)? | ITU-R P.2040, lucrări de propagare | `2.4 GHz wall attenuation brick concrete ITU-R P.2040` |
| 5 | Ce cadre OFDM trimite un router obișnuit fără clienți activi? Câte cadre CSI pe secundă rămân? | test pe placă, documentația ESP-IDF | `ESP32 promiscuous CSI frame types rate idle AP` |
| 6 | Sursă mai bună pentru „unități găsite după semnalele radio” în Ucraina | rapoarte RUSI, ISW, presă de apărare | `Ukraine units located by WiFi Bluetooth emissions EW direction finding` |

## Prioritate medie: kitul mobil

| # | Întrebare | Unde să cauți | Cuvinte de căutare |
|---|---|---|---|
| 7 | Lucrare cu CSI pe un receptor în mișcare, compensat cu IMU | IEEE Xplore, arXiv | `CSI device motion compensation IMU human sensing` |
| 8 | Disponibilitatea kiturilor UWB ieftine în 2026 (Novelda X4, Infineon, Qorvo DW3000 ca radar) | site-urile firmelor | `Novelda X4 dev kit 2026`, `DW3000 radar mode breathing`, `Infineon UWB radar kit` |
| 9 | Teste prin perete cu cipuri UWB ieftine | arXiv | `802.15.4z UWB radar through-wall breathing` |
| 10 | Calitatea CSI pe ESP32-WROOM-32U cu antenă direcțională externă | forumuri ESP32, GitHub `esp-csi` | `ESP32-WROOM-32U external antenna CSI` |
| 11 | Consumul ESP32 în mod promiscuu cu CSI activ (pentru autonomia bateriei) | măsurare proprie, forumuri | `ESP32 promiscuous mode current consumption mA` |
| 12 | Timpul minim de măsurare pentru respirație cu CSI (sub 10 s?) | lucrări de respirație | `WiFi CSI respiration rate short window` |

## Prioritate medie: ATAK și integrarea

| # | Întrebare | Unde să cauți | Cuvinte de căutare |
|---|---|---|---|
| 13 | Tipul CoT corect pentru o detecție de senzor (`a-u-G` sau ramura `b-d`) | documentația MIL-STD-2525, FreeTAKServer | `CoT type sensor detection b-d`, `MIL-STD-2525 CoT unknown ground` |
| 14 | ATAK-CIV pe Android: primește CoT prin USB sau doar prin rețea? | documentația TAK, forumuri | `ATAK CoT input USB serial plugin`, `ATAK-CIV network input UDP` |
| 15 | Plugin ATAK propriu comparat cu PyTAK pe telefon (Termux) | GitHub, tak.gov | `ATAK plugin SDK sensor`, `PyTAK Android Termux` |

## Prioritate mică: piața și finanțarea

| # | Întrebare | Unde să cauți | Cuvinte de căutare |
|---|---|---|---|
| 16 | Ce fac UTI Grup, Teamnet și Electromagnetica în apărare azi? | site-urile firmelor, presă românească | `UTI Grup apărare`, `Teamnet C4I`, `Electromagnetica militar` |
| 17 | Profilul exact al Artemis Research & Innovation | site-ul firmei, EDF | `Artemis Research Innovation EDF` |
| 18 | Ce fac Delphys Dynamics, Headlight Solutions, QUADYX și Crystal Matrix Design (Techcelerator Vanguard)? | site-urile firmelor, LinkedIn | numele firmelor |
| 19 | Prețul și starea Lumineye în 2026 | site-ul Lumineye, achiziții publice SUA | `Lumineye 2026`, `Lumineye contract` |
| 20 | Cum funcționează radarul distribuit CHAOS Industries (Vanquish) | presă de apărare | `CHAOS Industries Vanquish coherent radar` |
| 21 | Rezultatele finalei DARPA Triage Challenge (5–14 noiembrie 2026) | darpa.mil | `DARPA Triage Challenge final results 2026` |
| 22 | Textul complet al provocărilor DIANA 2027 și data apelului pentru 2028 | diana.nato.int, IUK Business Connect | `DIANA 2028 challenge call` |
| 23 | Textul complet Dr. Defender (IEEE TIFS 2024) | IEEE Xplore | `Dr. Defender autopilot drones CSI` |
| 24 | Firme din România care angajează pentru RF, embedded și fuziune de senzori | LinkedIn, ejobs, site-urile firmelor din surse.md | `RF engineer defence Romania`, `embedded drone Cluj` |

## Legal și etică

| # | Întrebare | Unde să cauți |
|---|---|---|
| 25 | Este legală în România recepția pasivă a cadrelor Wi-Fi străine pentru CSI, fără decodarea conținutului? | ANCOM, Legea 506/2004, GDPR, coordonatorul |
| 26 | Ce acord trebuie să aibă voluntarii din teste? | regulile UTCN pentru experimente cu oameni, coordonatorul |

## Teste pe placă (fără web)

Aceste teste nu cer cumpărături:

1. Pune o placă în mod promiscuu lângă routerul de acasă. Filtrează după MAC-ul routerului. Numără CSI/s cu un telefon care face streaming și fără trafic.
2. Pune placa după un perete. Măsoară varianța CSI cu camera goală și cu un om care merge.
3. Măsoară curentul plăcii în mod promiscuu cu CSI activ.
