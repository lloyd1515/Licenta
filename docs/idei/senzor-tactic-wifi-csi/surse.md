# Surse și descoperiri

Cercetare din 2026-11-12, cu căutări web. Fiecare secțiune are linkurile și ce am găsit în ele.

Legendă pentru încredere:

- **[oficial]**: site-ul firmei, al instituției sau o lucrare științifică
- **[presă]**: presă de specialitate sau presă generală
- **[slab]**: blog, listă comercială sau sursă pe care nu am putut-o verifica

Multe cifre (evaluări de firme, sume, prețuri) diferă între surse. Verifică cifra în sursa oficială înainte să o scrii în teză.

## Cuprins

1. [Ecosistemul de apărare din România](#1-ecosistemul-de-apărare-din-românia)
2. [Finanțare și programe: SAFE, NATO DIANA, acceleratoare](#2-finanțare-și-programe-safe-nato-diana-acceleratoare)
3. [Firme de apărare din Europa](#3-firme-de-apărare-din-europa)
4. [Firme de apărare din SUA și Israel](#4-firme-de-apărare-din-sua-și-israel)
5. [Senzori prin perete (produse)](#5-senzori-prin-perete-produse)
6. [Senzori de teren (UGS) și rețele de senzori ieftini](#6-senzori-de-teren-ugs-și-rețele-de-senzori-ieftini)
7. [Radar pasiv și Wi-Fi pasiv](#7-radar-pasiv-și-wi-fi-pasiv)
8. [Cercetare Wi-Fi CSI: intruziune și prin perete](#8-cercetare-wi-fi-csi-intruziune-și-prin-perete)
9. [Cercetare Wi-Fi CSI: atacuri și apărare](#9-cercetare-wi-fi-csi-atacuri-și-apărare)
10. [Respirația măsurată cu ESP32 CSI](#10-respirația-măsurată-cu-esp32-csi)
11. [Senzor în mișcare: compensare și IMU](#11-senzor-în-mișcare-compensare-și-imu)
12. [Radar UWB ieftin](#12-radar-uwb-ieftin)
13. [Drone: detecție prin CSI și Remote ID](#13-drone-detecție-prin-csi-și-remote-id)
14. [Victime sub dărâmături și triaj](#14-victime-sub-dărâmături-și-triaj)
15. [Gadgeturi: radar Seeed de 60 GHz](#15-gadgeturi-radar-seeed-de-60-ghz)
16. [ATAK, CoT și integrarea software](#16-atak-cot-și-integrarea-software)
17. [Comunicații mesh: Meshtastic și LoRa](#17-comunicații-mesh-meshtastic-și-lora)
18. [Senzori purtabili pentru soldați](#18-senzori-purtabili-pentru-soldați)
19. [Biblioteci pentru ilustrații](#19-biblioteci-pentru-ilustrații)
20. [Descoperiri din repo și de pe placă](#20-descoperiri-din-repo-și-de-pe-placă)

---

## 1. Ecosistemul de apărare din România

Concluzie: aproape toate firmele noi lucrează pe drone și anti-dronă. Nu am găsit nicio firmă românească pentru senzori prin perete sau pentru detecția victimelor.

### Firme noi (startup-uri)

| Firmă | Oraș | Ce face |
|---|---|---|
| OVES Enterprise | Cluj | Software AI „Nemesis” pentru anti-dronă. Armata SUA îl folosește în sistemele EAGLS din Orientul Mijlociu. Sistemul de interceptare SkyLock (ianuarie 2026). Parteneriat cu MSI (SUA) și cu STARK (drone navale). Joint venture româno-ucrainean pentru drone în Cluj (iulie 2026). |
| YOLO Machines | Cluj | Anti-dronă autonom (optică, embedded, ML). Fondată în 2025, CEO Lorand Minyo, program al INC3 Ventures. Faza de pre-prototip. |
| Qognifly | București | „Drone Wall”: detectează, urmărește și interceptează drone. Plan de fabrică în București. Sistem integrat cu interoperabilitate NATO. |
| BraveX Aero | București | Drone interceptoare și drone-țintă. În Orange Fab și în Techcelerator Vanguard. |
| Solomonar Corp | — | Drone interceptoare cu 5G și AI. Locul 3 la hackathonul EUDIS. |
| SkyHunter (România) | — | Interceptor de drone printat 3D, de 4 români. A câștigat hackathonul EUDIS din România. Nu confunda cu Sky Hunter din Ucraina. |
| Orbotix | Brașov | Drone autonome, roiuri, supraveghere cu AI |
| Obrotix Industries | — | Plan cu ROMAERO: 1.500 de drone militare pe lună |
| Artemis Research & Innovation | București | IMM româno-grec (2020): hardware RF, senzori, AI. Coordonator într-un proiect EDF 2023. Profilul exact nu este confirmat. |

### Firme mari și de stat

| Firmă | Ce face |
|---|---|
| Pro Optica | Lider în optronică de apărare: vedere pe timp de noapte, aparate de ochire, sisteme ISTAR, stația de armament ANUBIS, Argus FO3C |
| Aerostar (Bacău) | Mentenanță pentru avioane militare. Modernizări MiG-21 și MiG-29 cu Elbit. |
| ROMARM | Firmă de stat. Carfil produce drone cu Periscope Aviation (SUA) din 2025. |
| BlueSpace Technology | Echipamente TEMPEST pentru NATO |
| Rheinmetall (în România) | Contracte de aproximativ 6 mld. EUR prin SAFE. Peste 200 de subcontractori români. |
| UTI Grup, Teamnet, Electromagnetica | Nu am găsit informații actuale. |

### Persoane de contact (pentru emailuri)

| Firmă | Persoană | Ce știm |
|---|---|---|
| OVES Enterprise | Mihai Filip, CEO | Firmă fondată în Cluj-Napoca în 2015, cu birouri în Europa, Orientul Mijlociu și SUA. Fondatorul nu este numit în surse. Alte proiecte: racheta de croazieră Sahara (februarie 2026), drone navale cu STARK, extindere în SUA. |
| YOLO Machines | Lorand Minyo | Presa îl numește antreprenor român, CEO și fondator. Profilul LinkedIn (zona Cluj) listează YOLO Machines și „Neveli” (interceptare counter-UAS), dar rolul exact nu este clar. A lucrat la Trilulilu (Cluj). Firmă fondată în 2025, în faza de pre-prototip. |

Canale de contact (verificate pe 2026-11-12):

- OVES: site-ul nu publică nicio adresă de email sau telefon. Contact doar prin formularul „Get in touch” de pe https://ovesenterprise.com/contact. Adresa din Cluj: Str. Eugen Ionesco 109A, 400357 Cluj-Napoca. Nu am găsit profilul LinkedIn al lui Mihai Filip; o sursă îl numește purtător de cuvânt, altele CEO.
- YOLO Machines: nu am găsit site, email sau telefon. Singurul canal găsit este LinkedIn-ul lui Lorand Minyo. Firma este un program al INC3 Ventures SRL; site-ul INC3 nu este confirmat (posibil inc3.net, Incube Venture Studio).
- Nu ghici adrese de email după model (prenume.nume@firmă). Folosește doar canalele publicate.

Linkuri pentru persoane:

- [oficial] https://ovesenterprise.com/contact
- [slab] https://www.piatafinanciara.ro/tag/oves-enterprise/
- [slab] https://village.ai/company/incube-venture-studio

- [presă] https://www.romania-insider.com/oves-cruise-missile-romania-feb-2026
- [presă] https://www.romania-insider.com/society/oves-stark-maritime-drones-sept-2026
- [presă] https://www.romania-insider.com/business/romanian-oves-enterprise-expanding-us-military-drones-2025
- [presă] https://www.bursa.ro/sahara-autonomous-system-oves39-bet-on-smart-scalable-and-low-cost-missiles-24234856
- [presă] https://www.forbes.ro/tehnologia-nemesis-ai-dezvoltata-de-oves-enterprise-este-utilizata-in-sistemele-antidrona-eagls-ale-armatei-americane-din-orientul-mijlociu-491562
- [presă] https://actualdecluj.ro/un-dezvoltator-de-software-din-cluj-cu-expertiza-in-domeniile-militar-si-cybersecurity-face-apel-la-guvernul-romaniei-sa-faca-din-inteligenta-artificiala-o-prioritate-strategica-pentru-secu/
- [presă] https://www.economica.net/tehnologie-romaneasca-folosita-de-armata-sua-in-orientul-mijlociu-ce-aduce-nemesis-ai-pe-campul-de-lupta_921502.html
- [presă] https://www.businessforum.ro/industry/20241101/oves-enterprise-and-kongsberg-defence-aerospace-potential-strategic-partnership-983
- [oficial] https://ro.linkedin.com/in/lorandminyo
- [slab] https://lorand.medium.com/about

### Linkuri

- [presă] https://www.romania-insider.com/qognifly-counter-drone-system-march-2026
- [presă] https://www.romania-insider.com/society/romanian-qognifly-integrated-drone-system-nato-2026
- [presă] https://www.businessforum.ro/industry/20260304/romanian-firm-qognifly-launches-counter-drone-system-2945/amp
- [presă] https://outsourcing-today.ro/?p=15151
- [presă] https://militaeraktuell.at/en/yolo-machines-a-romanian-anti-drone-startup/
- [presă] https://militaeraktuell.at/yolo-machines-rumaenisches-anti-drohnen-startup/
- [presă] https://www.romanianbusinessjournal.ro/nemesis-ai-the-technology-developed-by-oves-enterprise-romanian-company-is-used-in-eagls-counter-drone-systems-deployed-by-the-u-s-army-in-the-middle-east/
- [presă] https://www.romanianbusinessjournal.ro/oves-enterprise-launches-skylock-an-integrated-ai-based-drone-interception-system-tested-in-real-world-conditions/
- [presă] https://www.romanianbusinessjournal.ro/romanian-company-oves-enterprises-and-msi-defense-solutions-announce-strategic-partnership-to-develop-advanced-ai-powered-anti-drone-and-anti-missile-systems/
- [presă] https://www.zfenglish.com/companies/technology-telecoms/oves-enterprise-launches-skylock-an-integrated-ai-based-drone-23028861
- [presă] https://www.romania-insider.com/romanias-oves-partners-us-company-msi-develop-ai-powered-anti-drone-and-anti-missile-systems
- [presă] https://www.romania-insider.com/oves-edrone-drone-production-cluj-july-2026
- [presă] https://startupcafe.ro/soft-de-inteligenta-artificiala-dezvoltat-la-cluj-ajunge-in-sistemele-antidrona-ale-armatei-sua-din-orientul-mijlociu-96058
- [presă] https://www.antena3.ro/actualitate/ceo-ul-nemesis-ai-ucigasul-romanesc-de-drone-folosit-de-sua-sper-ca-in-viitor-si-armata-romana-sa-se-poata-mandri-cu-sistemul-780627.html
- [presă] https://informat.ro/en/current-affairs/romanian-technology-nemesis-ai-used-by-the-us-military-in-the-middle-east-111278
- [presă] https://www.euronews.ro/articole/interceptor-pentru-combaterea-dronelor-produs-la-cluj
- [presă] https://www.romania-insider.com/orange-fab-startups-romania-june-2026
- [presă] https://startupcafe.ro/sistem-inteligent-aparare-aeriana-5000-euro-castigatori-hackathon-eudis-2026-solutii-domeniu-tehnologii-militare-aparare-97264
- [presă] https://startupcafe.ro/trei-romani-castig-2500-euro-hackathon-ue-solutii-domeniu-tehnologii-militare-aparare-88425
- [presă] https://www.revistabiz.ro/patru-romani-au-creat-skyhunter-un-interceptor-de-drone-imprimat-3d-proiectul-merge-la-o-competitie-europeana/
- [presă] https://scroll.media/en/?p=34121 (Sky Hunter din Ucraina, altă firmă)
- [presă] https://feedbagel.com/post/romanian-startup-shifts-from-civilian-to-military-drones
- [presă] https://www.romanianbusinessjournal.ro/why-doesnt-the-ministry-of-national-defense-encourage-drones-and-technologies-created-by-romanian-companies-and-start-ups-due-to-lack-of-interest/
- [oficial] https://prooptica.ro/company/
- [slab] https://platform.defencefinancemonitor.com/threads/pro-optica-sa-strategic-technological
- [oficial] https://en.wikipedia.org/wiki/Aerostar_SA
- [oficial] https://en.wikipedia.org/wiki/ROMARM
- [oficial] https://en.wikipedia.org/wiki/I.O.R.
- [oficial] https://en.wikipedia.org/wiki/Frankenburg_Technologies
- [slab] https://www.globalsecurity.org/military/world/europe/ro-industry.htm (listă veche)
- [slab] https://www.defencejobs.org/companies/country/romania (director de firme)
- [slab] https://www.failory.com/startups/romania
- [oficial] https://bstech.ro/en/category/news-bstech/ (BlueSpace, TEMPEST)
- [oficial] https://tehnomil.net/wp-content/uploads/2024/05/EDF_2023.pdf (proiecte EDF 2023, Artemis R&I)
- [oficial] https://een.ec.europa.eu/node/63717 (profil EEN, firmă fără nume în extras)
- [slab] https://cdnc.heyzine.com/flip-book/pdf/6755466066f712b93c2048e7c5a07af9ca330aba.pdf (Romanian Space Catalogue)
- [slab] https://www.globaldata.com/store/report/romania-defense-market-analysis/ (raport plătit)
- [presă] https://noatech.ro/calendarul-evenimentelor-defence-tech-si-dual-use-pentru-startup-urile-din-romania-si-europa-in-2026/ (calendar de evenimente 2026)

## 2. Finanțare și programe: SAFE, NATO DIANA, acceleratoare

### SAFE (împrumut UE pentru apărare)

- România: aproximativ 16,7 mld. EUR, a doua țară după Polonia.
- Acordul a fost semnat pe 12 mai 2026. Prima tranșă: 2,5 mld. EUR, pe 26 august 2026.
- 21 de proiecte MApN: 10 achiziții comune (mai ales cu Franța și Germania) și 11 doar pentru România.
- Legea cere cooperare industrială și producție locală la unele contracte.

Linkuri:

- [presă] https://www.intellinews.com/romania-signs-16-7bn-safe-financing-agreement-with-european-commission-444426/
- [presă] https://startupcafe.ro/romania-primeste-25-miliarde-eur-pentru-aparare-de-la-ue-este-prima-transa-din-imprumutul-safe-de-167-miliarde-eur-105773
- [presă] https://www.rri.ro/en/news-and-current-affairs/today-in-the-news/projects-funded-under-the-safe-program-id975749.html
- [presă] https://www.rri.ro/en/features-and-reports/the-future-starts-today/the-future-starts-today-green-light-for-safe-projects-id984880.html
- [presă] https://www.rri.ro/en/news-and-current-affairs/today-in-the-news/military-cooperation-id981871.html
- [presă] https://www.romania-insider.com/society/romania-procurement-list-safe-jan-2026
- [presă] https://pressone.ro/romania-beneficiar-major-al-safe-ce-vrea-statul-sa-faca-cu-cele-166-miliarde-de-euro
- [presă] https://www.capital.ro/romania-pastreaza-integral-banii-din-safe-pe-ce-vor-fi-cheltuiti-si-ce-se-intampla-cu-contractele-nesemnate-inca-raport-detaliat-al-guvernului.html
- [presă] https://businessforum.ro/finance/20260522/romania-secures-eur1668-billion-eu-defence-funding-deal-3232
- [slab] https://www.alcircle.com/news/romania-boosts-defence-industry-with-2-5b-from-eu-safe-payment-120960
- [slab] https://samsearch.co/government-contracting-news/romania-secures-1668b-to-enhance-military-procurement-amid-urgent-deadline-103121

### NATO DIANA

- Iunie 2026: NATO DIANA a aprobat 5 centre de testare noi în România, în bugetul pe 2027 (anunț ICI București).
- Politehnica București va găzdui un accelerator DIANA național.
- INCAS reprezintă România în cohorta DIANA 2026.
- Firmele selectate primesc 100.000 EUR și acces la peste 200 de centre de testare.
- Eligibilitate: firmă înregistrată într-o țară NATO, cu sediul acolo și cu proprietari majoritari din țări NATO.
- Apelul pentru cohorta 2027 (termen 3 iulie 2026) are 6 provocări. Cele relevante pentru acest concept:
  - „Multidomain Sensing and Advanced Data Processing for Intelligence and Surveillance”
  - „Operational Resilience in Contested Environments”
  - „Human Survivability” (exemplu: triaj asistat de AI)
- Cohorta 2026: 150 de firme, 10 provocări.

Linkuri:

- [oficial] https://www.diana.nato.int/connect/nato-diana-unveils-six-new-challenges-to-tackle-evolving-defence-and-security-needs.html
- [oficial] https://www.diana.nato.int/connect/nato-diana-announces-largestever-cohort-150-innovators-selected-across-ten-challenge-areas-for-2026-challenge-programme.html
- [oficial] https://www.diana.nato.int/connect/nato-diana-unveils-10-new-challenges-to-accelerate-dualuse-technology-breakthroughs.html
- [oficial] https://iuk-business-connect.org.uk/opportunities/nato-defence-innovation-accelerator-diana-2027-cohort/ (link spre documentul complet al provocărilor)
- [presă] https://www.romania-insider.com/society/romania-nato-diana-test-centers-june-2026
- [presă] https://agerpres.ro/english/2026/06/04/nato-diana-board-of-directors-approves-inclusion-of-five-new-romania-based-testing-centres-in-2027-b--1563113
- [presă] https://startupcafe.ro/nato-deschide-usa-pentru-inca-5-centre-de-testare-in-romania-proiectele-diana-intra-in-bugetul-de-anul-viitor-100946
- [presă] https://cursdeguvernare.ro/universitate-politehnica-gazduire-centru-national-diana-nato-accelerator-inovatii-dual-use.html
- [presă] https://startupcafe.ro/romania-prezenta-accelerator-nato-afaceri-diana-2026-institut-cercetare-dezvoltare-aerospatiala-91379
- [presă] https://startupcafe.ro/inscrieri-lansare-provocari-program-accelerator-diana-2027-finantari-nato-100000-euro-100729
- [presă] https://www.capital.ro/nato-ofera-100-000-de-euro-pentru-tehnologii-inovatoare-romanii-se-pot-inscrie-in-acceleratorul-diana-2027.html
- [presă] https://romania-insider.com/grayscale-nato-diana-programme-2023
- [presă] https://www.revistabiz.ro/romania-printre-cele-mai-importante-tari-aplicante-in-acceleratorul-nato-pentru-inovare/
- [presă] https://thequantuminsider.com/2026/06/02/nato-diana-announces-six-new-challenges-to-tackle-evolving-defense-and-security-needs/
- [presă] https://soldiersystems.net/2026/06/02/nato-diana-unveils-six-new-challenges-to-tackle-evolving-defence-and-security-needs/
- [presă] https://nordicdefencesector.com/en/article/nato-diana-announces-six-new-challenges-for-2027
- [presă] https://6gworld.com/natos-2026-diana-challenge-programme/
- [slab] https://www.inventya.com/calls/nato-diana-2027-challenge-call
- [slab] https://www.developmentaid.org/grants/view/1496569/nato-diana-challenge-call-for-2026-phase-1

### Acceleratoare și evenimente din România

- Techcelerator Vanguard (iunie–decembrie 2026), 16 firme:
  - Acceleration: Solomonar Corp, SkyHunter, Zerotak (vulnerabilități cyber), ATD Aerospace RS (motoare de rachetă), RISE, YOLO Machines, Delphys Dynamics, Crystal Matrix Design, Headlight Solutions, QUADYX.
  - ScaleUp Booster: BraveX Aero, Bright Spaces, Reps Mate, OxidOS, FieldOS, Wolf-E.
- Orange Fab: 58 de firme în total. BraveX Aero a intrat în mai 2026.
- Bulgaria pregătește un fond de 30 mil. EUR pentru apărare. România se bazează mai ales pe granturi UE și NATO.
- Evenimente 2026: EUDIS Defence Hackathon (15–17 octombrie), Naval Defense Tech Hackathon Uptide Danube 26, Galați (2–4 octombrie).

Linkuri:

- [presă] https://start-up.ro/cele-16-startup-uri-selectate-in-acceleratorul-dual-use-techcelerator-vanguard
- [presă] https://startupcafe.ro/16-startup-uri-si-scaleup-uri-romanesti-intra-intr-un-accelerator-pentru-tehnologii-strategice-acces-la-finantari-ue-si-nato-de-miliarde-de-euro-pentru-drone-cybersecurity-si-spatiu-102349
- [presă] https://www.bursa.ro/techcelerator-vanguard-selecteaza-16-companii-tehnologice-pentru-securitate-cibernetica-si-infrastructura-critica-09214950
- [presă] https://www.romaniajournal.ro/amp/business/16-high-potential-tech-companies-join-vanguard-the-first-strategic-deep-tech-accelerator-in-southeast-europe/
- [presă] https://www.revistacariere.ro/noutati/16-companii-tehnologice-au-fost-selectate-in-programul-techcelerator-vanguard
- [presă] https://www.revistabiz.ro/16-companii-tehnologice-cu-potential-ridicat-au-fost-selectate-in-techcelerator-vanguard/
- [slab] http://www.romaniapozitiva.ro/administratie/16-companii-tehnologice-cu-potential-ridicat-au-fost-selectate-in-techcelerator-vanguard-primul-accelerator-integrat-de-deeptech-din-europa-de-sud-est-dedicat-tehnologiilor-strategice/
- [slab] https://www.mediablog.ro/2026/06/16-companii-romanesti-intra-in.html
- [presă] https://startupcafe.ro/bulgaria-pregateste-un-fond-de-30-milioane-eur-pentru-startup-uri-de-aparare-romania-se-bazeaza-mai-ales-pe-granturi-ue-si-nato-104092

## 3. Firme de apărare din Europa

| Firmă | Țară | Produse |
|---|---|---|
| Helsing | Germania | AI pentru apărare, drone HX-2 și HF-1, drona subacvatică SG-1 Fathom |
| Quantum Systems | Germania | Drone de recunoaștere Vector |
| Stark | Germania | Drona de atac Virtus |
| Tekever | Portugalia | Drone de supraveghere AR3 și AR5 |
| ARX Robotics | Germania | Roboți terestri Gereon, Mithra OS |
| Hensoldt | Germania | Radarul pasiv TwInvis (vezi secțiunea 7) |
| Project Q | Germania | Kit UGS seismic-acustic cu AI (Eurosatory 2026) |
| Bertin Exensor | Franța | Rețeaua UGS Flexnet |
| Centum | Spania | Lifeseeker: găsește telefoane sub dărâmături, din dronă sau elicopter |

Linkuri:

- [oficial] https://en.wikipedia.org/wiki/Helsing_(company)
- [slab] https://dealroom.co/lists/defence-startups-europe/
- [slab] https://www.defencejobs.org/articles/german-defence-tech
- [slab] https://axomap.com/maps/european-defense-startups
- [slab] https://dronehub.ai/blog/european-defense-drone-investment-landscape
- [slab] https://signalsinbox.com/blogs/news/defense-tech-startups-europe
- [slab] https://m-ric.com/blog/european-drone-landscape/
- [slab] https://newmarketpitch.com/blogs/news/defense-tech-top-startups-valuation

## 4. Firme de apărare din SUA și Israel

| Firmă | Produse |
|---|---|
| Anduril | Lattice (fuziune de senzori, imagine operațională comună, rețea mesh), turnuri Sentry, drone, interceptoare. Evaluare raportată: 61 mld. USD. |
| Palantir | Gotham, Foundry, AIP, Maven Smart System |
| Shield AI | Pilotul AI Hivemind, V-BAT, X-BAT |
| Saronic | Nave de suprafață autonome |
| Epirus | Microunde de mare putere împotriva roiurilor de drone |
| CHAOS Industries | Radar distribuit pentru anti-dronă (detalii negăsite) |
| Hidden Level | Senzori RF pasivi BREAKER (fix) și SURGE (mobil). Contract OTA de 100 mil. USD cu DoD. |
| Lumineye, L3Harris Range-R, Camero (Israel), Vayyar (Israel) | Vezi secțiunea 5 |

Despre Lattice:

- Lattice acceptă orice senzor, rețea sau sistem, civil sau militar.
- AI filtrează datele și le trimite într-o rețea mesh.
- Rețeaua ocolește nodurile și legăturile distruse.
- Echipele terțe își integrează senzorii singure, prin API și SDK.
- Nu am găsit surse despre „senzori ieftini” în modelul Lattice.

Linkuri:

- [oficial] https://developer.anduril.com/guides/concepts/principles
- [presă] https://www.ex2.com.au/uncategorized/in-detail-anduril-a-software-company-enabled-by-hardware/
- [presă] https://breakingdefense.com/2024/12/decentralizing-battle-data-cdao-anduril-open-tactical-mesh-to-third-party-developers
- [presă] https://defensescoop.com/2024/12/03/anduril-awarded-100m-deal-cdao-scale-edge-data-mesh-capabilities-ota/
- [presă] https://defensescoop.com/2024/11/21/anduril-space-surveillance-network-upgrade-contract-sdanet/
- [presă] https://insideunmannedsystems.com/u-s-army-enterprise-contract-with-anduril-positions-lattice-as-core-platform-for-c-uas-operations/
- [presă] https://businesswire.com/news/home/20230509005464/en/Aalyria-Anduril-Partner-to-Integrate-Technologies-to-Enhance-Battlefield-Capabilities
- [oficial] https://softwareengineeringdaily.com/wp-content/uploads/2021/11/SED1381-Forrest-Landola.pdf (interviu Anduril)
- [presă] https://www.everythingrf.com/news/details/20703-hidden-level-offers-advanced-rf-sensing-solutions-to-mitigate-threats-in-mission-critical-environments
- [presă] https://militaryembedded.com/unmanned/counter-uas/counter-uas-tech-from-hidden-level-wins-100-million-dod-contract
- [slab] https://www.robotics.press/companies/hidden-level/
- [slab] https://droneintelligence.ai/companies/hidden-level
- [slab] https://newmarketpitch.com/blogs/news/defense-tech-next-anduril
- [slab] https://beststartup.us/top-10-us-defence-tech-startups-2026/
- [slab] https://valueaddvc.com/defense-tech
- [slab] https://startupill.com/top-10-defense-tech-startups-2026/

## 5. Senzori prin perete (produse)

Aceasta este categoria cea mai apropiată de concept.

| Produs | Ce știm |
|---|---|
| Lumineye Lux | Radar cu impulsuri, carcasă printată 3D, 0,7 kg. Detectează oameni care se mișcă sau respiră după perete. Rază de 15 m în aer liber. Arată doar distanța (1D). Mai multe unități pot triangula. Premiu xTechSearch de 250.000 USD de la Armata SUA (2019). Feedback de la SOCOM. Preț necunoscut. |
| L3Harris Range-R | Detector portabil. Arată prezența, distanța și direcția oamenilor care se mișcă sau stau pe loc. |
| Camero Xaver (100, 400, 800, 1000) | Radar UWB de 3–10 GHz. Xaver 800: imagine 3D, respirație. Clienți: armate, poliție, salvare. |
| Camero XLR-40 | Radar prin perete cu rază lungă, pentru oraș |
| Vayyar | Radar de 3–81 GHz, până la 72 de antene pe cip. Produs pentru căderi (Walabot HOME, Vayyar HOME). Nu am găsit clienți militari. |
| SRC Inc. | Brevet din ianuarie 2026 pentru detecția radar a respirației prin perete |

Pieptul se mișcă 1–5 mm la respirație. Această mișcare produce o modulație Doppler mică, dar detectabilă.

Linkuri:

- [presă] https://www.militarytimes.com/news/your-army/2019/10/24/this-device-could-help-soldiers-see-through-walls-in-the-urban-fight
- [presă] https://taskandpurpose.com/news/army-xtechsearch-lumineye.md
- [presă] https://techcrunch.com/?p=1869460
- [oficial] https://www.sbir.gov/awards/185376
- [slab] https://www.inknowvation.com/sbir/companies/lumineye-inc
- [slab] https://en.techrecipe.co.kr/posts/6787
- [oficial] https://camero-tech.com/camero-tech-launches-its-groundbreaking-xavertm-long-range-system/
- [presă] https://www.edrmagazine.eu/xlr-40-an-urban-long-range-sense-through-the-wall-radar-from-camero
- [presă] https://www.janes.com/defence-intelligence-insights/defence-news/israels-camero-networks-sense-though-wall-radars-to-mount-on-unmanned-platforms
- [presă] https://www.aviation-defence-universe.com/camero-tech-an-sk-group-member-has-received-a-purchase-order-for-xavertm-long-range-sense-through-the-wall-sttw-system-from-a-western-european-police-special-forces
- [oficial] https://nij.ojp.gov/index%2ephp/library/publications/through-wall-sensors-ttws-law-enforcement-test-evaluation-version-12 (evaluare NIJ pentru poliție)
- [oficial] https://ojp.gov/pdffiles1/nij/nlectc/240729.pdf
- [oficial] https://www.srcinc.com/news-and-events/press/2026/20260107-Patent-for-Detecting-Breathing-Radar-Targets.html
- [presă] https://www.asdnews.com/news/defense/2026/01/07/src-awarded-patent-detecting-breathing-radar-targets
- [presă] https://sofrep.com/news/us-army-invests-in-wall-penetrating-radar-to-allow-soldiers-to-see-through-walls
- [presă] https://www.policemag.com/articles/first-look-seeing-through-walls
- [slab] https://rfessentials.com/rf-knowledge-base/how-does-a-through-wall-radar-work-and-what-frequencies-are-most-effective-for-b/
- [slab] https://geozondas.com/radar_moving_detection.html
- [presă] https://www.fiercebiotech.com/medtech/vayyar-launches-home-radar-sensor-for-remotely-detecting-falls
- [presă] https://www.securityinfowatch.com/residential-technologies/product/21122182/vayyar-imaging-vayyar-home-fall-detection-system
- [presă] https://venturebeat.com/business/walabot-home-detects-if-seniors-fall-in-their-homes

## 6. Senzori de teren (UGS) și rețele de senzori ieftini

- UGS = senzori lăsați în teren, fără operator. Tipuri: seismic, acustic, magnetic, optic, infraroșu, PIR.
- Senzorii seismici sunt mici, ieftini și au o istorie lungă în apărare.
- Project Q (Germania): kit UGS seismic-acustic cu AI, la Eurosatory 2026. Clasifică drone, vehicule și oameni.
- Bertin Exensor Flexnet: 4 senzori în rețea mesh. Contract cu țările nordice (DSEI 2025).
- McQ RANGER: seismic, acustic și magnetic.
- Polonia, Estonia și Ucraina dezvoltă mine „inteligente” cu senzori seismici-acustici și rețea mesh criptată.
- Sky Fortress (Ucraina): aproximativ 9.500 de senzori acustici (telefon Android și microfon pe un stâlp), de 400–500 USD fiecare. Datele intră în rețeaua de apărare aeriană Virazh. Toată rețeaua costă mai puțin decât două rachete Patriot.
- Alte rețele acustice ucrainene: Zvook, FENEK. Sky Map unește peste 10.000 de senzori.

Linkuri:

- [presă] https://resiliencemedia.co/project-q-launches-passive-surveillance-sensor-kit-for-contested-environments/
- [presă] https://www.calibredefence.co.uk/dsei-2025-bertin-exensor-secures-contract-with-nordic-nations/
- [oficial] https://www.mcqinc.com/persistent-unattended-sensing-for-brigade-scale-maneuver-fires-and-intelligence-in-contested-high-intensity-conflict/
- [presă] https://www.thinkdefence.co.uk/?p=66686
- [oficial] https://dsiac.dtic.mil/technical-inquiries/notable/unattended-ground-sensor-survey/
- [oficial] https://dsiac.dtic.mil/wp-content/uploads/2018/05/2165849_STI_Document.pdf
- [slab] https://sensoguard.com/ugs-system-unattended-ground-sensors
- [slab] https://defense.dotsaga.live/ (fișă tehnică neverificată)
- [presă] https://euromaidanpress.com/2026/03/24/mesh-networked-smart-mines-under-development-by-poland-estonia-ukraine/
- [presă] https://militarnyi.com/?p=452106
- [presă] https://www.defenseone.com/defense-systems/2024/07/ukraines-cheap-sensors-are-helping-troops-fight-waves-russian-drones/398204/
- [oficial] https://www.army.mil/article/292099/listening_to_the_sky_acoustic_drone_detection_systems_ukraine_emerging_technologies
- [oficial] https://nllp.jallc.nato.int/iks/sharing%20public/20260109_(nu)_%20uas_acoustic_sensor_systems_for_artillery_and_drone_threat_detection.pdf
- [presă] https://english.nv.ua/russian-war/ukrainian-engineers-develop-sky-fortress-drone-detection-system-to-counter-shaheds-50520480.html
- [presă] https://itc.ua/en/news/in-ukraine-9-500-phones-detect-shaheds-by-sound-and-transmit-air-defense-data
- [presă] https://www.janes.com/defence-intelligence-insights/defence-news/weapons/ukraine-conflict-ukrainian-air-defence-employs-passive-sensors-for-detection-and-tracking
- [slab] https://voz.us/en/world/250609/25564/sky-fortress-ukraine-s-low-cost-secret-weapon-to-shoot-down-russian-drones.html
- [slab] https://www.webpronews.com/ukraines-acoustic-sensor-networks-expose-costly-flaws-in-western-air-defenses/
- [presă] https://www.yahoo.com/news/ukraine-launches-production-acoustic-sensors-135935484.html

## 7. Radar pasiv și Wi-Fi pasiv

Aceasta este baza științifică a modului silențios.

- Hensoldt TwInvis: nu emite. Folosește ecourile semnalelor radio analogice, radio digitale și TV. Urmărește în 3D până la 200 de avioane pe o rază de 250 km (cifre ale firmei). Forțele aeriene germane l-au testat în 2023.
- UCL, Chetty, Smith, Woodbridge (2012): IEEE Trans. Geoscience and Remote Sensing, vol. 50, nr. 4, pp. 1218–1226, DOI 10.1109/TGRS.2011.2164411.
  - Receptor pasiv multistatic de 2,4 GHz, în afara clădirii, cu un AP Wi-Fi în interior.
  - Prototip de mărimea unei valize, cu două antene. A găsit poziția, viteza și direcția unui om printr-un zid de cărămidă de 30 cm.
  - Presa spune că Ministerul britanic al Apărării a analizat sistemul pentru lupta în oraș. Nu am verificat afirmația în lucrare.
- Lucrări UCL ulterioare:
  - Li, Piechocki, Woodbridge, Tang, Chetty: beacon-uri rare, AP în repaus, prin perete.
  - Chen et al.: deep learning pe rafale Wi-Fi ambientale; respirație prin perete; clasifică „în picioare”, „pe scaun” și „cădere”.

Linkuri:

- [oficial] https://www.hensoldt.net/products/twinvis-passive-radar-surveillance-of-noiseless-objects
- [presă] https://www.defensenews.com/global/europe/2023/10/25/german-air-force-tests-hensoldt-passive-radar-system-to-boost-defenses/
- [presă] https://www.armyrecognition.com/archives/archives-land-defense/land-defense-2023/hensoldt-explains-twinvis-passive-radar-system-for-silent-surveillance-of-silent-targets
- [presă] https://www.defenceconnect.com.au/joint-capabilities/6431-hensoldt-presents-twinvis-passive-radar-silent-surveillance-of-silent-objects
- [presă] https://www.cio.de/a/deutsche-radarfirma-ortete-us-tarnkappenbomber,3608127
- [presă] https://phys.org/news/2012-08-see-through-wall-surveillance-wifi-shown-ucl.html
- [presă] https://spectrum.ieee.org/tech-talk/at-work/test-and-measurement/see-through-walls-by-the-glow-of-your-wifi
- [presă] https://www.popsci.com/?p=28684
- [presă] https://www.csoonline.com/article/2222896/stealthy-wi-fi-spy-sees-you-through-walls-thanks-to-your-wireless-router.html
- [oficial] https://discovery-pp.ucl.ac.uk/10089404/7/Chetty_Respiration%20and%20Activity%20Detection%20based%20on%20Passive%20Radio%20Sensing%20in%20Home%20Environments_VoR.pdf
- [slab] https://typeset.io/pdf/passive-wifi-radar-for-human-sensing-using-a-stand-alone-jxmmym4ais.pdf
- [oficial] https://electronicimaging.spiedigitallibrary.org/profile/Kevin.Chetty-4013032

## 8. Cercetare Wi-Fi CSI: intruziune și prin perete

- Southampton 2026: detecția intruziunii prin perete cu CSI, faza ca trăsătură principală, 5 activități.
- WiBorder: separă „în interior” de „în exterior”, prin perete.
- WiFiLeaks (IEEE TMC 2024): om nemișcat prin perete, cu dispozitive comune. Raportează 100% la 20 m (cifră neverificată).
- Nu am găsit programe militare care folosesc CSI. Nu am găsit lucrări CSI prin perete pe ESP32.

Linkuri:

- [oficial] https://www.southampton.ac.uk/~sqc/listP/IEEEWCLwifiS2026.pdf
- [oficial] https://shengjieli-pku.github.io/ShengjieLi/Paper/WiBorder.pdf
- [oficial] https://datasec.whu.edu.cn/wp-content/uploads/2024/06/WiFiLeaks_Exposing_Stationary_Human_Presence_Through_a_Wall_With_Commodity_Mobile_Devices.pdf
- [oficial] https://arxiv.org/pdf/1901.00715 (studiu general despre Wi-Fi sensing)
- [oficial] https://www.net.in.tum.de/fileadmin/TUM/NET/NET-2023-11-1/NET-2023-11-1_07.pdf
- [oficial] https://drum.lib.umd.edu/bitstreams/67a77260-1d53-4bc9-b6cb-7eade7983ae9/download
- [oficial] https://eprints.soton.ac.uk/507890/1/Wifi_sensing.pdf
- [slab] https://healsecurity.com/wifi-signals-reveal-human-activities-through-walls-by-mapping-body-keypoints/
- [slab] https://www.blog.brightcoding.dev/2026/07/03/wifi-3d-fusion-the-revolutionary-tool-that-sees-through-walls

## 9. Cercetare Wi-Fi CSI: atacuri și apărare

Relevant pentru capitolul opțional „atac și apărare”.

- IS-WARS: un semnal din alt protocol schimbă CSI și păcălește clasificatorul, fără să strice Wi-Fi-ul.
- INFOCOM 2022 și IEEE TDSC 2024: bruiaj sincronizat care produce exemple CSI false.
- Atac prin preambul (2024, 35 de participanți): 90,47% succes la recunoașterea activității, 83,83% la autentificare.
- NoiFi: detecție a atacurilor, independentă de tipul atacului.
- arXiv 2501.06798: falsificarea țintelor și bruiaj înșelător contra senzorilor WLAN JCAS.
- arXiv 2511.20456: prima evaluare sistematică a robusteții CSI la atacuri ML.
- IRShield (IEEE S&P 2022, Ruhr-Universität Bochum): suprafață reflectorizantă inteligentă (IRS) care ascunde canalul. Detecția mișcării de către atacator scade la 5% sau mai puțin.
- „Et Tu Alexa?”: dispozitivele Wi-Fi din casă devin senzori de mișcare pentru un atacator de afară.

Linkuri:

- [oficial] https://www.cs.fsu.edu/~xzhang/files/IS-WARS_Intelligent_and_Stealthy_Adversarial_Attack_to_Wi-Fi-Based_Human_Activity_Recognition_Systems.pdf
- [oficial] https://hyh6540.github.io/pdf/INFOCOM22_WiFiSensing_Attack.pdf
- [oficial] https://hyh6540.github.io/pdf/TDSC24_WiFi_Sensing_Security.pdf
- [oficial] https://researchwith.njit.edu/en/publications/practical-adversarial-attack-on-wifi-sensing-through-unnoticeable/
- [oficial] https://people.cs.vt.edu/~naren/papers/3779208.3806083.pdf (NoiFi)
- [oficial] https://export.arxiv.org/abs/2501.06798
- [oficial] https://arxiv.org/pdf/2511.20456v1
- [oficial] https://par.nsf.gov/servlets/purl/10296543
- [oficial] https://par.nsf.gov/servlets/purl/10511800
- [oficial] https://re.public.polimi.it/bitstream/11311/1280626/5/Cominelli2024_BeamDancer_TWC_AAM.pdf (BeamDancer)
- [oficial] https://arxiv.org/pdf/2112.01967 (IRShield)
- [oficial] https://casa.rub.de/forschung/publikationen/detail/irshield-a-countermeasure-against-adversarial-physical-layer-wireless-sensing
- [oficial] https://arxiv.org/pdf/1810.10109 (Et Tu Alexa?)

## 10. Respirația măsurată cu ESP32 CSI

| Lucrare | Rezultat |
|---|---|
| Applied Sciences (MDPI 2024), ESP32, 8 participanți | Eroare medie 2,60 respirații/min; 1,38 la respirație normală. Referință: centură Vernier. |
| JCDE (OUP), Wi-ESP | Amplitudine, filtru trece-bandă, vârf spectral. Acuratețe raportată 91–99% (condiții neclare). |
| SA-WiSense (arXiv 2507.17623) | 91,2% detecție până la 8 m, o singură antenă, ESP32 |
| IEEE Access 2024 | Validitatea clinică a respirației din CSI nu este demonstrată. |
| RuView (proiect) | 6–30 respirații/min. Fiecare cameră cere calibrare. Funcționează mai bine cu omul nemișcat. |

Linkuri:

- [oficial] https://mdpi.com/2076-3417/14/15/6458
- [oficial] https://doaj.org/article/8aad8683e5dc44f8a55e87de1d021f4f
- [oficial] https://academic.oup.com/jcde/article/9/3/992/6590610
- [oficial] https://api.crossref.org/works/10.1093%2FJCDE%2FQWAC037
- [oficial] https://arxiv.org/html/2507.17623v2
- [oficial] https://doaj.org/article/af6425956d774801bfa35efac1f160c1
- [oficial] https://unige.iris.cineca.it/retrieve/57607f33-0a52-4ab4-ad09-a6b0a320b78f/phdunige_5554386.pdf
- [slab] https://www.besthub.dev/articles/ruview-9-wifi-board-detects-breath-through-walls-but-pose-estimation-fails-cross-room-6733dcb3dd51
- [slab] https://gh.mise.run.place/ruvnet/RuView/blob/main/docs/edge-modules/medical.md

## 11. Senzor în mișcare: compensare și IMU

- Nu am găsit o lucrare exactă: CSI pe un receptor în mișcare, compensat cu IMU, pentru detecția oamenilor.
- Mobi2Sense: elimină mișcarea proprie a senzorului (robot). Folosește UWB, nu Wi-Fi. IMU-ul nu prinde vibrațiile fine.
- „Et Tu Alexa?”: telefonul folosește accelerometrul și giroscopul pentru pași și traseu, plus măsurători Wi-Fi.
- RIM (SIGCOMM 2019): Wi-Fi folosit ca IMU.
- Brevet USPTO 12137396: schimbă eșantionarea CSI și ponderile când dispozitivul se mișcă.

Linkuri:

- [oficial] https://arxiv.org/pdf/1810.10109
- [slab] https://typeset.io/pdf/mobi2sense-empowering-wireless-sensing-with-mobility-21c4wef1.pdf
- [oficial] https://ct.cswu.me/papers/sigcomm19_rim_paper.pdf
- [oficial] https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/12137396
- [oficial] https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/11054638
- [oficial] https://www.cs.wm.edu/~yma/files/YongsenMa_dissertation_final_November21_2019_stamped.pdf
- [oficial] https://arxiv.org/pdf/2602.14004 (Rethinking RSSI for WiFi Sensing)
- [oficial] https://arxiv.org/html/2508.12614v1 (SISO bistatic sensing pentru ISAC)
- [oficial] https://arxiv.org/pdf/2511.22144v2

## 12. Radar UWB ieftin

- Novelda X4/X4F103 (2021): mișcări sub-milimetrice, respirație, până la 5 m. Trece prin plastic, sticlă și haine. Kit doar pentru „clienți selectați”.
- Novelda, senzor nou (2023): sub 100 µW, respirație până la 10 m.
- IEEE Sensors Journal (arXiv 2504.03772): respirație cu UWB 802.15.4z de serie. Cod și date open-source. Baterie până la 313 zile.
- Infineon: nu am găsit informații.
- Nu am găsit teste prin perete pentru cipurile UWB ieftine.

Linkuri:

- [presă] https://www.cnx-software.com/2021/12/28/novelda-uwb-x4-sensor-can-detect-submillimeter-movements/
- [presă] https://www.cnx-software.com/2023/06/22/novelda-latest-uwb-radar-presence-sensor-consumes-less-than-100-%c2%b5w/
- [oficial] https://arxiv.org/abs/2504.03772v2
- [oficial] https://imec-publications.be/handle/20.500.12860/59847
- [presă] https://www.eenewseurope.com/en/single-chip-uwb-radar-offers-a-scalable-sensor-development-platform/
- [presă] https://www.sensortips.com/development-tools/ulp-proximity-sensor-capable-of-detecting-breathing-motion-at-ten-meters/

## 13. Drone: detecție prin CSI și Remote ID

Idee respinsă, dar sursele rămân utile.

- Dr. Defender (IEEE TIFS 2024): detecția dronelor cu autopilot din CSI, după mișcarea elicelor, fără semnal de la dronă. Textul complet nu este găsit.
- Mesh-Mapper: ESP32-S3; un nucleu prinde Remote ID Wi-Fi, celălalt BLE. Hartă Flask pe Linux.
- SignalSweep: ESP32-C5, decodează ASTM F3411 prin BLE, beacon Wi-Fi și Wi-Fi NAN. Doar recepție.
- opendroneid-core-c: biblioteca de referință; exemplul ESP32 conține și cod de recepție.
- DragonSync: Remote ID → CoT pentru ATAK.

Linkuri:

- [oficial] https://www.aminer.org/pub/65588a2b939a5f4082bf1c4a/dr-defender-proactive-detection-of-autopilot-drones-based-on-csi
- [oficial] https://aminer.org/pub/5b67b45517c44aac1c860e90/unmanned-aerial-vehicle-detection-based-on-channel-state-information
- [oficial] https://arxiv.org/pdf/2111.03760
- [oficial] https://arxiv.org/pdf/2401.14287
- [oficial] https://arxiv.org/pdf/2207.01927
- [oficial] https://pmc.ncbi.nlm.nih.gov/articles/PMC9460464
- [oficial] https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/10735908
- [slab] https://liveinthefuture.org/priorart/wifi-csi-drone-incursion.html
- [presă] https://www.hackster.io/colonelpanic/mesh-mapper-drone-remote-id-mapping-and-mesh-alerts-8e7c61
- [presă] https://circuitdigest.com/news/signalsweep-open-source-ble-and-wi-fi-scanner-on-esp32-c5-that-can-detect-airtags-flock-cameras-and-drones
- [oficial] https://github.com/zingdrones/opendroneid-core-c
- [slab] https://www.jaredwatkins.com/research/drone-detection/open-source/
- [presă] https://www.rtl-sdr.com/tag/remote-id/

## 14. Victime sub dărâmături și triaj

Idee respinsă, dar sursele rămân utile.

- Nu am găsit o lucrare CSI pentru oameni sub dărâmături.
- MDPI Sensors 2022: Wi-Fi FTM și UWB sub dărâmături. Performanța scade din cauza reflexiilor și a atenuării.
- Tehnički Vjesnik 2024: CSI cu router și SVM pe o dronă, pentru oameni într-un incendiu.
- Lifeseeker (Centum), NEC SARDO, UMD: găsesc telefoanele victimelor din dronă.
- DARPA Triage Challenge: finala are loc între 5 și 14 noiembrie 2026, la Disaster City, Texas. Rezultatele nu erau publice pe 12 noiembrie.

Linkuri:

- [oficial] https://www.mdpi.com/1424-8220/22/21/8433
- [oficial] https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9658015/
- [oficial] https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5877370/
- [oficial] https://doaj.org/article/cde03786e01f48728db68f9690c49747
- [slab] https://peerlist.io/leonardo_zanobi/articles/wifidensepose-revolutionary-throughwall-human-tracking
- [slab] https://github.com/ahmed1hisham/BrickThru/blob/main/README.md
- [presă] https://dronelife.com/2020/05/18/search-and-rescue-drones-finding-a-cell-phone-signal-and-a-missing-person/
- [oficial] https://uk.nec.com/en_GB/press/PR/20210324215819_18969.html
- [presă] https://today.umd.edu/disaster-drones-to-the-rescue.md
- [oficial] https://www.darpa.mil/research/challenges/darpa-triage-challenge
- [oficial] https://www.darpa.mil/research/challenges/darpa-triage-challenge/events
- [oficial] https://www.darpa.mil/sites/default/files/attachment/2026-05/darpa-triage-challenge-program-summary.pdf
- [oficial] https://www.darpa.mil/sites/default/files/attachment/2026-10/darpa-triage-challenge-finals-team-operations-guide.pdf
- [oficial] https://www.darpa.mil/news/2025/dart-msai-triumph-darpa-triage-challenge

## 15. Gadgeturi: radar Seeed de 60 GHz

- MR60FDA2 (cădere): cub de 3 × 3 × 3 m, montaj la 2,2–3,0 m înălțime, unghi 100° × 40°. Nu detectează prin sticlă sau lemn subțire.
- MR60BHA2 (respirație și puls): puls până la 1,5 m, prezență statică până la 6 m. Consum 0,5–1,4 W.
- Ambele au XIAO ESP32-C6, ESPHome și Home Assistant. Preț de lansare: 22,90–24,90 USD.
- Utilizare în concept: referință de adevăr în cameră, nu senzor prin perete.

Linkuri:

- [presă] https://electronics-lab.com/seeed-studio-mr60bha2-and-mr60fda2-60ghz-mmwave-sensor-kits-with-xiao-esp32c6-for-fall-breathing-and-heartbeat-detection
- [presă] https://cnx-software.com/2024/10/21/seeed-studio-esp32-c6-60ghz-mmwave-human-fall-detection-and-breathing-heartbeat-detection-sensor-kits/
- [presă] https://www.hackster.io/news/seeed-adds-home-assistant-ready-breathing-fall-detection-sensors-to-its-mmwave-range-c97eeb97b8d9
- [oficial] https://wiki.seeedstudio.com/getting_started_with_mr60fda2_mmwave_kit/
- [oficial] https://new.esphome.io/components/seeed_mr60fda2
- [slab] https://thepihut.com/products/60ghz-mmwave-breathing-and-heartbeat-detection-sensor-mr60bha2
- [slab] https://smarthomescene.com/reviews/seeed-studio-60ghz-mmwave-sensors-review/

## 16. ATAK, CoT și integrarea software

- PyTAK: bibliotecă Python pentru clienți, servere și porți TAK. Trimite CoT XML. Implicit folosește adresa multicast UDP a ATAK.
- FreeTAKServer: primește CoT prin TCP (port 8087) sau TLS (port 8089).
- cot_gateway: transformă detecții (ID, lat/lon, clasă, încredere) în CoT prin PyTAK.
- DragonSync: Remote ID de pe ESP32 → CoT pentru ATAK. Exemplul cel mai apropiat de concept.
- Tipurile CoT urmează MIL-STD-2525. Ramura „b-d” este pentru detecții de senzori. În pagină am folosit `a-u-G` (necunoscut la sol).

Linkuri:

- [oficial] https://pypi.org/project/pytak/5.5.0
- [oficial] https://www.mintlify.com/FreeTAKTeam/FreeTakServer/api/cot/message-format
- [oficial] https://freetakteam.github.io/FreeTAKServer-User-Docs/About/architecture/mil_std_2525/
- [oficial] https://babeloff.github.io/FreeTAKServer-User-Docs/About/architecture/cot_domain
- [oficial] https://github.com/alphafox02/DragonSync
- [oficial] https://github.com/pinztrek/takpak
- [oficial] https://projectqai.github.io/docs/integration/atak
- [slab] https://knogin.com/developers/tactical-awareness-tak-ecosystem
- [slab] https://www.jaredwatkins.com/research/drone-detection/open-source/dragonsync/
- [oficial] https://pypi.org/project/adsbcot/2.1.1 (exemplu: ADS-B → CoT)

## 17. Comunicații mesh: Meshtastic și LoRa

- Plăci Heltec LoRa V3 cu Meshtastic au fost testate în Donbas.
- Voluntari au donat echipamente Meshtastic și goTenna unităților de pe front.
- Un consilier al ministrului ucrainean al apărării spune că Ucraina are nevoie de modemuri radio mesh proprii, rapide.
- Avertisment: unitățile au fost găsite după semnalele lor Wi-Fi, celulare și Bluetooth. Sursa este un articol DEV, deci slabă. Această afirmație susține modul silențios, dar cere o sursă mai bună.
- Meshtastic are AES, dar alt model de amenințare decât radiourile militare.

Linkuri:

- [presă] https://euromaidanpress.com/2026/04/29/ukraine-needs-to-build-its-own-high-speed-mesh-tech-as-china-is-russias-supplier-and-western-modems-are-too-expensive/
- [presă] https://euromaidanpress.com/?p=412760
- [slab] https://dev.to/joshbullock90/atak-over-a-mesh-network-5a8g
- [slab] https://dev.to/joshbullock90/drones-in-combat-applications-5478
- [slab] https://www.recoilweb.com/secure-comms-for-the-concerned-civilian-185780.html
- [slab] https://meshtastic.discourse.group/t/using-in-ukraine/5685
- [slab] https://ukraine-war-analytics.com/cyber/mesh-networking-ukraine.html
- [presă] https://www.hackster.io/openelab/meshtastic-lora-mesh-for-off-grid-sensing-and-telemetry-d98eb1
- [oficial] https://sciety.org/articles/activity/10.21203/rs.3.rs-5314157/v1

## 18. Senzori purtabili pentru soldați

- CAPSARII (UE, februarie 2026): textile inteligente, rețea mesh, AI la margine, securitate cibernetică.
- Armata SUA testează ceasuri și inele inteligente (pilot MOMRP / DEVCOM).
- Senzori de stres termic: alarmă cu până la 12 minute înainte.
- Nu am găsit informații despre Equivital.

Linkuri:

- [oficial] https://arxiv.org/abs/2602.08080v1
- [oficial] https://mrdc.health.mil/index.cfm/media/articles/2024/MOMRP_army_war_college_team_up_for_wearables_pilot
- [presă] https://www.technologyreview.com/s/405396/wearable-health-reports/
- [slab] https://www.pulse.bot/defense/news/new-science-on-heat-is-changing-the-future-of-soldiering-535b0fda-a881-4576-a324-5f1a30997b4f

## 19. Biblioteci pentru ilustrații

- GSAP 3.12.5 (cdnjs): timeline-ul misiunii și ScrollTrigger. https://gsap.com/
- Restul paginii folosește SVG, Canvas și CSS, fără alte biblioteci.

## 20. Descoperiri din repo și de pe placă

Acestea sunt fapte măsurate sau citite în repo, nu în web.

| Fapt | Sursă |
|---|---|
| [main.c:36](../../../src/firmware/esp32_csi_node/main/main.c#L36) acceptă doar probe request-uri (`hdr[0] == 0x40`). Nu verifică sursa. | firmware |
| Pachetul UDP are 138 de octeți: antet `<HBbIH` și 64 de perechi (Q, I) din LLTF. Nu conține MAC-ul emițătorului. | firmware |
| Probe-urile pleacă la 6 Mbps (OFDM), 100 pe secundă. La 1 Mbps nu dau CSI. | teste 12 nov 2026 |
| Beacon-urile hotspot-ului sunt 802.11b și nu dau CSI. | teste 9 nov 2026 |
| În mod promiscuu, pe canalul 1, placa a primit aproximativ 400 CSI/s de la un dispozitiv străin. | teste 9 nov 2026 |
| Cu ping la 20 ms, placa dă 50 CSI/s. | teste 10 nov 2026 |
| 52 de subpurtătoare active (k = ±1..26). | teste 12 nov 2026 |
| Detectorul vechi de cădere: `src/csi/fall_detector.py`, stările CALM, MERS, IMPACT, VERIFICARE, ALARMĂ. | git, `HEAD~5` |
