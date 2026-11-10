# CV-monitor

Herbruikbaar ESP32-S3-sensorbord voor Home Assistant (ESPHome). Eerste toepassing: aanvoer- en
retourtemperatuur van de CV-installatie meten met 2× DS18B20. Voeding via USB-C met een 18650 als
UPS-backup. Uitbreidbaar via Qwiic (I²C), een uitbreidingsheader en aansluitingen voor OLED en e-ink.

Leertraject: Koen stuurt en controleert, Claude voert uit.

## Status
| Stap | Status |
|------|--------|
| 1. Schema (KiCad) | rev 0.7 – gereviewd; POC-BOM voor JLCPCB Economic, zie `docs/BOM_JLCPCB.md` |
| 2. PCB-layout | rev 0.2, 4 lagen: plaatsing goedgekeurd, eerste routing (Freerouting) in review – `docs/pcb_routing_*_rev0.2.png`, 3D: `docs/pcb_3d_*_rev0.2.png` |
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

## PCB opnieuw genereren: plaatsing + routing
```bash
P=hardware/cv_monitor/cv_monitor
kicad-cli sch export netlist -o /tmp/cv_monitor.net $P.kicad_sch
/usr/bin/python3 generator/make_pcb.py /tmp/cv_monitor.net $P.kicad_pcb      # plaatsing + silkscreen
/usr/bin/python3 generator/route.py prep $P.kicad_pcb $P.dsn                 # vlakken, keepouts, fanout, DSN
xvfb-run -a java -jar freerouting.jar -de $P.dsn -dr generator/freerouting.rules -do $P.ses -mp 80 -mt 1
/usr/bin/python3 generator/route.py import $P.kicad_pcb $P.ses               # sporen + GND-vulling
/usr/bin/python3 generator/drc.py $P.kicad_pcb                               # moet 0 / 0 geven
/usr/bin/python3 generator/route_report.py $P.kicad_pcb                      # lengtes, breedtes, controles
```
- Plaatsing: `generator/placement.py`; ontwerpregels en netklassen: `generator/rules.py`.
- Lagen: F.Cu signaal + GND-vulling | In1 GND-vlak | In2 3V3-vlak | B.Cu signaal + GND-vulling.
- Netklassen: standaard 0,2 mm (0,15 mm vrij), 5V/VSYS/accu 0,8 mm, USB-ingang 0,5 mm, B− 0,4 mm,
  GND/3V3 0,4 mm, USB D+/D− als differentieel paar 0,25/0,15 mm (~90 Ω, schatting); via's 0,6/0,3 mm
  (vermogen 0,8/0,4 mm).
- USB: vast voorgerouteerd (`fanout.usb_preroute`): USB-C → ESD-chip U1 (180° gedraaid, zodat D−/D+
  zonder kruising doorlopen) → paar over de onderkant → ESP-pin 13/14; ~79 mm, lengteverschil < 0,5 mm.
- `route.py prep` geeft elke SMD-pad op GND/3V3 een eigen via naar het vlak (`generator/fanout.py`),
  legt de dubbele USB-C-datapinnen vast en houdt de antennezone (alle lagen) en de bovenlaag onder
  de ESP-module vrij van sporen. Freerouting (v1.9.0, open source) routeert de rest.
- Koperlagen als plaatje: `generator/render_layers.sh $P.kicad_pcb docs rev0.2`.

3D: alle footprints staan in de projectbibliotheek `cv_monitor.pretty` en de 3D-modellen (STEP) in
`hardware/cv_monitor/3dmodels` (zie de README daar). In KiCad: **Beeld → 3D-viewer** (Alt+3).
Bord met onderdelen: 94 × 70 × 29,9 mm (19,1 mm onder het bord door accuhouder + cel, 9,3 mm erboven).
Snelle preview zonder KiCad: `kicad-cli pcb export step` en `generator/render_3d.py` →
`docs/pcb_3d_boven_rev0.2.png` en `docs/pcb_3d_onder_rev0.2.png`.

Plaatsingsafspraken (worden door `drc.py` mee gecontroleerd):
- alle R's, C's, diodes en LED's horizontaal (0° of 180°), kleine onderdelen in nette rijen/kolommen;
- alle silkscreentekst horizontaal, leesbaar vanuit één kant (boven: van voren, onder: met het bord omgedraaid);
- referentie bij voorkeur recht boven/onder/links/rechts van het eigen onderdeel, binnen de bordrand;
- pinnamen van headers en klemmen op de bovenkant (waar je aansluit), één naam per regel links van de pin;
- polariteit (+) bij de accu en bij de accu-omgekeerd-LED, op boven- en onderkant;
- achterkant: blokschema van de werking (`generator/back_diagram.py`), titel bovenaan tussen de montagegaten;
- geen THT-pin door een onderdeel aan de andere kant (accuhouder).

## Opnieuw bouwen en controleren
```bash
./generator/build.sh
```
Genereert het schema uit `generator/design.py`, laat KiCad de netlist exporteren en vergelijkt die
pin voor pin met de bedoeling (kortsluitingen, losse pinnen, voeding). Daarnaast: ERC in KiCad zelf.

## KiCad-versie
De bestanden worden gemaakt met **KiCad 7.0** (het formaat dat de generator schrijft). Openen, bekijken
en ERC draaien kan prima in KiCad 8, 9 of 10. **Sla ze in een nieuwere versie niet op over de repo-bestanden**:
KiCad zet ze dan om naar het nieuwe formaat, dat KiCad 7 niet meer kan lezen. Wil je iets aanpassen,
geef het door (of sla op als kopie); de wijziging komt dan via `design.py` in het ontwerp.

## Werkwijze
- Elke ontwerpwijziging is een eigen commit; goedgekeurde stappen krijgen een tag (bijv. `schema-v1.0`).
- Wijzig het schema bij voorkeur via `design.py` + `build.sh`, zodat de controle blijft kloppen.
  Handmatige aanpassingen in KiCad kunnen ook, maar worden bij een volgende generatie overschreven.
