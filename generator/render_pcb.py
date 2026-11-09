"""Maakt een review-plaatje van de PCB: footprints, courtyards, silkscreen en de ratsnest
(kortste verbindingen per net, zonder GND) op de laag Dwgs.User.
    /usr/bin/python3 generator/render_pcb.py <board.kicad_pcb> <uit.svg>
"""
import os
import subprocess
import sys
import tempfile

import pcbnew

src, out = sys.argv[1], sys.argv[2]
board = pcbnew.LoadBoard(src)
board.BuildConnectivity()

pads_by_net = {}
for fp in board.GetFootprints():
    for p in fp.Pads():
        n = p.GetNetname()
        if n and n != 'GND' and not n.startswith('unconnected'):
            pads_by_net.setdefault(n, []).append(p.GetPosition())

count = 0
for net, pts in pads_by_net.items():
    pts = list({(q.x, q.y) for q in pts})
    if len(pts) < 2:
        continue
    # minimale opspannende boom (Prim)
    inside, rest = [pts[0]], pts[1:]
    while rest:
        best = min(((a, b) for a in inside for b in rest), key=lambda ab: (ab[0][0] - ab[1][0]) ** 2 + (ab[0][1] - ab[1][1]) ** 2)
        s = pcbnew.PCB_SHAPE(board)
        s.SetShape(pcbnew.SHAPE_T_SEGMENT)
        s.SetStart(pcbnew.VECTOR2I(*best[0]))
        s.SetEnd(pcbnew.VECTOR2I(*best[1]))
        s.SetLayer(pcbnew.Dwgs_User)
        s.SetWidth(pcbnew.FromMM(0.08))
        board.Add(s)
        inside.append(best[1])
        rest.remove(best[1])
        count += 1

tmp = os.path.join(tempfile.mkdtemp(), 'review.kicad_pcb')
pcbnew.SaveBoard(tmp, board)
layers = 'Edge.Cuts,F.Cu,F.SilkS,F.Fab,F.CrtYd,B.Fab,Dwgs.User'
subprocess.run(['kicad-cli', 'pcb', 'export', 'svg', '--layers', layers, '--page-size-mode', '2',
                '--exclude-drawing-sheet', '-o', out, tmp], check=True, capture_output=True)
print(f'{count} ratsnest-lijnen, render: {out}')
