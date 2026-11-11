# Productiebestanden PCB rev 0.2 – JLCPCB

Gemaakt op 10 november 2026, onderdelen bijgewerkt op 11 november uit het gerouteerde bord (DRC 0/0). Keuze: **Economic PCBA**, JLCPCB plaatst
alle SMD-onderdelen aan de bovenkant; de ESP-module en alle through-hole-onderdelen soldeer je zelf.

| Bestand | Inhoud | Uploaden bij |
|---|---|---|
| `cv_monitor_rev0.2_gerber.zip` | 4 koperlagen, masker, pasta, silkscreen, bordrand + boorbestanden (PTH/NPTH) | PCB – "Add gerber file" |
| `cv_monitor_rev0.2_bom.csv` | 27 regels, 57 onderdelen, met LCSC-nummers | PCB Assembly – BOM |
| `cv_monitor_rev0.2_cpl.csv` | 57 posities (mm, oorsprong linksonder), draaiing voor JLCPCB | PCB Assembly – CPL |

Gecontroleerd met gerbv (onafhankelijk van KiCad): `docs/gerber_controle_boven_rev0.2.png` en
`docs/gerber_controle_onder_rev0.2.png` (onderkant gespiegeld, zoals je hem ziet als je het bord omdraait).

## 1. PCB-instellingen
Upload de zip op jlcpcb.com. Afmetingen en lagen worden herkend; de rest zo instellen:

| Instelling | Kiezen | Waarom |
|---|---|---|
| Base material | FR-4 | |
| Layers | 4 | wordt herkend |
| Dimensions | 94 × 70 mm | wordt herkend |
| PCB Qty | 5 | minimum |
| Delivery format | Single PCB | |
| PCB thickness | 1,6 mm | |
| PCB color | Green | bij 1,6 mm de kleur met de meeste Economic-opties |
| Silkscreen | White | |
| Surface finish | HASL (with lead) of LeadFree HASL | met lood is het goedkoopst en soldeert makkelijker met de hand; JLCPCB gebruikt dan ook loodhoudende soldeerpasta |
| Outer copper weight | 1 oz | |
| Inner copper weight | 0,5 oz | standaard |
| Specify stackup | standaard (JLC04161H-7628) | Economic PCBA ondersteunt alleen de standaard-opbouw |
| Impedance control | niet nodig | USB full-speed (12 Mbit/s) is daar niet gevoelig voor |
| Via covering | Tented | standaard |
| Mark on PCB | niets toevoegen | JLCPCB drukt sinds mei 2026 geen ordernummer meer; er staat dus ook geen "JLCJLCJLCJLC" op het bord |

Overige opties op de standaardwaarde laten.

## 2. PCB Assembly
Zet **PCB Assembly** aan:

| Instelling | Kiezen |
|---|---|
| PCBA type | **Economic** |
| Assembly side | **Top side** |
| PCBA qty | 5 (minimaal 2; elk bord minder scheelt ongeveer $3) |
| Confirm parts placement | **Yes** (een engineer van JLCPCB controleert de plaatsing; jij bevestigt daarna) |
| Overige (tooling holes, verpakking) | standaard laten |

Klik op *Next*, upload de BOM en de CPL en kies *Process BOM & CPL*.

## 3. BOM controleren
- Alle **27 regels** moeten een gekoppeld onderdeel hebben (vinkje aan) met voorraad voor 5 borden.
  Staat er "shortfall" of "no stock"? Stuur een screenshot, dan zoek ik een vervanger en pas ik `design.py` aan.
- Verwacht **9 extended** onderdelen: J1 USB-C, F1 PTC, U1 USBLC6, U3 DW01A, U4 AP2112K, Q2 AO8810, J5/J6 Qwiic
  en de groene en blauwe LED (D3, D4). U2 TP4056 is "preferred" (geen toeslag).
- Op 11 november 2026 was alles op voorraad (`generator/jlc_check.py`). Tussen controle en bestelling kan dat
  veranderen; daarom deze stap toch even nalopen.
- De zelf te solderen onderdelen staan niet in de bestanden, dus JLCPCB meldt daar niets over.

## 4. Plaatsingspreview – het belangrijkste stuk
JLCPCB legt zijn eigen onderdeelmodel over onze pads. Weerstanden en condensatoren mogen 180° gedraaid zitten;
deze onderdelen **niet**. Kijk per onderdeel of de stand overeenkomt met de silkscreen en stuur screenshots,
ook als het goed lijkt:

| Ref | Onderdeel | Waar op letten |
|---|---|---|
| J1 | USB-C | opening naar de **linker bordrand**, de vier schildpootjes in de vier gaten |
| J5, J6 | Qwiic (JST-SH liggend) | opening naar de **onderrand**, de twee bevestigingslippen op de grote pads |
| U1 | USBLC6-2SC6 (SOT-23-6) | pin 1 bij het driehoekje in de silkscreen |
| U2 | TP4056 (SOIC-8 met koelvlak) | pin 1 bij het driehoekje |
| U3 | DW01A (SOT-23-6) | pin 1 bij het driehoekje |
| U4 | AP2112K-3.3 (SOT-23-5) | de kant met 3 pootjes op de 3 pads |
| Q1, Q3 | AO3401A (SOT-23) | het losse pootje (drain) op de losse pad |
| Q2 | AO8810 (TSSOP-8) | pin 1 bij het driehoekje |
| D1 | SS34 (SMA) | kathodestreep aan de kant van de streep in de silkscreen |
| D6 | 1N4148W (SOD-123) | kathodestreep aan de kant van de streep in de silkscreen |
| D2, D3, D4 | LED's 0603 | kathode aan de gemarkeerde kant |
| SW1–SW3 | drukknoppen | vier pootjes op de vier pads, niet 90° verdraaid: dan zit de knop altijd "ingedrukt" (RESET houdt de ESP dan in reset) |

**Eerste preview (11 november 2026):** alles goed behalve U1, U3 en U4 (SOT-23-6/-5), die stonden een kwartslag
gedraaid. Gecorrigeerd in de CPL (90° / 270° / 270°). Na opnieuw uploaden van de CPL alleen die drie nog nalopen:
pin-1-punt bij ons driehoekje, en bij U4 de 3 pootjes links.

Klopt er iets niet: niet zelf in de JLCPCB-tool draaien, maar mij laten weten. Dan pas ik de draaiing in
`generator/make_production.py` aan, zodat ook een nabestelling klopt.

## 5. Bestellen en daarna
- Vergelijk het totaal met `docs/KOSTEN.md`.
- Na de bestelling doet JLCPCB een DFM-controle en controleert een engineer de plaatsing. Je krijgt een
  bevestigingsverzoek in je order; productie wacht tot je op *Confirm* klikt. Bij twijfel: screenshot sturen.

## 6. Zelf solderen na levering
Van laag naar hoog, dan zit niets in de weg:

| Volgorde | Ref | Onderdeel | Let op |
|---|---|---|---|
| 1 | U5 | ESP32-S3-WROOM-1-N8 | Uitlijnen, twee hoeken vastzetten, dan de randpads met veel flux. Het grote GND-vlak eronder soldeer je **van de achterkant** via het rooster van via's (bout erop, tin erin tot het doorloopt). Daarna 3V3–GND doormeten op sluiting. |
| 2 | J9 | JST-PH 2-polig (NTC) | bovenkant; de NTC-draad gaat door de sleuf naar de accu |
| 3 | J7, J4, J8 | pinheaders 1×4, 1×10, 1×8 | alleen als je OLED, uitbreiding of e-ink gebruikt |
| 4 | J2, J3 | schroefklemmen 3-polig 3,5 mm | opening naar de rechter bordrand |
| 5 | D5 | rode LED 3 mm | **onderkant**, naast de accuhouder; lange poot (anode) in het gat bij de **+** |
| 6 | BT1 | accuhouder MPD BK-18650-PC2 | onderkant, als laatste; pootjes aan de bovenkant solderen |

## 7. Eerste keer aanzetten
1. Zonder accu en zonder USB: weerstand meten tussen VBUS–GND, VSYS–GND en 3V3–GND (de rij testpunten
   VBUS, VSYS, BAT+, 3V3, GND links op het bord). Geen van drieën mag ongeveer 0 Ω zijn.
2. USB-C aan een lader van minimaal 1 A, nog zonder accu: op 3V3 moet 3,3 V staan.
3. Accu erin, met de **+** zoals op het bord. D5 moet uit blijven (brandt alleen als de accu verkeerd om zit).
   Eén keer USB aansluiten activeert de accubeveiliging; de rode LED (laden) gaat aan.

## Opnieuw maken
Na een wijziging in `generator/design.py` (bijv. een ander LCSC-nummer), zonder opnieuw te routeren:
```bash
./generator/build.sh                                                   # schema + BOM-overzicht
/usr/bin/python3 generator/sync_attrs.py hardware/cv_monitor/cv_monitor.kicad_pcb
/usr/bin/python3 generator/drc.py hardware/cv_monitor/cv_monitor.kicad_pcb
/usr/bin/python3 generator/make_production.py hardware/cv_monitor/cv_monitor.kicad_pcb rev0.2
python3 -I generator/jlc_check.py hardware/cv_monitor/production/cv_monitor_rev0.2_bom.csv   # voorraad + klasse
```

Bronnen: [JLCPCB PCBA-capabilities](https://jlcpcb.com/capabilities/pcb-assembly-capabilities),
[How to mark on PCB](https://jlcpcb.com/help/article/How-to-mark-on-PCB),
[PCB assembly price](https://jlcpcb.com/help/article/pcb-assembly-price).
