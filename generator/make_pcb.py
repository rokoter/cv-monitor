"""Bouwt hardware/cv_monitor/cv_monitor.kicad_pcb uit de KiCad-netlist + placement.py.

Draaien met de Python van het systeem (daar zit de KiCad-module pcbnew in):
    /usr/bin/python3 generator/make_pcb.py <netlist> <uitvoer.kicad_pcb>

Elke footprint krijgt het pad (UUID) van zijn schemasymbool, zodat KiCad's
'Update PCB from Schematic' en kruis-selectie gewoon werken.
"""
import math
import os
import re
import sys

import pcbnew

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from placement import PLACE, HOLES, EDGE_ALIGN, BOARD_W, BOARD_H, CORNER_R  # noqa: E402

NETLIST, OUT = sys.argv[1], sys.argv[2]
PRJ = os.path.dirname(os.path.abspath(OUT))
OX, OY = 100.0, 100.0          # bordoorsprong in KiCad-coördinaten (mm)
mm = pcbnew.FromMM


def P(x, y):
    return pcbnew.VECTOR2I(mm(OX + x), mm(OY + y))


# ------------------------------------------------------------------ netlist inlezen
txt = open(NETLIST).read()
comps = {}
for m in re.finditer(r'\(comp \(ref "([^"]+)"\)(.*?)\(tstamps "([^"]+)"\)\)', txt, re.S):
    ref, body, ts = m.group(1), m.group(2), m.group(3)
    val = re.search(r'\(value "([^"]*)"\)', body).group(1)
    fp = re.search(r'\(footprint "([^"]*)"\)', body).group(1)
    props = dict(re.findall(r'\(property \(name "([^"]+)"\) \(value "([^"]*)"\)\)', body))
    comps[ref] = dict(value=val, fp=fp, uuid=ts, props=props)
nets = {}
for m in re.finditer(r'\(net \(code "\d+"\) \(name "([^"]*)"\)(.*?)\)\s*(?=\(net |\)\s*\)\s*$)', txt, re.S):
    name = m.group(1).lstrip('/')
    nodes = re.findall(r'\(node \(ref "([^"]+)"\) \(pin "([^"]+)"\)', m.group(2))
    nodes = [n for n in nodes if not n[0].startswith('#')]
    if nodes:
        nets[name] = nodes

# DNP en 'niet in BOM' uit het ontwerp halen
from design import COMPONENTS  # noqa: E402
meta = {c['ref']: c for c in COMPONENTS}

board = pcbnew.BOARD()
board.SetCopperLayerCount(2)

# ------------------------------------------------------------------ footprints
fps = {}
for ref, c in sorted(comps.items()):
    lib, name = c['fp'].split(':')
    libpath = os.path.join(PRJ, 'cv_monitor.pretty') if lib == 'cv_monitor' else f'/usr/share/kicad/footprints/{lib}.pretty'
    fp = pcbnew.FootprintLoad(libpath, name)
    if fp is None:
        raise SystemExit(f'footprint {c["fp"]} niet gevonden')
    fp.SetFPID(pcbnew.LIB_ID(lib, name))
    fp.SetReference(ref)
    fp.SetValue(c['value'])
    fp.SetPath(pcbnew.KIID_PATH(f'/{c["uuid"]}'))
    if c['props'].get('LCSC'):
        fp.SetProperty('LCSC', c['props']['LCSC'])
    attrs = fp.GetAttributes()
    md = meta.get(ref, {})
    if md.get('dnp') or md.get('in_bom') is False:
        attrs |= pcbnew.FP_EXCLUDE_FROM_POS_FILES | pcbnew.FP_EXCLUDE_FROM_BOM
        if md.get('dnp') and hasattr(pcbnew, 'FP_DNP'):
            attrs |= pcbnew.FP_DNP
    fp.SetAttributes(attrs)
    board.Add(fp)
    fps[ref] = fp

# ------------------------------------------------------------------ netten koppelen
netobjs = {}
for name, nodes in nets.items():
    ni = pcbnew.NETINFO_ITEM(board, name)
    board.Add(ni)
    netobjs[name] = ni
    for ref, pin in nodes:
        pads = [p for p in fps[ref].Pads() if p.GetNumber() == pin]
        if not pads:
            raise SystemExit(f'{ref} heeft geen pad {pin}')
        for p in pads:
            p.SetNet(ni)

# ------------------------------------------------------------------ plaatsing
missing = [r for r in fps if r not in PLACE and r not in HOLES]
if missing:
    raise SystemExit(f'geen plaats voor: {missing}')


def bbox_mm(fp):
    cy = fp.GetCourtyard(pcbnew.F_CrtYd if not fp.IsFlipped() else pcbnew.B_CrtYd)
    bb = cy.BBox() if cy.OutlineCount() else fp.GetBoundingBox(False, False)
    return (pcbnew.ToMM(bb.GetLeft()) - OX, pcbnew.ToMM(bb.GetTop()) - OY,
            pcbnew.ToMM(bb.GetRight()) - OX, pcbnew.ToMM(bb.GetBottom()) - OY)


for ref, (x, y, rot, side) in PLACE.items():
    fp = fps[ref]
    fp.SetPosition(P(x or 0, y or 0))
    fp.SetOrientationDegrees(rot)
    if side == 'B':
        fp.Flip(fp.GetPosition(), True)
    if ref in EDGE_ALIGN:
        edge, over = EDGE_ALIGN[ref]
        l, t, r, b = bbox_mm(fp)
        dx = dy = 0.0
        if edge == 'left':
            dx = (-over) - l
        elif edge == 'right':
            dx = (BOARD_W + over) - r
        elif edge == 'bottom':
            dy = (BOARD_H + over) - b
        fp.Move(pcbnew.VECTOR2I(mm(dx), mm(dy)))
for ref, (x, y) in HOLES.items():
    fps[ref].SetPosition(P(x, y))

# ------------------------------------------------------------------ bordcontour (afgeronde hoeken)
def add_shape(shape, layer=pcbnew.Edge_Cuts, w=0.1):
    shape.SetLayer(layer)
    shape.SetWidth(mm(w))
    board.Add(shape)


W, H, R = BOARD_W, BOARD_H, CORNER_R
for (x1, y1, x2, y2) in [(R, 0, W - R, 0), (W, R, W, H - R), (W - R, H, R, H), (0, H - R, 0, R)]:
    s = pcbnew.PCB_SHAPE(board)
    s.SetShape(pcbnew.SHAPE_T_SEGMENT)
    s.SetStart(P(x1, y1))
    s.SetEnd(P(x2, y2))
    add_shape(s)
k = R * (1 - math.sqrt(0.5))
for (sx, sy, mx, my, ex, ey) in [(0, R, k, k, R, 0), (W - R, 0, W - k, k, W, R),
                                 (W, H - R, W - k, H - k, W - R, H), (R, H, k, H - k, 0, H - R)]:
    a = pcbnew.PCB_SHAPE(board)
    a.SetShape(pcbnew.SHAPE_T_ARC)
    a.SetArcGeometry(P(sx, sy), P(mx, my), P(ex, ey))
    add_shape(a)

# ------------------------------------------------------------------ silkscreen: titel en accupolariteit
def text(t, x, y, size=1.0, layer=pcbnew.F_SilkS, mirror=False):
    tx = pcbnew.PCB_TEXT(board)
    tx.SetText(t)
    tx.SetPosition(P(x, y))
    tx.SetLayer(layer)
    tx.SetTextSize(pcbnew.VECTOR2I(mm(size), mm(size)))
    tx.SetTextThickness(mm(size * 0.15))
    if mirror:
        tx.SetMirrored(True)
    board.Add(tx)


text('CV-monitor rev 0.1', 47.0, 36.5, 1.2)
bt = fps['BT1']
for pad in bt.Pads():
    if pad.GetNumber() in ('1', '2'):
        pos = pad.GetPosition()
        sym = '+' if pad.GetNumber() == '1' else '-'
        for layer, mir in ((pcbnew.B_SilkS, True), (pcbnew.F_SilkS, False)):
            t = pcbnew.PCB_TEXT(board)
            t.SetText(sym)
            t.SetPosition(pcbnew.VECTOR2I(pos.x, pos.y - mm(3.2)))
            t.SetLayer(layer)
            t.SetTextSize(pcbnew.VECTOR2I(mm(2.0), mm(2.0)))
            t.SetTextThickness(mm(0.3))
            t.SetMirrored(mir)
            board.Add(t)

board.BuildConnectivity()
pcbnew.SaveBoard(OUT, board)
print(f'PCB geschreven: {len(fps)} footprints, {len(nets)} netten -> {OUT}')
