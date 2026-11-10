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


def _d_pt_seg(px, py, x1, y1, x2, y2):
    dx, dy = x2 - x1, y2 - y1
    L2 = dx * dx + dy * dy
    t = 0.0 if L2 == 0 else max(0.0, min(1.0, ((px - x1) * dx + (py - y1) * dy) / L2))
    return math.hypot(px - (x1 + t * dx), py - (y1 + t * dy))


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
        self.segs = []      # bestaande sporen: (x1, y1, x2, y2, halve breedte, net)
        for t in board.GetTracks():
            if t.GetClass() == 'PCB_VIA':
                self.vias.append((pcbnew.ToMM(t.GetPosition().x) - OX, pcbnew.ToMM(t.GetPosition().y) - OY,
                                  t.GetNetname()))
            else:
                self.segs.append((pcbnew.ToMM(t.GetStart().x) - OX, pcbnew.ToMM(t.GetStart().y) - OY,
                                  pcbnew.ToMM(t.GetEnd().x) - OX, pcbnew.ToMM(t.GetEnd().y) - OY,
                                  pcbnew.ToMM(t.GetWidth()) / 2, t.GetNetname(), t.GetLayer()))
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
        for sx1, sy1, sx2, sy2, hw, sn, sl in self.segs:          # via: alle lagen
            if sn != net and _d_pt_seg(x, y, sx1, sy1, sx2, sy2) < r + hw + CLR:
                return False
        if strict_crt:
            own_ref = pcbnew.Cast_to_FOOTPRINT(own_pad.GetParent()).GetReference() if own_pad else ''
            for b, ref, cy in self.crt:
                if ref != own_ref and _d_pt_box(x, y, b) < r and cy.Collide(pt, mm(r)):
                    return False
        return True

    def stub_ok(self, x1, y1, x2, y2, net, own_pad, other_pad=None):
        n = max(2, int(math.hypot(x2 - x1, y2 - y1) / 0.05))
        for i in range(n + 1):
            x, y = x1 + (x2 - x1) * i / n, y1 + (y2 - y1) * i / n
            for b, pn, kind, ref, p in self.items:
                if p is own_pad or p is other_pad or (pn == net and kind in ('pad', 'stub')):
                    continue
                if _d_pt_box(x, y, b) < STUB_W / 2 + (0.3 if kind == 'hole' else CLR):
                    return False
            for vx, vy, vn in self.vias:
                if vn != net and math.hypot(x - vx, y - vy) < VIA_D / 2 + STUB_W / 2 + CLR:
                    return False
            for sx1, sy1, sx2, sy2, hw, sn, sl in self.segs:      # stub ligt op de bovenlaag
                if sl == pcbnew.F_Cu and sn != net and _d_pt_seg(x, y, sx1, sy1, sx2, sy2) < STUB_W / 2 + hw + CLR:
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
        if not placed:
            # geen plek voor een eigen via: kort spoor naar een pad van hetzelfde net in de buurt
            # (bijv. ESP-voedingspin -> ontkoppelcondensator, die zelf een via naar het vlak heeft)
            cands = []
            for fp2 in board.GetFootprints():
                for q in fp2.Pads():
                    tht = q.GetAttribute() == pcbnew.PAD_ATTRIB_PTH        # zit al aan het vlak
                    smd_other = (q.GetAttribute() == pcbnew.PAD_ATTRIB_SMD and not fp2.IsFlipped()
                                 and fp2.GetReference() != fp.GetReference())
                    if q.GetNetname() == p.GetNetname() and (tht or smd_other):
                        qb = _box(q)
                        qx, qy = (qb[0] + qb[2]) / 2, (qb[1] + qb[3]) / 2
                        dd = math.hypot(qx - px, qy - py)
                        if dd < 4.0:
                            cands.append((dd, q, qx, qy))
            for dd, q, qx, qy in sorted(cands, key=lambda c: c[0]):
                if obs.stub_ok(px, py, qx, qy, p.GetNetname(), p, q):
                    _add_track(board, net, px, py, qx, qy, STUB_W)
                    obs.items.append(((min(px, qx), min(py, qy), max(px, qx), max(py, qy)),
                                      p.GetNetname(), 'stub', '', None))
                    placed = True
                    break
        if placed:
            done += 1
        else:
            failed.append(f'{fp.GetReference()}.{p.GetNumber()}')
    return done, failed


USB_W, USB_GAP = 0.25, 0.15          # differentieel paar: ~90 ohm op JLCPCB 4-laags (schatting)


def _offset(points, d):
    """Evenwijdige lijn op afstand d links van de rijrichting (y omlaag), met verstekhoeken."""
    out = []
    n = len(points)
    for i in range(n):
        normals = []
        for a, b in ((i - 1, i), (i, i + 1)):
            if 0 <= a and b < n:
                dx, dy = points[b][0] - points[a][0], points[b][1] - points[a][1]
                L = math.hypot(dx, dy)
                normals.append((dy / L, -dx / L))
        nx = sum(v[0] for v in normals) / len(normals)
        ny = sum(v[1] for v in normals) / len(normals)
        L = math.hypot(nx, ny)
        nx, ny = nx / L, ny / L
        k = d / (nx * normals[0][0] + ny * normals[0][1])
        out.append((points[i][0] + nx * k, points[i][1] + ny * k))
    return out


def _poly(board, net, pts, w, layer):
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        _add_track(board, net, x1, y1, x2, y2, w, layer)


def usb_preroute(board):
    """USB D+/D- helemaal vast: dubbele pinnen in de USB-C, via ESD-chip U1 en dan als
    differentieel paar (0,25 mm / 0,15 mm) over de onderkant naar ESP-pin 13 (D-) en 14 (D+).
    U1 staat 180° gedraaid zodat D- links/boven en D+ rechts/onder blijft: geen kruising nodig."""
    fps = {f.GetReference(): f for f in board.GetFootprints()}
    def pad(ref, num):
        p = next(q for q in fps[ref].Pads() if q.GetNumber() == num)
        return pcbnew.ToMM(p.GetPosition().x) - OX, pcbnew.ToMM(p.GetPosition().y) - OY, p.GetNet()
    xa7, ya7, dm = pad('J1', 'A7')
    xb7, yb7, _ = pad('J1', 'B7')
    xa6, ya6, dp = pad('J1', 'A6')
    xb6, yb6, _ = pad('J1', 'B6')
    F, B = pcbnew.F_Cu, pcbnew.B_Cu
    w0 = 0.2                                     # tussen de 0,5 mm-pinnen van de USB-C
    # D-: rechts van de padrij, via naar de onderkant (zodat de tweede VBUS-pin A9 vrij naar rechts kan),
    #     onder langs en via weer omhoog: van boven in U1 pin 4 (west, boven)
    xr = xa7 + 0.725 + 0.63
    for y in (ya7, yb7):
        _add_track(board, dm, xa7, y, xr, y, w0)
    _add_track(board, dm, xr, ya7, xr, yb7, w0)
    u4x, u4y, _ = pad('U1', '4')
    ylow = max(ya7, yb7)
    v1x, v1y = xr + 0.4, ylow + 0.85
    _poly(board, dm, [(xr, ylow), (xr + 0.4, ylow + 0.4), (v1x, v1y)], w0, F)
    _add_via(board, dm, v1x, v1y)
    v2x, v2y = u4x, u4y - 1.2
    _poly(board, dm, [(v1x, v1y), (v1x, v2y - (v2x - v1x)), (v2x, v2y)], w0, B)
    _add_via(board, dm, v2x, v2y)
    _add_track(board, dm, v2x, v2y, u4x, u4y, w0)
    # D+: links van de padrij (onder de connector), via naar de onderkant, en van onderen in U1 pin 6
    xl = xa6 - 0.725 - 0.27
    for y in (ya6, yb6):
        _add_track(board, dp, xa6, y, xl, y, w0)
    _add_track(board, dp, xl, ya6, xl, yb6, w0)
    v0x, v0y = xl - 0.25, (ya6 + yb6) / 2
    _add_track(board, dp, xl, v0y, v0x, v0y, w0)
    _add_via(board, dp, v0x, v0y)
    u6x, u6y, _ = pad('U1', '6')
    xb = v0x + 1.75                              # verticaal op de onderkant, rechts van de mantelpin S1
    vbx, vby = xb, u6y + 0.4
    _poly(board, dp, [(v0x, v0y), (xb, v0y + 1.25), (xb, vby)], w0, B)
    _add_via(board, dp, vbx, vby)
    _poly(board, dp, [(vbx, vby), (vbx + 0.4, u6y), (u6x, u6y)], w0, F)
    # U1 pin 5 (VBUS) zit nu tussen D- en D+ in: eigen via naar links, de autorouter doet de rest
    u5x, u5y, vbus = pad('U1', '5')
    _add_track(board, vbus, u5x, u5y, u5x - 0.96, u5y, 0.5)
    _add_via(board, vbus, u5x - 0.96, u5y, 0.8, 0.4)
    # U1 oost: pin 3 (D-, boven) en pin 1 (D+, onder) -> via's -> paar op de onderkant
    u3x, u3y, _ = pad('U1', '3')
    u1x, u1y, _ = pad('U1', '1')
    vx = u3x + 1.76
    _add_track(board, dm, u3x, u3y, vx, u3y, USB_W)
    _add_track(board, dp, u1x, u1y, vx, u1y, USB_W)
    _add_via(board, dm, vx, u3y)
    _add_via(board, dp, vx, u1y)
    # ESP-kant: via's links van pin 13 (D-) en 14 (D+)
    e13x, e13y, _ = pad('U5', '13')
    e14x, e14y, _ = pad('U5', '14')
    ex = e13x - 2.3
    _add_via(board, dm, ex, e13y)
    _add_via(board, dp, ex, e14y)
    _add_track(board, dm, ex, e13y, e13x, e13y, USB_W)
    _add_track(board, dp, ex, e14y, e14x, e14y, USB_W)
    # het paar (middellijn) op de onderkant: oost (onder J9 langs), noord langs x 49,4 (tussen de
    # NTC-connector en de uitbreidingsheader), oost tussen J7 en J4 door, en zuid naar de ESP-via's
    h = (USB_W + USB_GAP) / 2
    yc = (u3y + u1y) / 2
    top = 19.2                                   # tussen J7 (onderste pad 17,0) en J4 (bovenste pad 21,2)
    xv = 49.4
    xs = vx + 0.75
    xturn = ex - 1.55
    centre = [(xs, yc), (xv - 1.0, yc), (xv, yc - 1.0), (xv, top + 1.0), (xv + 1.0, top), (xturn, top),
              (xturn, e13y - 0.8)]
    left, right = _offset(centre, h), _offset(centre, -h)          # links = D-, rechts = D+
    # einde: D- schuin naar via 13, D+ verder omlaag en evenwijdig schuin (0,6 mm hart-op-hart) naar via 14
    lx, ly = left[-1]
    dm_end = [(lx + (e13y - ly), e13y), (ex, e13y)]
    c2 = (lx - ly) - 0.85
    rx, ry = right[-1]
    y2 = max(ry, rx - c2)
    xe = min(ex, c2 + e14y)
    dp_end = [(rx, y2), (xe, e14y)] + ([(ex, e14y)] if xe < ex else [])
    _poly(board, dm, [(vx, u3y)] + left + dm_end, USB_W, B)
    _poly(board, dp, [(vx, u1y)] + right + dp_end, USB_W, B)
    return (xr, (ya7 + yb7) / 2), (v0x, v0y)
