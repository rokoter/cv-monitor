"""Draait de KiCad-DRC (via de Python-API, KiCad 7 heeft geen CLI-DRC) en vat het rapport samen.
    /usr/bin/python3 generator/drc.py <board.kicad_pcb> [rapport.txt] [--detail type]
"""
import collections
import os
import re
import sys

os.environ.setdefault('KICAD7_FOOTPRINT_DIR', '/usr/share/kicad/footprints')
os.environ.setdefault('KICAD7_SYMBOL_DIR', '/usr/share/kicad/symbols')
import pcbnew  # noqa: E402

board_path = sys.argv[1]
rpt = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith('--') else '/tmp/drc.rpt'
detail = sys.argv[sys.argv.index('--detail') + 1] if '--detail' in sys.argv else None

board = pcbnew.LoadBoard(board_path)
pcbnew.WriteDRCReport(board, rpt, pcbnew.EDA_UNITS_MILLIMETRES, True)
txt = open(rpt).read()
items = re.findall(r'^\[(\w+)\]: (.*?)\n((?:    .*\n)*)', txt, re.M)
cnt = collections.Counter(t for t, _, _ in items)
for t, n in cnt.most_common():
    sev = 'fout' if re.search(rf'\[{t}\]: .*\n.*; error', txt) else ''
    print(f'{n:4}  {t}')
if detail:
    for t, msg, body in items:
        if t == detail:
            print('-', msg.strip(), '|', ' / '.join(l.strip() for l in body.splitlines()[:3]))
m = re.search(r'\*\* Found (\d+) DRC violations', txt)
u = re.search(r'\*\* Found (\d+) unconnected pads', txt)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pcb_checks import tht_vs_other_side  # noqa: E402
mech = tht_vs_other_side(board)
for e in mech:
    print('MECH-FOUT:', e)
print(f'DRC: {m.group(1) if m else "?"} schendingen, {u.group(1) if u else "?"} niet-verbonden pads, {len(mech)} mechanische fouten')
