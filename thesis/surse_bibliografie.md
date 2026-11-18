# Bibliografia tezei: fișiere locale și verificare

Data verificării: 11 nov. 2026. Toate fișierele sunt în `docs/Materials/CSI_Sensing/sources-2026-10-21/`.

## Metoda

1. Datele bibliografice din `licenta.bib` au fost comparate cu prima pagină a fișierului local.
2. Aceleași date au fost comparate cu înregistrarea Crossref (`https://api.crossref.org/works/<DOI>`).
3. Fiecare fragment citat în capitolul 4 a fost căutat în textul PDF-ului local: `python3 thesis/verifica_citate.py`. Rezultat (12 nov. 2026, după secțiunea 4.7 și completările din 4.3, 4.4 și 4.6): 70 de fragmente găsite, 0 lipsă.

## Referințele

| Nr. | Cheia | Fișierul local | Verificat pe | Ce s-a corectat |
|---|---|---|---|---|
| [1] | `zhang2015antifall` | `Zhang_Wang_2015_Anti_Fall_CSI_Commodity_WiFi.pdf` | PDF + Crossref | DOI adăugat |
| [2] | `tse2005` | `Tse_Viswanath_2005_Fundamentals_Wireless_Communication/` (14 PDF-uri) | PDF + pagina cărții (web.stanford.edu/~dntse) | ISBN adăugat |
| [3] | `wang2015carm` | `Wang_2015_Understanding_Modeling_WiFi_HAR_CARM.pdf` | PDF + Crossref | numele complet al conferinței; paginile 65–76 confirmate |
| [4] | `halperin2011` | `Halperin_2011_Tool_Release_80211n_CSI.pdf` | PDF + Crossref | pagina 53 și DOI adăugate |
| [5] | `ieee80211a` | `IEEE_1999_Std_802.11a_OFDM_PHY_5GHz.pdf` | PDF + Crossref (ISBN 0-7381-1810-9 identic) | luna aprobării scoasă; DOI adăugat |
| [6] | `espidf517wifi` | `Espressif_ESP-IDF_v5.1.7_WiFi_Driver_2026-11-11.pdf` | pagina web (HTTP 200) + `~/esp/esp-idf/docs/en/api-guides/wifi.rst` | nimic |
| [7] | `chen2016trips` | `Chen_Liu_2016_WiFi_TRIPS_Time_Reversal.pdf` | PDF + Crossref + DBLP | luna și DOI adăugate |
| [8] | `zeng2019farsense` | `Zeng_2019_FarSense_Respiration_CSI_Ratio.pdf` | PDF + Crossref | nimic |
| [9] | `chen2018trbreath` | `Chen_Liu_2018_TR_BREATH_Time_Reversal.pdf` | PDF + Crossref | volumul 65, nr. 3, pp. 489–501, martie 2018 adăugate |
| [10] | `wang2020phasebeat` | `Wang_Mao_2020_PhaseBeat_Vital_Signs.pdf` | PDF + Crossref (DOI 10.1145/3377165) | adăugată la 12 nov. 2026, pentru secțiunea 4.6.1 |

## Diferențe între fișierul local și versiunea publicată

- [1] Fișierul local este versiunea corectată a autorilor (o referință lipsea în original). Titlul, autorii și paginile sunt aceleași.
- [8] Fișierul local este versiunea arXiv (`arXiv:1907.03994v3`). Antetul paginilor (121:1–121:26) este cel din revistă.
- [9] Fișierul local este versiunea acceptată („accepted for publication in a future issue”). Datele publicării vin din Crossref.
- [6] Fișierul local este pagina web salvată ca PDF la 11 nov. 2026. Fragmentele citate sunt identice cu `wifi.rst` din ESP-IDF v5.1.7 instalat.

## Alte fișiere descărcate

- `docs/Materials/UTCN_licenta_2026/templateLaTeX-Rom-2026.zip`: șablonul oficial, de pe cs.utcluj.ro.
- `docs/Materials/UTCN_licenta_2026/MetodologieLicenta_Iulie2026-Calculatoare.pdf`: metodologia, de pe cs.utcluj.ro.

## Legătura cu celelalte bibliografii

`docs/Materials/references_master.bib` și `CSI_Sensing/references_csi.bib` nu conțin niciuna dintre aceste 10 referințe. `licenta.bib` este singura sursă pentru ele.
