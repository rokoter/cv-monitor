# Kosteninschatting POC – PCB rev 0.2, 11 november 2026

De productiebestanden zijn klaar (`hardware/cv_monitor/production/`). De definitieve prijs volgt uit de
JLCPCB-offerte na het uploaden; dit is de inschatting vooraf. Bedragen in USD zoals JLCPCB rekent,
euro's afgerond (koers ~0,9, niet geverifieerd). Tarieven: JLCPCB-helpartikel "PCB assembly price"
(bijgewerkt 22 oktober 2026).

## Gekozen optie
- 4-laags bord, 94 × 70 mm, 1,6 mm, groen, HASL; **5 stuks, alle 5 geassembleerd**.
- **Economic PCBA**, alleen bovenkant: JLCPCB plaatst **27 unieke SMD-onderdelen** (57 per bord,
  179 soldeerpunten), waarvan **9 extended**. Ook U1 (USB-ESD) en de Qwiic-connectoren J5/J6 zitten erbij.
- Voorraad en klasse op 11 november gecontroleerd met `generator/jlc_check.py`: alle 27 regels leverbaar.
- Zelf solderen: de ESP-module en alle through-hole-onderdelen (klemmen, headers, NTC-connector, D5, accuhouder).

## A. JLCPCB-bestelling (1 zending)
| Post | Bedrag | Toelichting |
|---|---|---|
| PCB, 5 stuks, 4 lagen | $2 – 15 | exacte prijs volgt uit de offerte |
| Setup Economic PCBA | $8,18 | eenmalig per order |
| Stencil | $1,53 | |
| Confirm parts placement | $0,45 | engineer controleert de plaatsing vóór productie |
| Extended onderdelen | $27,63 | 9 × $3,07; TP4056 is "preferred" en dus zonder toeslag |
| Plaatsen (179 punten × 5 borden) | ≈ $1,50 | ~$0,0016 per soldeerpunt |
| Onderdelen voor 5 borden | $8 – 15 | incl. minimale afnamehoeveelheden |
| **Subtotaal JLCPCB** | **$49 – 69** | |
| Verzending naar NL | $15 – 25 | afhankelijk van de vervoerder |
| Btw 21% (IOSS, bij afrekenen) | ≈ €12 – 18 | |
| EU-douane sinds juli 2026 | ≈ €20 – 25 | €3 tijdelijk douanerecht per HS-code + €2 afhandeling per regel + vervoerderskosten (min. €15–16,50) |
| **Totaal geleverd** | **≈ €90 – 130** | |

## B. Zelf aan te schaffen (voor 2 werkende borden)
| Onderdeel | Aantal | Indicatie |
|---|---|---|
| ESP32-S3-WROOM-1-N8 | 2 | €10 – 14 |
| 18650-houder MPD BK-18650-PC2 | 2 | €2 – 4 |
| 18650-cel (merk, zonder beveiligingsprint) | 2 | €10 – 16 (of eigen voorraad) |
| DS18B20 waterdichte probe | 4 | €8 – 12 |
| NTC 10k B3950 probe + JST-PH 2-polig | 2 | €2 – 4 |
| Schroefklemmen 3,5 mm 3-polig, pinheaders, 3 mm rode LED | – | €3 – 5 |
| **Subtotaal** | | **≈ €35 – 55** |
| Optioneel: OLED 0,96" SSD1306 I²C (GND-VCC-SCL-SDA) | 1 | €4 – 8 |
| Optioneel: Waveshare 2,9" e-Paper V2 (8-pins) | 1 | €15 – 25 |

De andere 3 borden zijn ook geassembleerd: later alleen een ESP-module en de through-hole-onderdelen erbij.

## Totaal
**≈ €125 – 185 voor 2 werkende borden incl. sensoren en accu's** (zonder displays), plus 3 reserveborden.

## Waarom deze keuze
| Alternatief | Verschil | Oordeel |
|---|---|---|
| Groene/blauwe LED vervangen door wit (basic) en geel (preferred) | ≈ $6 goedkoper | groen = vol en blauw = status zijn duidelijker |
| Economic, maar U1 en J5/J6 zelf solderen | ≈ $6 goedkoper | fijn-pitch SMD met de hand; niet de moeite waard |
| Economic, 2 i.p.v. 5 borden assembleren | ≈ $9 goedkoper | reserveborden zonder SMD zijn weinig waard |
| Standard PCBA | ≈ $44 duurder | pas zinvol voor een eindversie of 10+ borden |
| Alles zelf solderen | stencil + onderdelen + veel tijd | TP4056, DW01A, USB-C en 0603 met de hand: geen besparing |

## Waar zit het geld?
1. **Vaste kosten per zending** (verzending + btw + douane ≈ €40–55): bestel alles in één JLCPCB-order
   en koop de losse onderdelen bij één leverancier.
2. **Extended onderdelen** ($27,63): elk uniek extended onderdeel kost eenmalig $3,07 per order.
   Sinds 2026 zijn groene en blauwe 0603-LED's geen basic-onderdelen meer bij JLCPCB.
3. Het bord zelf en de geplaatste onderdelen zijn per stuk goedkoop.

## Bronnen
- JLCPCB PCB assembly price: https://jlcpcb.com/help/article/pcb-assembly-price
- JLCPCB PCBA-capabilities (Economic: 1,6 mm groen, HASL of ENIG, 2–50 stuks): https://jlcpcb.com/capabilities/pcb-assembly-capabilities
- JLCPCB EU-douanereform juli 2026: https://jlcpcb.com/help/article/eu-customs-reform-faq
