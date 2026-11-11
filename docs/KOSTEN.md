# Kosten POC – PCB rev 0.2, offerte 11 november 2026

Gebaseerd op de echte JLCPCB-offerte (winkelwagen, 11 november 2026), bijgewerkt voor de LED-keuze
van dezelfde dag (status geel i.p.v. blauw). Tarieven: JLCPCB-helpartikel "PCB assembly price" (bijgewerkt 22 oktober 2026).

## Gekozen optie
- 4-laags bord, 94 × 70 mm, 1,6 mm, groen, HASL met lood; **5 stuks, alle 5 geassembleerd**.
- **Economic PCBA**, alleen bovenkant: JLCPCB plaatst **27 unieke SMD-onderdelen** (57 per bord,
  179 soldeerpunten), waarvan **8 extended**. Ook U1 (USB-ESD) en de Qwiic-connectoren J5/J6 zitten erbij.
- LED's: rood = laden, **groen = vol**, **geel = status**. Groen is sinds 2026 extended (€2,76 per order);
  geel is preferred (geen toeslag) en minder fel dan blauw. R5 = 4k7, zodat groen even fel is als rood.
- Voorraad en klasse op 11 november gecontroleerd met `generator/jlc_check.py`: alle 27 regels leverbaar.
- Zelf solderen: de ESP-module en alle through-hole-onderdelen (klemmen, headers, NTC-connector, D5, accuhouder).

## A. JLCPCB-bestelling (1 zending)
| Post | Offerte | Na LED-keuze |
|---|---|---|
| PCB, 5 stuks, 4 lagen | €7,16 | €7,16 |
| Setup Economic PCBA | €7,37 | €7,37 |
| Stencil | €1,39 | €1,39 |
| Onderdelen (27 regels, 5 borden) | €10,49 | ≈ €10,50 |
| Extended-toeslag | €24,88 (9 × €2,76) | **€22,11 (8 × €2,76)** |
| SMT-assemblage | €1,44 | €1,44 |
| Stikstof-reflow | €0,81 | €0,81 |
| **Subtotaal bestelling** | **€53,55** | **≈ €50,80** |
| Verzending (schatting in winkelwagen) | €15,31 | €15,31 |
| Kortingsbon | −€8,95 | −€8,95 |
| **Winkelwagen** | **€59,91** | **≈ €57,15** |
| Btw 21% (IOSS, bij afrekenen) | | ≈ €12 |
| EU-douane sinds juli 2026 | | ≈ €20 – 25 (€3 douanerecht per HS-code + €2 afhandeling per regel + vervoerderskosten) |
| **Totaal geleverd** | | **≈ €90 – 95** |

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
**≈ €125 – 150 voor 2 werkende borden incl. sensoren en accu's** (zonder displays), plus 3 reserveborden.

## Waarom deze keuze
| Alternatief | Verschil | Oordeel |
|---|---|---|
| Wit (basic) i.p.v. groen voor 'vol' | €2,76 goedkoper per order | groen is duidelijker; niet de moeite waard |
| Qwiic J5/J6 niet laten plaatsen | ≈ €4,70 goedkoper | later zelf solderen (1 mm steek); alleen nodig voor uitbreidingssensoren |
| U1 weglaten | – | kan niet: D+ en D- lopen door de chip heen |
| Economic, 2 i.p.v. 5 borden assembleren | ≈ $9 goedkoper | reserveborden zonder SMD zijn weinig waard |
| Standard PCBA | ≈ $44 duurder | pas zinvol voor een eindversie of 10+ borden |
| Alles zelf solderen | stencil + onderdelen + veel tijd | TP4056, DW01A, USB-C en 0603 met de hand: geen besparing |

## Waar zit het geld?
1. **Vaste kosten per zending** (verzending + btw + douane ≈ €40–55): bestel alles in één JLCPCB-order
   en koop de losse onderdelen bij één leverancier.
2. **Extended onderdelen** (€22,11): elk uniek extended onderdeel kost eenmalig €2,76 ($3,07) per order.
   Voor de overige 7 (alles behalve de groene LED) bestaat bij JLCPCB geen basic/preferred-variant met dezelfde behuizing en pinout
   (gecontroleerd 11 november 2026); goedkoper kan alleen door onderdelen weg te laten of het bord aan te passen.
3. Het bord zelf en de geplaatste onderdelen zijn per stuk goedkoop.

## Bronnen
- JLCPCB PCB assembly price: https://jlcpcb.com/help/article/pcb-assembly-price
- JLCPCB PCBA-capabilities (Economic: 1,6 mm groen, HASL of ENIG, 2–50 stuks): https://jlcpcb.com/capabilities/pcb-assembly-capabilities
- JLCPCB EU-douanereform juli 2026: https://jlcpcb.com/help/article/eu-customs-reform-faq
