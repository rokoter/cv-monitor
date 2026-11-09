# CV-monitor

Herbruikbaar ESP32-S3-sensorbord voor Home Assistant (ESPHome). Eerste toepassing: aanvoer- en
retourtemperatuur van de CV-installatie meten met 2× DS18B20. Voeding via USB-C met een 18650 als
UPS-backup. Uitbreidbaar via Qwiic (I²C), een uitbreidingsheader en aansluitingen voor OLED en e-ink.

Leertraject: Koen stuurt en controleert, Claude voert uit.

## Status
| Stap | Status |
|------|--------|
| 1. Schema (KiCad) | rev 0.4 – in review |
| 2. PCB-layout | – |
| 3. JLCPCB productie (Gerber, BOM, CPL) | – |
| 4. Firmware (ESPHome) | – |
| 5. Behuizing (FreeCAD) | – |

## Mappen
| Map | Inhoud |
|-----|--------|
| `hardware/cv_monitor/` | KiCad-project (open `cv_monitor.kicad_pro`); details in de README daar |
| `generator/` | Scripts die schema en bibliotheek opbouwen en controleren (`design.py` = het ontwerp in tekst) |
| `docs/` | Schema-PDF en uitleg (draw.io) |
| `firmware/` | ESPHome-configuratie (volgt) |
| `enclosure/` | FreeCAD-behuizing (volgt) |

## Opnieuw bouwen en controleren
```bash
./generator/build.sh
```
Genereert het schema uit `generator/design.py`, laat KiCad de netlist exporteren en vergelijkt die
pin voor pin met de bedoeling (kortsluitingen, losse pinnen, voeding). Daarnaast: ERC in KiCad zelf.

## Werkwijze
- Elke ontwerpwijziging is een eigen commit; goedgekeurde stappen krijgen een tag (bijv. `schema-v1.0`).
- Wijzig het schema bij voorkeur via `design.py` + `build.sh`, zodat de controle blijft kloppen.
  Handmatige aanpassingen in KiCad kunnen ook, maar worden bij een volgende generatie overschreven.
