"""Fanout en vaste voor-routing vóór de autorouter.

1. Elke SMD-pad op GND of 3V3 krijgt een kort spoor naar een eigen via naar het binnenvlak
   (In1 = GND, In2 = 3V3). Freerouting doet dat zelf niet (het beschouwt vlak-netten als verbonden).
   De via komt zo dicht mogelijk bij de pad, bij voorkeur aan de buitenkant van het onderdeel,
   met de ontwerpregels als harde eis (eigen eenvoudige geometrie: pads als rechthoek/cirkel).
2. USB-C: D+ (A6/B6) en D- (A7/B7) liggen om en om in een rij met 0,5 mm steek. D- wordt rechts
   van de rij verbonden (boven), D+ links onder de connector met een via naar de onderkant.
Alle sporen/via's hier worden vergrendeld, zodat de autorouter ze laat staan.
"""
import math

import pcbnew

mm = pcbnew.FromMM
OX, OY, W, H = 100.0, 100.0, 94.0, 70.0
VIA_D, VIA_DRILL = 0.6, 0.3
STUB_W = 0.4
CLR = 0.22          # koper-koper (Supply-klasse 0,2 + marge)
EDGE = 0.35         # koper-bordrand (regel 0,3 + marge)


def _box(item):
    b = item.GetBoundingBox()
    return (pcbnew.ToMM(b.GetLeft()) - OX, pcbnew.ToMM(b.GetTop()) - OY,
            pcbnew.ToMM(b.GetRight()) - OX, pcbnew.ToMM(b.GetBottom()) - OY)


def _d_pt_box(x, y, b):
    dx = max(b[0] - x, 0, x - b[2])
    dy = max(b[1] - y, 0, y - b[3])
    return math.hypot(dx, dy)


class Obstacles:
    def __init__(self, board):
        self.items = []     # (box, net, kind) kind: 'pad' (koper), 'hole', 'via', 'stub'
        self.vias = []      # (x, y, net)
        self.keepout = []   # boxen waar geen via mag (antenne)
        self.crt = []       # (box, ref) courtyards bovenkant
        for fp in board.GetFootprints():
            for p in fp.Pads():
                kind = 'hole' if p.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH else 'pad'
                self.items.append((_box(p), p.GetNetname(), kind, fp.GetReference(), p))
            if not fp.IsFlipped():
                cy = fp.GetCourtyard(pcbnew.F_CrtYd)
                if cy.OutlineCount():
                    b = cy.BBox()
                    self.crt.append(((pcbnew.ToMM(b.GetLeft()) - OX, pcbnew.ToMM(b.GetTop()) - OY,
                                      pcbnew.ToMM(b.GetRight()) - OX, pcbnew.ToMM(b.GetBottom()) - OY),
                                     fp.GetReference(), cy))
            for z in fp.Zones():
                if z.GetIsRuleArea() and z.GetDoNotAllowVias():
                    self.keepout.append(z)
        for z in board.Zones():
            if z.GetIsRuleArea() and z.GetDoNotAllowVias():
                self.keepout.append(z)
        for d in board.GetDrawings():                         # uitsparingen (NTC-sleuf)
            if d.GetLayer() == pcbnew.Edge_Cuts:
                b = _box(d)
                if b[0] > 1 and b[2] < W - 1 and b[1] > 1 and b[3] < H - 1:
                    self.items.append((b, '', 'hole', '', None))

    def via_ok(self, x, y, net, own_pad, strict_crt=True):
        r = VIA_D / 2
        if x - r < EDGE or y - r < EDGE or x + r > W - EDGE or y + r > H - EDGE:
            return False
        for c in ((3, 3), (W - 3, 3), (3, H - 3), (W - 3, H - 3)):      # afgeronde hoeken (R 3)
            if (abs(x - c[0]) > 0 and (x < 3 or x > W - 3)) and (y < 3 or y > H - 3):
                if math.hypot(x - c[0], y - c[1]) > 3 - EDGE - r:
                    return False
        pt = pcbnew.VECTOR2I(mm(OX + x), mm(OY + y))
        for z in self.keepout:
            if z.Outline().Collide(pt, mm(r)):
                return False
        for b, n, kind, ref, p in self.items:
            d = _d_pt_box(x, y, b)
            if p is own_pad:
                if d < r + 0.15:                      # geen via-in-pad
                    return False
            elif kind == 'hole':
                if d < r + 0.3:
                    return False
            elif n != net or not n:
                if d < r + CLR:
                    return False
            elif d < r + 0.1:                         # zelfde net: niet in een andere pad
                return False
        for vx, vy, vn in self.vias:
            if math.hypot(x - vx, y - vy) < VIA_D + 0.3:
                return False
        if strict_crt:
            own_ref = pcbnew.Cast_to_FOOTPRINT(own_pad.GetParent()).GetReference() if own_pad else ''
            for b, ref, cy in self.crt:
                if ref != own_ref and _d_pt_box(x, y, b) < r and cy.Collide(pt, mm(r)):
                    return False
        return True

    def stub_ok(self, x1, y1, x2, y2, net, own_pad):
        n = max(2, int(math.hypot(x2 - x1, y2 - y1) / 0.05))
        for i in range(n + 1):
            x, y = x1 + (x2 - x1) * i / n, y1 + (y2 - y1) * i / n
            for b, pn, kind, ref, p in self.items:
                if p is own_pad or (pn == net and kind == 'pad'):
                    continue
                if _d_pt_box(x, y, b) < STUB_W / 2 + (0.3 if kind == 'hole' else CLR):
                    return False
            for vx, vy, vn in self.vias:
                if vn != net and math.hypot(x - vx, y - vy) < VIA_D / 2 + STUB_W / 2 + CLR:
                    return False
        return True


def _add_track(board, net, x1, y1, x2, y2, w, layer=pcbnew.F_Cu):
    t = pcbnew.PCB_TRACK(board)
    t.SetStart(pcbnew.VECTOR2I(mm(OX + x1), mm(OY + y1)))
    t.SetEnd(pcbnew.VECTOR2I(mm(OX + x2), mm(OY + y2)))
    t.SetWidth(mm(w))
    t.SetLayer(layer)
    t.SetNet(net)
    t.SetLocked(True)
    board.Add(t)


def _add_via(board, net, x, y, d=VIA_D, drill=VIA_DRILL):
    v = pcbnew.PCB_VIA(board)
    v.SetViaType(pcbnew.VIATYPE_THROUGH)
    v.SetPosition(pcbnew.VECTOR2I(mm(OX + x), mm(OY + y)))
    v.SetWidth(mm(d))
    v.SetDrill(mm(drill))
    v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
    v.SetNet(net)
    v.SetLocked(True)
    board.Add(v)


def fanout(board, nets=('GND', '+3V3')):
    obs = Obstacles(board)
    done, failed = 0, []
    pads = []
    for fp in board.GetFootprints():
        pth = {p.GetNumber() for p in fp.Pads() if p.GetAttribute() == pcbnew.PAD_ATTRIB_PTH}
        cx, cy = (pcbnew.ToMM(fp.GetPosition().x) - OX, pcbnew.ToMM(fp.GetPosition().y) - OY)
        for p in fp.Pads():
            if (p.GetNetname() in nets and p.GetAttribute() == pcbnew.PAD_ATTRIB_SMD
                    and p.GetNumber() not in pth and not fp.IsFlipped()):
                pads.append((fp, p, cx, cy))
    seen = set()
    for fp, p, cx, cy in pads:
        b = _box(p)
        px, py = (b[0] + b[2]) / 2, (b[1] + b[3]) / 2
        key = (fp.GetReference(), round(px, 2), round(py, 2))
        if key in seen:                              # USB-C: A1/B12 liggen op dezelfde plek
            continue
        seen.add(key)
        net = p.GetNet()
        hw, hh = (b[2] - b[0]) / 2, (b[3] - b[1]) / 2
        out = math.atan2(py - cy, px - cx) if (abs(px - cx) + abs(py - cy)) > 0.05 else 0.0
        angles = sorted((math.radians(a) for a in range(0, 360, 15)),
                        key=lambda a: abs(math.atan2(math.sin(a - out), math.cos(a - out))))
        placed = False
        for strict in (True, False):
            for extra in (0.0, 0.25, 0.5, 0.8, 1.2, 1.7):
                for a in angles:
                    ca, sa = math.cos(a), math.sin(a)
                    # afstand tot de rand van de pad in deze richting + via + marge
                    reach = min(hw / abs(ca) if abs(ca) > 1e-6 else 1e9, hh / abs(sa) if abs(sa) > 1e-6 else 1e9)
                    dist = reach + 0.15 + VIA_D / 2 + extra
                    vx, vy = px + ca * dist, py + sa * dist
                    if obs.via_ok(vx, vy, p.GetNetname(), p, strict) and \
                            obs.stub_ok(px, py, vx, vy, p.GetNetname(), p):
                        _add_track(board, net, px, py, vx, vy, STUB_W)
                        _add_via(board, net, vx, vy)
                        obs.vias.append((vx, vy, p.GetNetname()))
                        obs.items.append(((min(px, vx), min(py, vy), max(px, vx), max(py, vy)),
                                          p.GetNetname(), 'stub', '', None))
                        placed = True
                        break
                if placed:
                    break
            if placed:
                break
        if placed:
            done += 1
        else:
            failed.append(f'{fp.GetReference()}.{p.GetNumber()}')
    return done, failed


def usb_preroute(board):
    """Vaste verbindingen van de dubbele USB-C datapinnen (zie module-uitleg)."""
    j1 = next(f for f in board.GetFootprints() if f.GetReference() == 'J1')
    pads = {p.GetNumber(): p for p in j1.Pads()}
    pos = lambda n: (pcbnew.ToMM(pads[n].GetPosition().x) - OX, pcbnew.ToMM(pads[n].GetPosition().y) - OY)
    dm, dp = pads['A7'].GetNet(), pads['A6'].GetNet()
    (xa7, ya7), (xb7, yb7) = pos('A7'), pos('B7')
    (xa6, ya6), (xb6, yb6) = pos('A6'), pos('B6')
    w = 0.2
    # D-: rechts van de padrij
    xr = xa7 + 0.725 + 0.63
    for y in (ya7, yb7):
        _add_track(board, dm, xa7, y, xr, y, w)
    _add_track(board, dm, xr, ya7, xr, yb7, w)
    # D+: links van de padrij (onder de connector) en via naar de onderkant
    xl = xa6 - 0.725 - 0.27
    for y in (ya6, yb6):
        _add_track(board, dp, xa6, y, xl, y, w)
    _add_track(board, dp, xl, ya6, xl, yb6, w)
    vx, vy = xl - 0.25, (ya6 + yb6) / 2           # standaardvia 0,6/0,3, 0,22 mm van pad A7
    _add_track(board, dp, xl, vy, vx, vy, w)
    _add_via(board, dp, vx, vy)
    return (xr, (ya7 + yb7) / 2), (vx, vy)
