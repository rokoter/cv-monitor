#!/usr/bin/env bash
# Bouwt symboolbibliotheek + schema opnieuw en controleert het resultaat met KiCad zelf.
# Gebruik:  ./generator/build.sh        (vanuit de hoofdmap van de repo, KiCad 7+ met kicad-cli nodig)
set -euo pipefail
cd "$(dirname "$0")/.."
PRJ=hardware/cv_monitor

python3 -I generator/make_lib.py "$PRJ/cv_monitor.kicad_sym"
python3 -I generator/make_project_fps.py "$PRJ/cv_monitor.pretty"
python3 -I generator/make_sch.py "$PRJ"
python3 -I generator/make_drawio.py docs/accubeveiliging_DW01A_FS8205A.drawio

# Controle: KiCad exporteert de netlist, wij vergelijken met de bedoeling (design.py)
kicad-cli sch export netlist -o /tmp/cv_monitor.net "$PRJ/cv_monitor.kicad_sch" >/dev/null
python3 -I generator/check_netlist.py /tmp/cv_monitor.net generator/expected_nets.json
python3 -I generator/check_footprints.py | tail -1

kicad-cli sch export pdf -o docs/cv_monitor_schema.pdf "$PRJ/cv_monitor.kicad_sch" >/dev/null
python3 -I generator/bom_overview.py
echo "klaar: schema, PDF en controle bijgewerkt"
