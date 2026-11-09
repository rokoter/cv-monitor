# Kosteninschatting POC (rev 0.6) – 9 november 2026

Inschatting vóór de PCB-layout. De definitieve prijs volgt uit de JLCPCB-offerte na het uploaden van
Gerber/BOM/CPL. Bedragen in USD zoals JLCPCB rekent; euro's afgerond (koers ~0,9, niet geverifieerd).

## Aannames
- 2-laags bord, maximaal 100 × 100 mm, 1,6 mm, groen, HASL.
- 5 PCB's, waarvan **2 geassembleerd** (Economic PCBA, minimum is 2).
- JLCPCB plaatst 25 unieke SMD-onderdelen (~150 soldeerpunten per bord), waarvan 5–6 extended
  (TP4056 is mogelijk "preferred" en dan gratis). Zie `BOM_JLCPCB.md`.
- ESP-module, accuhouder, klemmen, headers en connectoren soldeer je zelf.

## A. JLCPCB-bestelling (1 zending)
| Post | Bedrag | Toelichting |
|---|---|---|
| PCB, 5 stuks | $2 – 5 | 2-laags ≤ 100 × 100 mm |
| Setup Economic PCBA | $8,18 | eenmalig per order |
| Stencil | $1,50 | |
| Extended feeders | $15 – 18 | 5–6 × $3,07 |
| Plaatsen (~150 punten × 2 borden) | < $1 | $0,0016 per soldeerpunt |
| Onderdelen voor 2 borden | $4 – 7 | incl. minimale afnamehoeveelheden |
| **Subtotaal JLCPCB** | **$31 – 40** | |
| Verzending naar NL | $15 – 25 | afhankelijk van de vervoerder |
| Btw 21% (IOSS, bij afrekenen) | ≈ €9 – 12 | |
| EU-douane sinds juli 2026 | ≈ €20 – 25 | €3 tijdelijk douanerecht per HS-code + €2 afhandeling per regel + vervoerderskosten (min. €15–16,50) |
| **Totaal geleverd** | **≈ €70 – 95** | |

Extra geassembleerd bord: ongeveer $2–3 per stuk (alleen onderdelen en plaatsing). Van 2 naar 5
geassembleerde borden kost dus ongeveer $6–9 extra.

## B. Zelf aan te schaffen (voor 2 borden)
| Onderdeel | Aantal | Indicatie |
|---|---|---|
| ESP32-S3-WROOM-1-N8 | 2 | €10 – 14 |
| 18650-houder THT | 2 | €2 – 4 |
| 18650-cel (merk, zonder beveiligingsprint) | 2 | €10 – 16 (of eigen voorraad) |
| DS18B20 waterdichte probe | 4 | €8 – 12 |
| NTC 10k B3950 probe + JST-PH 2-polig | 2 | €2 – 4 |
| Schroefklemmen 3,5 mm 3-polig, pin-headers | – | €3 – 5 |
| **Subtotaal** | | **≈ €35 – 55** |
| Optioneel: OLED 1,3" I²C | 1 | €4 – 8 |
| Optioneel: e-ink 2,9" SPI-module | 1 | €15 – 25 |

## Totaal
**≈ €105 – 150 voor 2 werkende borden incl. sensoren en accu's** (zonder displays).

## Waar zit het geld?
1. **Vaste kosten per zending** (verzending + btw + douane ≈ €40–55): bestel alles in één JLCPCB-order
   en koop de losse onderdelen bij één leverancier.
2. **Extended feeders** (≈ $15–18): al geminimaliseerd; verder omlaag alleen door veiligheid in te leveren.
3. Het bord zelf en de geplaatste onderdelen zijn per stuk goedkoop.

## Bronnen
- JLCPCB PCB assembly price: https://jlcpcb.com/help/article/pcb-assembly-price
- JLCPCB prototype assembly: https://jlcpcb.com/solutions/pcb-prototype-assembly
- JLCPCB EU-douanereform juli 2026: https://jlcpcb.com/help/article/eu-customs-reform-faq
