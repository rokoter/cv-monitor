#!/usr/bin/env bash
# Koperlagen als PNG (KiCad-kleuren) voor documentatie: boven, onder (gespiegeld), In1 (GND), In2 (3V3).
# Gebruik: generator/render_layers.sh <bord.kicad_pcb> <uitmap> <achtervoegsel>
set -euo pipefail
B=$1; OUT=$2; SUF=$3; T=$(mktemp -d)
exp() { kicad-cli pcb export svg $3 --layers "$2" --page-size-mode 2 --exclude-drawing-sheet -o "$T/$1.svg" "$B" >/dev/null 2>&1
        rsvg-convert -w 1800 -b white "$T/$1.svg" -o "$OUT/pcb_routing_$1_$SUF.png"; }
exp boven "F.Cu,F.SilkS,Edge.Cuts" ""
exp onder "B.Cu,B.SilkS,Edge.Cuts" "-m"
exp in1_gnd "In1.Cu,Edge.Cuts" ""
exp in2_3v3 "In2.Cu,Edge.Cuts" ""
rm -rf "$T"
echo "lagen -> $OUT/pcb_routing_*_$SUF.png"
