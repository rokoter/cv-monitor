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
from placement import PLACE, HOLES, EDGE_ALIGN, BOARD_W, BOARD_H, CORNER_R, COPPER_LAYERS  # noqa: E402

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
board.SetCopperLayerCount(COPPER_LAYERS)

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

# ------------------------------------------------------------------ doorvoersleuf NTC (afgeronde sleuf in Edge.Cuts)
from placement import NTC_SLOT  # noqa: E402
sx0, sy0, sw, sh = NTC_SLOT
sr = sw / 2                                           # halve breedte = straal van de ronde uiteinden
for x in (sx0 - sr, sx0 + sr):
    s = pcbnew.PCB_SHAPE(board)
    s.SetShape(pcbnew.SHAPE_T_SEGMENT)
    s.SetStart(P(x, sy0 - sh / 2 + sr))
    s.SetEnd(P(x, sy0 + sh / 2 - sr))
    add_shape(s)
for cy, d in ((sy0 - sh / 2 + sr, -1), (sy0 + sh / 2 - sr, 1)):
    a = pcbnew.PCB_SHAPE(board)
    a.SetShape(pcbnew.SHAPE_T_ARC)
    a.SetArcGeometry(P(sx0 - sr, cy), P(sx0, cy + d * sr), P(sx0 + sr, cy))
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


text('CV-monitor rev 0.2', 58.0, 56.5, 1.2)

# accupolariteit: '+' en '-' naast de padden van de houder (boven- en onderkant)
bt = fps['BT1']
POL = {'1': ('+', 0.0, 3.6), '2': ('-', 0.0, -3.6)}       # (teken, dx, dy) t.o.v. de pad
for pad in bt.Pads():
    if pad.GetNumber() in POL:
        sym, dx, dy = POL[pad.GetNumber()]
        pos = pad.GetPosition()
        for layer, mir in ((pcbnew.B_SilkS, True), (pcbnew.F_SilkS, False)):
            t = pcbnew.PCB_TEXT(board)
            t.SetText(sym)
            t.SetPosition(pcbnew.VECTOR2I(pos.x + mm(dx), pos.y + mm(dy)))
            t.SetLayer(layer)
            t.SetTextSize(pcbnew.VECTOR2I(mm(2.0), mm(2.0)))
            t.SetTextThickness(mm(0.3))
            t.SetMirrored(mir)
            board.Add(t)
# referentie van de houder midden op de houder (onderkant)
bt.Reference().SetPosition(P(47.0, 58.7))
bt.Reference().SetTextAngle(pcbnew.EDA_ANGLE(0, pcbnew.DEGREES_T))

# ------------------------------------------------------------------ silkscreen-referenties
from silk import place_all  # noqa: E402
tp_labels = {r: comps[r]['value'] for r in comps if r.startswith('TP')}
from placement import FUNC_LABELS, FUNC_LABELS_BACK, FUNC_LABEL_DIR, PIN_LABELS  # noqa: E402
from silk import place_pin_labels  # noqa: E402
failed = place_pin_labels(board, OX, OY, BOARD_W, BOARD_H, CORNER_R, PIN_LABELS)   # eerst: vaste plek
failed += place_all(board, OX, OY, BOARD_W, BOARD_H, CORNER_R, label_override=tp_labels, hide=tuple(HOLES),
                   inner=('U5',), func_labels=FUNC_LABELS, func_labels_back=FUNC_LABELS_BACK,
                   func_dir=FUNC_LABEL_DIR, manual=('BT1',))
if failed:
    print('referentie naar fab-laag (geen plek op silk):', ', '.join(failed))

# ------------------------------------------------------------------ mechanische controle
from pcb_checks import tht_vs_other_side  # noqa: E402
mech = tht_vs_other_side(board)
for e in mech:
    print('MECH-FOUT:', e)

board.BuildConnectivity()
pcbnew.SaveBoard(OUT, board)
print(f'PCB geschreven: {len(fps)} footprints, {len(nets)} netten -> {OUT}')
