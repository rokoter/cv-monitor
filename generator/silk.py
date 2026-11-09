"""Automatische plaatsing van silkscreen-referenties.

Per footprint wordt rond de courtyard gezocht naar een plek waar de referentie:
- binnen de bordrand valt (incl. afgeronde hoeken),
- niet over pads/gaten valt (silk wordt daar door de soldeermasker-opening afgeknipt),
- niet over silk-lijnen van footprints of andere teksten valt,
- bij voorkeur niet over een ander onderdeel (courtyard) valt.
Lukt dat niet, dan gaat de referentie naar de fab-laag (niet geprint) en wordt dat gemeld.
"""
import math

import pcbnew

mm = pcbnew.FromMM
TEXT_H = 1.0          # mm, JLCPCB-advies minimaal 1,0 mm
TEXT_W = 0.15         # mm lijndikte
PAD_CLR = 0.2         # mm vrije ruimte tussen silk en pad/maskeropening


def _box(b):
    return (b.GetLeft(), b.GetTop(), b.GetRight(), b.GetBottom())


def _infl(b, d):
    d = mm(d)
    return (b[0] - d, b[1] - d, b[2] + d, b[3] + d)


def _hit(a, b):
    return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]


class SilkPlacer:
    def __init__(self, board, ox, oy, w, h, r):
        self.board = board
        self.bx = (mm(ox), mm(oy), mm(ox + w), mm(oy + h))
        self.r = mm(r)
        self.pads, self.silk, self.crt, self.texts = [], [], {}, []
        for fp in board.GetFootprints():
            back = fp.IsFlipped()
            for p in fp.Pads():
                if not back or p.GetAttribute() in (pcbnew.PAD_ATTRIB_PTH, pcbnew.PAD_ATTRIB_NPTH):
                    self.pads.append(_infl(_box(p.GetBoundingBox()), PAD_CLR))
            if back:
                continue
            for it in fp.GraphicalItems():
                if it.GetLayer() == pcbnew.F_SilkS and it.GetClass() != 'FP_TEXT':
                    self.silk.append(_infl(_box(it.GetBoundingBox()), 0.1))
            cy = fp.GetCourtyard(pcbnew.F_CrtYd)
            if cy.OutlineCount():
                self.crt[fp.GetReference()] = _box(cy.BBox())
        for d in board.GetDrawings():
            if d.GetLayer() == pcbnew.F_SilkS:
                self.texts.append(_infl(_box(d.GetBoundingBox()), 0.15))

    def _inside_board(self, b):
        m = mm(0.3)
        x1, y1, x2, y2 = self.bx
        if b[0] < x1 + m or b[1] < y1 + m or b[2] > x2 - m or b[3] > y2 - m:
            return False
        r = self.r
        for cx, cy, px, py in ((x1 + r, y1 + r, b[0], b[1]), (x2 - r, y1 + r, b[2], b[1]),
                               (x1 + r, y2 - r, b[0], b[3]), (x2 - r, y2 - r, b[2], b[3])):
            inx = (px < cx) if cx < (x1 + x2) / 2 else (px > cx)
            iny = (py < cy) if cy < (y1 + y2) / 2 else (py > cy)
            if inx and iny and math.hypot(px - cx, py - cy) > r - m:
                return False
        return True

    def _ok(self, b, own, strict):
        if not self._inside_board(b):
            return False
        if any(_hit(b, o) for o in self.pads) or any(_hit(b, o) for o in self.texts):
            return False
        if any(_hit(b, o) for o in self.silk):
            return False
        if strict and any(_hit(b, c) for ref, c in self.crt.items() if ref != own):
            return False
        return True

    def place(self, text, own_ref, own_box, inner=False):
        """Zoek een plek voor 'text' (FP_TEXT of PCB_TEXT) rond own_box (nm).
        inner=True: eerst binnen own_box proberen (grote modules zonder onderdelen erin)."""
        text.SetTextSize(pcbnew.VECTOR2I(mm(TEXT_H), mm(TEXT_H)))
        text.SetTextThickness(mm(TEXT_W))
        l, t, r, b = own_box
        cx, cy = (l + r) // 2, (t + b) // 2
        if inner:
            text.SetTextAngle(pcbnew.EDA_ANGLE(0, pcbnew.DEGREES_T))
            for k in (-0.3, 0.3, -0.15, 0.15, -0.4, 0.4):
                text.SetPosition(pcbnew.VECTOR2I(cx, int(cy + k * (b - t))))
                bb = _box(text.GetBoundingBox())
                if self._ok(bb, own_ref, False):
                    if hasattr(text, 'SetLocalCoord'):
                        text.SetLocalCoord()
                    self.texts.append(_infl(bb, 0.15))
                    return True
        for strict in (True, False):
            for gap in (0.15, 0.5, 1.0, 1.6, 2.4):
                g = mm(gap)
                for ang in (0, 90):
                    text.SetTextAngle(pcbnew.EDA_ANGLE(ang, pcbnew.DEGREES_T))
                    text.SetPosition(pcbnew.VECTOR2I(cx, cy))
                    tb = _box(text.GetBoundingBox())
                    hw, hh = (tb[2] - tb[0]) // 2, (tb[3] - tb[1]) // 2
                    cands = [(cx, t - g - hh), (cx, b + g + hh), (l - g - hw, cy), (r + g + hw, cy),
                             (l - g - hw, t - g - hh), (r + g + hw, t - g - hh),
                             (l - g - hw, b + g + hh), (r + g + hw, b + g + hh)]
                    for (x, y) in cands:
                        text.SetPosition(pcbnew.VECTOR2I(int(x), int(y)))
                        bb = _box(text.GetBoundingBox())
                        if self._ok(bb, own_ref, strict):
                            if hasattr(text, 'SetLocalCoord'):
                                text.SetLocalCoord()
                            self.texts.append(_infl(bb, 0.15))
                            return True
        return False


def place_all(board, ox, oy, w, h, r, label_override=None, hide=(), inner=()):
    """Plaatst alle referenties. label_override: {ref: tekst} -> extra silk-tekst i.p.v. de referentie
    (bijv. netnaam bij testpunten). hide: referenties die niet geprint worden."""
    label_override = label_override or {}
    sp = SilkPlacer(board, ox, oy, w, h, r)
    failed = []
    fps = sorted(board.GetFootprints(), key=lambda f: -_area(f))   # grote onderdelen eerst
    for fp in fps:
        fp.Value().SetVisible(False)
        ref = fp.GetReference()
        rt = fp.Reference()
        if fp.IsFlipped():
            continue
        if ref in hide:
            rt.SetVisible(False)
            continue
        if ref in inner:     # module: zoek binnen de pads (de courtyard bevat ook de antennezone)
            pb = [_box(p.GetBoundingBox()) for p in fp.Pads()]
            own = (min(q[0] for q in pb), min(q[1] for q in pb), max(q[2] for q in pb), max(q[3] for q in pb))
        else:
            own = sp.crt.get(ref) or _box(fp.GetBoundingBox(False, False))
        if ref in label_override:
            rt.SetVisible(False)
            t = pcbnew.PCB_TEXT(board)
            t.SetText(label_override[ref])
            t.SetLayer(pcbnew.F_SilkS)
            board.Add(t)
            if not sp.place(t, ref, own):
                board.Remove(t)
                failed.append(ref)
            continue
        rt.SetLayer(pcbnew.F_SilkS)
        if not sp.place(rt, ref, own, inner=ref in inner):
            rt.SetLayer(pcbnew.F_Fab)
            failed.append(ref)
    return failed


def _area(fp):
    b = fp.GetBoundingBox(False, False)
    return b.GetWidth() * b.GetHeight()
