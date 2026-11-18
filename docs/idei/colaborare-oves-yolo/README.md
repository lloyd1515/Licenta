# Colaborare pentru licență: OVES Enterprise și YOLO Machines

Data: 2026-11-13. Stare: research gata, emailuri gata, nimic trimis.

Ambele firme sunt în Cluj-Napoca. Ambele lucrează în apărare, pe drone și pe sisteme anti-dronă.

## 1. Ce face fiecare firmă

### OVES Enterprise

| Ce | Detalii |
|---|---|
| Profil | Firmă de software din Cluj, fondată în 2015, peste 200 de angajați. Birouri în RO, DE, UAE, UK, SUA, NO. CEO: Mihai Filip. |
| Produs central | **Nemesis AI**: navigație fără GPS, pilotaj autonom, urmărire și ghidare terminală. Verifică integritatea semnalelor GNSS de ~200 ori/s (jamming, spoofing, meaconing). Fără GNSS, folosește senzori inerțiali. |
| Alte produse | **Ixxera** (securitate pentru rețele de UAV și IoT), **Hyper Drone** (deminare), **INTERJET** (interceptor cu turbină), **SAHARA** (rachetă de croazieră autonomă). |
| Parteneri | MSI Defense (EAGLS, armata SUA), STARK (VANTA, drone navale, sept. 2026), EDRONE (fabrică de drone la Cluj, ~1.000/lună), Overwatch Aerospace, Kongsberg (potențial). |
| Hardware | Pachet minoritar în MXT Creation (plăci electronice) din 2024. Linie de drone mici din 2024. |
| Bani | Venit ~20 mil. EUR (2024). R&D 3 mil. EUR (2025). Discuții pentru 55 mil. EUR. |
| Contact | Fără email public. Formular: https://ovesenterprise.com/contact. Alternativ: mesaj pe LinkedIn către Mihai Filip. |

### YOLO Machines

| Ce | Detalii |
|---|---|
| Profil | Startup anti-dronă din Cluj, operat de INC3 Ventures SRL. Fondator și CEO: Lorand Minyo. Anul fondării: 2025 (interviu) sau 2026 (site). |
| Sistem | **M0THER** (dronă purtătoare <25 kg, camere vizibil + termic, pasivă), **S0N** (interceptor de unică folosință, mărimea palmei), **BAY** (stație de sol autonomă: încarcă și reîncarcă în <5 min). |
| Doctrină | Pasiv în loc de activ. Distribuit (vot 2-din-3 între carriere, pe un mesh local). Edge, fără cloud ("jamming takes the network first"). Modular. |
| Stadiu | Pre-prototip. Arhitectura e gata. Urmează un bench build de 7 luni (3 carriere, 1 BAY, 6 interceptoare), după runda seed. Lab 2027, teren 2028, serie 2029+. |
| Angajări | "Optics, embedded-systems and machine-learning engineers are hired locally" (în Cluj). |
| Program | Unul din cele 16 startup-uri din Techcelerator Vanguard (iunie–decembrie 2026; NATO DIANA, EIC, EUDIS printre susținători). |
| Contact | hello@yolomachines.com |

## 2. Cu ce poate contribui Vlad

Ce am deja (din acest repo):

- Firmware ESP32 scris de la zero în C (ESP-IDF): 3 noduri, cadre OFDM la 6 Mbps, CSI pe 52 de subpurtătoare, trimis prin UDP la PC.
- Interfață live în Python (`src/csi_ui.py`): amplitudine pe subpurtătoare, se vede mișcarea unui om.
- Driverul Wi-Fi închis al ESP32 urmărit până la regiștri (`nm`, `objdump` pe `libnet80211.a`, `libpp.a`, `libphy.a`).
- Ubertooth pentru Bluetooth.
- Direcția următoare: senzor pasiv (nu emite nimic), starea camerei, ieșire CoT spre ATAK. Vezi [../senzor-tactic-wifi-csi/](../senzor-tactic-wifi-csi/).

| Nevoia firmei | Ce pot face eu | Potrivire |
|---|---|---|
| OVES: Nemesis verifică dacă semnalul GNSS e de încredere | Detector de bruiaj și de cadre falsificate pe legăturile de 2,4 GHz, din CSI, RSSI și `noise_floor` | Mare |
| OVES: Ixxera, securitatea rețelelor UAV și IoT | Detecție de anomalii la nivel fizic pe Wi-Fi și BLE (ESP32 + Ubertooth) | Mare |
| OVES: fuziune de senzori în Nemesis | Senzor pasiv ieftin care trimite detecții (prezență, mișcare) spre Nemesis sau ATAK | Medie |
| OVES: fabrica EDRONE din Cluj | Firmware și bancuri de test pe microcontrolere | Medie |
| YOLO: "passive over active" | Senzorul meu pasiv urmează exact acest principiu | Mare |
| YOLO: mesh local + vot 2-din-3 | Banc ESP32 care emulează mesh-ul și măsoară latența votului și pierderile | Mare |
| YOLO: "jamming takes the network first" | Detecția locală a degradării legăturii radio (CSI, RSSI, zgomot) | Mare |
| YOLO: angajează embedded în Cluj | Profil exact: embedded + RF + edge | Mare |

Ce NU propun (nu se potrivește sau e ilegal):

- Teste de bruiaj reale. Bruiajul fără autorizație ANCOM este ilegal. Propun doar detecția.
- Ghidarea interceptoarelor sau a armelor. Nu e domeniul meu și nu intră într-o licență publică.
- Detecția pasivă a dronelor FPV cu ESP32. Legăturile ELRS (LoRa 2,4 GHz) și video 5,8 GHz nu sunt cadre Wi-Fi. ESP32 clasic nu le decodează. Ideea rămâne o întrebare deschisă, nu o promisiune.

## 3. Înainte de trimitere

1. Întreabă îndrumătorul dacă acceptă un partener industrial. Dacă da, pune-l în CC.
2. Completează câmpurile `[...]` din emailuri.
3. Fă un GIF sau un video de 30 s cu `csi_ui.py` când cineva trece între noduri. Repo-ul GitHub este privat, deci nu ai alt link de demo.
4. Trimite de pe adresa de student UTCN.
5. Trimite un singur follow-up după 5–7 zile lucrătoare.

CAUTION: Stabilește de la început că licența rămâne publică și neclasificată. OVES lucrează cu informații clasificate, iar o licență nu poate conține astfel de date.

## 4. Email OVES Enterprise

Canal: formularul https://ovesenterprise.com/contact și mesaj LinkedIn către Mihai Filip.

Versiunea 2 (2026-11-13): simplă, sinceră, fără diacritice, fără promisiuni.

```text
Subiect: Student UTCN - licenta cu senzori Wi-Fi pe ESP32

Buna ziua,

Ma numesc Vlad Sarandan si sunt student in anul 4 la UTCN. Pentru licenta lucrez cu placi ESP32 si Wi-Fi CSI. Pana acum am facut un prototip care detecteaza caderea unei persoane dupa cum se schimba semnalul Wi-Fi intre placi. E un prototip simplu, inca lucrez la el.

Mai departe as vrea sa fac un senzor care nu emite nimic, doar asculta Wi-Fi-ul care exista deja intr-o cladire si spune daca e cineva in camera. Dar sunt deschis si la alte idei.

Am citit despre Nemesis AI si despre fabrica de drone din Cluj si mi-ar placea mult sa lucrez la licenta cu cineva din domeniul asta. As vrea sa va intreb daca ar avea sens o colaborare, chiar si doar cateva sfaturi sau o problema reala la care sa lucrez. Si daca pe viitor aveti loc de internship as fi interesat.

Va multumesc pentru timp,
Vlad Sarandan
```

## 5. Email YOLO Machines

Canal: hello@yolomachines.com și mesaj LinkedIn către Lorand Minyo.

Versiunea 2 (2026-11-13): simplă, sinceră, fără diacritice, fără promisiuni.

```text
Subiect: Student UTCN - licenta cu senzori Wi-Fi pe ESP32

Buna ziua,

Ma numesc Vlad Sarandan si sunt student in anul 4 la UTCN. Pentru licenta lucrez cu placi ESP32 si Wi-Fi CSI. Pana acum am facut un prototip care detecteaza caderea unei persoane dupa cum se schimba semnalul Wi-Fi intre placi. E un prototip simplu, inca lucrez la el.

Am vazut pe site ca sistemul vostru e pasiv si decide local, fara cloud. In directia asta vreau sa merg si eu: un senzor care nu emite nimic, doar asculta Wi-Fi-ul care exista deja si spune daca e cineva intr-o camera. Dar sunt deschis si la alte idei.

As vrea sa va intreb daca ar avea sens o colaborare pe licenta, chiar si doar cateva sfaturi sau o problema mica din proiectul vostru la care sa lucrez. Si daca pe viitor cautati oameni pe embedded as fi interesat.

Va multumesc,
Vlad Sarandan
```

Notă: site-ul YOLO este doar în engleză. Dacă vrei, trimite emailul în engleză.

## 6. Toate linkurile

### OVES Enterprise – surse oficiale

- https://ovesenterprise.com/
- https://ovesenterprise.com/SpaceDefence
- https://ovesenterprise.com/Innovation (Nemesis AI, Ixxera, Hyper Drone)
- https://ovesenterprise.com/SoftwareServices
- https://ovesenterprise.com/CyberSecurity
- https://ovesenterprise.com/contact
- https://x.com/OvesEnterprise

### OVES – Nemesis AI, navigație fără GPS

- https://startupcafe.ro/o-companie-romaneasca-are-o-solutie-pentru-dronele-militare-ramase-fara-comunicatii-prin-satelit-precum-in-incidentul-starlink-din-ucraina-cum-functioneaza-tehnologia-dezvoltata-la-cluj-109222

### OVES – fabrica de drone cu EDRONE (Cluj)

- https://startupcafe.ro/companie-din-ucraina-deschide-o-fabrica-de-drone-militare-la-cluj-interceptoarele-testate-pe-front-vor-integra-tehnologia-nemesis-ai-a-companiei-romanesti-oves-103994
- https://start-up.ro/oves-enterprise-si-edrone-vor-produce-drone-militare-la-cluj-capacitatea-initiala-1-000-de-unitati-lunar
- https://www.digi24.ro/stiri/romania-si-ucraina-incep-productia-comuna-de-drone-militare-la-cluj-napoca-cand-vor-fi-gata-primele-modele-3882683
- https://www.ziarulprofit.ro/o-companie-ucraineana-deschide-o-fabrica-de-drone-militare-la-cluj-interceptoarele-vor-integra-tehnologia-romaneasca-nemesis-ai/
- https://cluj24.ro/drone-militare-fabricate-la-cluj-in-parteneriat-cu-ucraina-o-companie-clujeana-va-produce-pana-la-1-000-de-unitati-pe-luna-299397.html
- https://www.afaceri.news/parteneriat-romano-ucrainean-prima-fabrica-de-drone-militare-se-va-deschide-la-cluj/
- https://www.economica.net/drone-militare-fabricate-in-romania-au-fost-deja-testate-pe-front-si-vor-iesi-din-fabrica-echipate-complet-si-pregatite-pentru-utilizare-operationala_962925.html
- https://oecd.ai/en/incidents/2026-07-28-6f7b

### OVES – STARK (drone navale VANTA)

- https://www.romania-insider.com/society/oves-stark-maritime-drones-sept-2026
- https://www.wall-street.ro/articol/it-and-c/parteneriat-romano-german-pe-piata-dronelor-militare-mutarea-oves-enterprise.html
- https://startupcafe.ro/tehnologie-ai-romaneasca-pe-o-platforma-navala-care-tocmai-a-intrat-in-testarea-armatei-germane-cofondatorul-stark-a-fondat-si-quantum-systems-furnizor-al-romaniei-prin-safe-106045
- https://www.revistabiz.ro/oves-integreaza-nemesis-ai-in-sistemele-autonome-dezvoltate-de-stark/
- https://cursdeguvernare.ro/oves-enterprise-si-compania-germana-stark-semneaza-un-parteneriat-pentru-integrarea-ai-in-sisteme-navale-autonome.html
- https://oecd.ai/en/incidents/2026-09-01-e44c

### OVES – MSI Defense și EAGLS (armata SUA)

- https://www.msidefense.com/next-gen-ai-threat-mitigation/
- https://thedefensepost.com/2025/04/30/ai-autonomous-threat-interception-eagls/amp/
- https://www.romania-insider.com/romanias-oves-partners-us-company-msi-develop-ai-powered-anti-drone-and-anti-missile-systems
- https://startupcafe.ro/soft-de-inteligenta-artificiala-dezvoltat-la-cluj-ajunge-in-sistemele-antidrona-ale-armatei-sua-din-orientul-mijlociu-96058
- https://www.forbes.ro/tehnologia-nemesis-ai-dezvoltata-de-oves-enterprise-este-utilizata-in-sistemele-antidrona-eagls-ale-armatei-americane-din-orientul-mijlociu-491562
- https://www.economica.net/tehnologie-romaneasca-folosita-de-armata-sua-in-orientul-mijlociu-ce-aduce-nemesis-ai-pe-campul-de-lupta_921502.html/amp
- https://www.romanianbusinessjournal.ro/nemesis-ai-the-technology-developed-by-oves-enterprise-romanian-company-is-used-in-eagls-counter-drone-systems-deployed-by-the-u-s-army-in-the-middle-east/
- https://cuashub.com/en/content/msi-to-enhance-eagls-system-with-oves-ai-technology/
- https://www.zfenglish.com/companies/oves-enterprise-s-nemesis-ai-technology-used-in-eagls-counter-drone-23084701

### OVES – Overwatch Aerospace și extinderea în SUA

- https://www.thediplomat.ro/2025/03/17/oves-enterprise-signs-deal-with-overwatch-aerospace-to-integrate-ai-technology-into-advanced-military-drones/
- https://economedia.ro/oves-enterprise-dezvoltator-roman-de-software-va-furniza-tehnologie-ai-pentru-drone-militare-avansate-folosite-inclusiv-de-guvernul-britanic-si-in-operatiuni-desfasurate-in-ucraina.html
- https://www.romania-insider.com/business/romanian-oves-enterprise-expanding-us-military-drones-2025
- https://startupcafe.ro/firma-clujeana-de-solutii-software-parteneriat-cu-o-companie-americana-pentru-dezvoltarea-dronelor-militare-de-mari-dimensiuni-85491

### OVES – hardware, plăci electronice, producție de drone

- https://www.romania-insider.com/business/oves-production-printed-electronic-boards-jul-2024
- https://economedia.ro/compania-romaneasca-de-software-oves-enterprise-achizitioneaza-un-pachet-minoritar-in-mxt-creation-si-intra-pe-piata-productiei-de-placi-electronice-imprimate.html
- https://www.romania-insider.com/society/oves-romania-drone-manufacturing-february-2024
- https://www.romanianbusinessjournal.ro/the-romanian-company-oves-enterprise-invests-in-the-production-of-drones-including-those-with-military-utility/
- https://startupcafe.ro/companie-it-cluj-investitie-drone-euro-htm-24465

### OVES – firmă, finanțare, CEO

- https://www.amcham.ro/company/oves-enterprise
- https://www.thediplomat.ro/2025/01/28/romanian-software-company-oves-enterprise-to-invest-3-million-euro-in-rd-in-2025/
- https://businessforum.ro/industry/20250128/oves-enterprise-accelerates-investments-allocating-eur3-million-for-rd-in-2025-1331
- https://www.businessforum.ro/economy/20241212/oves-enterprise-aims-for-eur20-million-revenue-in-2024-1170
- https://seenews.com/news/romanias-oves-enterprise-in-talks-to-raise-55-mln-euro-1293665
- https://www.profit.ro/povesti-cu-profit/oves-enterprise-discuta-atragerea-unei-finantari-de-55-milioane-euro-la-o-evaluare-de-298-milioane-euro-22419927
- https://www.businessforum.ro/industry/20241101/oves-enterprise-and-kongsberg-defence-aerospace-potential-strategic-partnership-983
- https://www.romanianbusinessjournal.ro/oves-enterprise-romanian-software-development-start-up-and-drone-manufacturer-opens-its-first-office-in-norway/
- https://romania-insider.com/oves-enterprise-munich-office-feb-2022
- https://www.revistabiz.ro/mihai-filip-oves-enterprise-avem-un-buget-de-rd-de-25-mil-euro-pentru-2024/
- https://profit.ro/profit-live/video-profit-live-tv-mihai-filip-ceo-oves-enterprise-conteaza-cea-mare-bomba-ci-cel-inteligent-sistem-vrem-ducem-nemesis-nivelul-urmator-protejam-partenerii-nato-spatiu-22134921
- https://emerging-europe.com/emerging-europe-talks-success-and-failure-it-and-software-business-with-oves-enterprises-mihai-filip/
- https://www.howtoweb.co/speaker/mihai-filip/
- https://clutch.co/profile/oves-enterprise
- https://www.designrush.com/agency/profile/oves-enterprise-srl
- https://www.zfenglish.com/tags/oves+enterprise

### YOLO Machines

- https://yolomachines.com/ (contact: hello@yolomachines.com)
- https://militaeraktuell.at/en/yolo-machines-a-romanian-anti-drone-startup/ (interviu cu Lorand Minyo, EN)
- https://militaeraktuell.at/yolo-machines-rumaenisches-anti-drohnen-startup/ (același interviu, DE)
- https://www.linkedin.com/in/lorandminyo/
- https://www.romaniajournal.ro/amp/business/16-high-potential-tech-companies-join-vanguard-the-first-strategic-deep-tech-accelerator-in-southeast-europe/
- https://outsourcing-today.ro/?p=15972
- https://www.revistabiz.ro/16-companii-tehnologice-cu-potential-ridicat-au-fost-selectate-in-techcelerator-vanguard/
- https://startupcafe.ro/16-startup-uri-si-scaleup-uri-romanesti-intra-intr-un-accelerator-pentru-tehnologii-strategice-acces-la-finantari-ue-si-nato-de-miliarde-de-euro-pentru-drone-cybersecurity-si-spatiu-102349
- https://romania-insider.com/romanias-techcelerator-launches-first-deep-tech-cybersecurity-accelerator-southeast-europe (contextul programului Vanguard)

### Ce nu am găsit

- Un email public pentru OVES. Site-ul are doar formular.
- Pagini de cariere sau internship-uri publice la OVES sau YOLO.
- Un parteneriat formal OVES–UTCN.
- Date tehnice independente despre sistemul YOLO. Totul vine de la firmă.
