# CV temperatuurmonitor – stap 1: schema (rev 0.7)

Herbruikbaar ESP32-S3-sensorbord: meet aanvoer- en retourtemperatuur van de CV met 2× DS18B20,
heeft een 18650 als UPS-backup, laadt/werkt via USB-C en heeft aansluitingen voor Qwiic-modules,
een OLED (I²C) en een e-ink-display (SPI).

## Openen
Pak de map uit en open `cv_monitor.kicad_pro` in KiCad (7, 8 of 9). De projectbibliotheken
(`cv_monitor.kicad_sym`, `cv_monitor.pretty`) worden via `sym-lib-table`/`fp-lib-table` automatisch geladen.
Gemaakt in KiCad 7-formaat; KiCad 8/9 vraagt bij opslaan om te converteren – dat is prima.

## Blokken
| # | Blok | Kern |
|---|------|------|
| 1 | USB-C | 1,1 A PTC-zekering, 5,1k CC-weerstanden, USBLC6 ESD op D+/D- (native USB) |
| 2 | Lader | TP4056, 600 mA (R3 = 2k), rode/groene LED, optionele NTC op J9 (JP1 doorsnijden) |
| 3 | Power-path | SS34 + AO3401A: USB voedt systeem, accu neemt naadloos over; AP2112K-3.3 LDO |
| 4 | Accu | 18650 + ompoolbeveiliging (Q3) + fout-LED D5 + DW01A + AO8810 (8205A-type dubbele MOSFET; onder-/overspanning, overstroom) |
| 5 | ESP32-S3-WROOM-1-N8 | 8 MB flash, alle GPIO's op het symbool |
| 6 | Metingen | VBAT, USB aanwezig, 2 sensorpoorten (4,7k pull-up, 100R serie) |
| 7 | Bediening | RESET, BOOT, STATUS-knop, status-LED, uitbreidingsheader J4 (DNP) |
| 8 | Qwiic | 2× JST-SH, I²C met 4,7k pull-ups |
| 9 | Displays | J8 e-ink (SPI, Waveshare-volgorde), J7 OLED (I²C) – beide DNP |
| – | Testpunten | TP1–TP5: VBUS, VSYS, BAT+, 3V3, GND (alleen koperpads) |

## GPIO-overzicht (ESP32-S3)
| GPIO | Functie | GPIO | Functie |
|------|---------|------|---------|
| 0 | BOOT-knop | 13 | e-ink DC |
| 1 | VBAT meting (ADC1) | 14 | e-ink RST |
| 2 | USB aanwezig (ADC1) | 15 | STATUS-knop |
| 3 | vrij (strapping) | 16 | status-LED |
| 4 | Sensor 1 (aanvoer) | 17/18 | uitbreiding J4 |
| 5 | Sensor 2 (retour) | 19/20 | USB D-/D+ |
| 6/7 | uitbreiding J4 (ADC1) | 21 | e-ink BUSY |
| 8 | I²C SDA (Qwiic + OLED) | 43/44 | UART TX/RX (J4) |
| 9 | I²C SCL (Qwiic + OLED) | 45/46 | vrij (strapping) |
| 10 | e-ink CS | overige | vrij (X op schema) |
| 11 | e-ink DIN (MOSI) | | |
| 12 | e-ink CLK | | |

## Controle door jou
1. Open het schema en draai **Inspect → Electrical Rules Checker**. Verwacht: 0 fouten.
2. Loop elk blok na met de notities op het blad.
3. LCSC-nummers staan als veld `LCSC` per onderdeel; die worden in de BOM-stap opnieuw gecontroleerd.

## Gebruik / aandachtspunten
- Voeding via een USB-lader van minimaal 1 A (laden 0,6 A + systeem); een pc-poort levert te weinig.
- Na het plaatsen van de accu één keer USB aansluiten: dan activeert de DW01A de accu-uitgang.
- Accuhouder: MPD BK-18650-PC2 (de footprint past alleen op deze houder).
- Accu-NTC (optioneel): stekker in J9 aan de bovenkant, de draad door de sleuf (4 × 7 mm) eronder naar
  de onderkant en de NTC met kaptontape midden op de cel. Bij gebruik van een NTC: JP1 doorsnijden.
  De sleuf is groot genoeg om ook een JST-PH-stekkertje in de lengte door te steken.

## Productie
Gerber, BOM, CPL en de bestelchecklist voor JLCPCB: `production/README.md`.
Gekozen: accuhouder MPD BK-18650-PC2, schroefklemmen 3,5 mm; J7/J8 volgen de pinvolgorde van een
0,96" SSD1306-OLED (GND-VCC-SCL-SDA) en een Waveshare 2,9" e-Paper V2 (8-pins).

## Documentatie
- `../../docs/accubeveiliging_DW01A_FS8205A.drawio`: uitleg hoe de accubeveiliging werkt (openen op app.diagrams.net).
