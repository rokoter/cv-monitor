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
    def __init__(self, board, ox, oy, w, h, r, side='F'):
        self.board = board
        self.side = side
        self.layer = pcbnew.F_SilkS if side == 'F' else pcbnew.B_SilkS
        self.bx = (mm(ox), mm(oy), mm(ox + w), mm(oy + h))
        self.r = mm(r)
        self.pads, self.silk, self.crt, self.texts = [], [], {}, []
        for fp in board.GetFootprints():
            same = fp.IsFlipped() == (side == 'B')
            for p in fp.Pads():
                if same or p.GetAttribute() in (pcbnew.PAD_ATTRIB_PTH, pcbnew.PAD_ATTRIB_NPTH):
                    self.pads.append(_infl(_box(p.GetBoundingBox()), PAD_CLR))
            for it in fp.GraphicalItems():
                if it.GetLayer() == self.layer and it.GetClass() != 'FP_TEXT':
                    self.silk.append(_infl(_box(it.GetBoundingBox()), 0.1))
            if not same:
                continue
            cy = fp.GetCourtyard(pcbnew.F_CrtYd if side == 'F' else pcbnew.B_CrtYd)
            if cy.OutlineCount():
                self.crt[fp.GetReference()] = _box(cy.BBox())
        for d in board.GetDrawings():
            if d.GetLayer() == self.layer:
                self.texts.append(_infl(_box(d.GetBoundingBox()), 0.15))

    def place_dir(self, text, own_ref, pad_box, direction, angle, size=TEXT_H, offset=0.0):
        """Pinlabel: alleen in één richting naast de pad zoeken (consistente rij labels)."""
        text.SetTextSize(pcbnew.VECTOR2I(mm(size), mm(size)))
        text.SetTextThickness(mm(TEXT_W))
        _set_angle(text, angle)
        l, t, r, b = pad_box
        cx, cy = (l + r) // 2, (t + b) // 2
        text.SetPosition(pcbnew.VECTOR2I(cx, cy))
        tb = _box(text.GetBoundingBox())
        hw, hh = (tb[2] - tb[0]) // 2, (tb[3] - tb[1]) // 2
        for gap in (0.35, 0.6, 0.9, 1.3):
            g = mm(gap + offset)
            x, y = {'left': (l - g - hw, cy), 'right': (r + g + hw, cy),
                    'up': (cx, t - g - hh), 'down': (cx, b + g + hh)}[direction]
            text.SetPosition(pcbnew.VECTOR2I(int(x), int(y)))
            bb = _box(text.GetBoundingBox())
            if self._ok(bb, own_ref, False):
                if hasattr(text, 'SetLocalCoord'):
                    text.SetLocalCoord()
                self.texts.append(_infl(bb, 0.1))
                return True
        return False

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
            _set_angle(text, 0)
            for k in (-0.3, 0.3, -0.15, 0.15, -0.4, 0.4):
                text.SetPosition(pcbnew.VECTOR2I(cx, int(cy + k * (b - t))))
                bb = _box(text.GetBoundingBox())
                if self._ok(bb, own_ref, False):
                    if hasattr(text, 'SetLocalCoord'):
                        text.SetLocalCoord()
                    self.texts.append(_infl(bb, 0.15))
                    return True
        # volgorde: eerst recht boven/onder/links/rechts dichtbij, dan schuin (hoeken), dan verder weg.
        # Zo blijft een referentie zo eenduidig mogelijk bij zijn eigen onderdeel.
        _set_angle(text, 0)              # alle tekst horizontaal: leesbaar vanuit één kant
        text.SetPosition(pcbnew.VECTOR2I(cx, cy))
        tb = _box(text.GetBoundingBox())
        hw, hh = (tb[2] - tb[0]) // 2, (tb[3] - tb[1]) // 2
        sides = lambda g: [(cx, t - g - hh), (cx, b + g + hh), (l - g - hw, cy), (r + g + hw, cy)]
        corners = lambda g: [(l - g - hw, t - g - hh), (r + g + hw, t - g - hh),
                             (l - g - hw, b + g + hh), (r + g + hw, b + g + hh)]
        steps = [(sides, (0.15, 0.5, 1.0)), (corners, (0.15, 0.5)), (sides, (1.6, 2.4)), (corners, (1.0, 1.6, 2.4))]
        for strict in (True, False):
            for fn, gaps in steps:
                for gap in gaps:
                    for (x, y) in fn(mm(gap)):
                        text.SetPosition(pcbnew.VECTOR2I(int(x), int(y)))
                        bb = _box(text.GetBoundingBox())
                        if self._ok(bb, own_ref, strict):
                            if hasattr(text, 'SetLocalCoord'):
                                text.SetLocalCoord()
                            self.texts.append(_infl(bb, 0.15))
                            return True
        return False


def _set_angle(text, ang):
    """Absolute teksthoek. KiCad 7 slaat de hoek van een footprinttekst (FP_TEXT) op t.o.v. de footprint."""
    if isinstance(text, pcbnew.FP_TEXT):
        ang -= pcbnew.Cast_to_FOOTPRINT(text.GetParent()).GetOrientationDegrees()
    text.SetTextAngle(pcbnew.EDA_ANGLE(ang, pcbnew.DEGREES_T))


def _new_text(board, txt, layer):
    t = pcbnew.PCB_TEXT(board)
    t.SetText(txt)
    t.SetLayer(layer)
    if layer == pcbnew.B_SilkS:
        t.SetMirrored(True)
    board.Add(t)
    return t


def place_pin_labels(board, ox, oy, w, h, r, pin_labels):
    """pin_labels: {ref: (richting, hoek, {padnummer: tekst})} -> labels op de onderkant (B.SilkS)."""
    sp = SilkPlacer(board, ox, oy, w, h, r, side='B')
    fps = {f.GetReference(): f for f in board.GetFootprints()}
    failed = []
    for ref, (direction, angle, labels, *opt) in pin_labels.items():
        stagger = 'stagger' in opt      # om en om in twee rijen (labels breder dan de pinafstand)
        for i, pad in enumerate(sorted(fps[ref].Pads(), key=lambda p: int(p.GetNumber() or 0))):
            txt = labels.get(pad.GetNumber())
            if not txt:
                continue
            t = _new_text(board, txt, pcbnew.B_SilkS)
            off = 1.9 if (stagger and i % 2) else 0.0   # 1 tekstregel (incl. marge) lager
            if not sp.place_dir(t, ref, _box(pad.GetBoundingBox()), direction, angle, offset=off):
                board.Remove(t)
                failed.append(f'{ref}.{pad.GetNumber()}')
    return failed


def place_all(board, ox, oy, w, h, r, label_override=None, hide=(), inner=(), func_labels=None,
              func_labels_back=None, func_dir=None, manual=()):
    """Plaatst functielabels en referenties op boven- en onderkant.
    label_override: {ref: tekst} i.p.v. de referentie (bijv. netnaam bij testpunten)
    func_labels / func_labels_back: extra functietekst (boven / onder)
    func_dir: {ref: richting} -> functielabel vast in die richting (bijv. 'up' voor een rij knoppen)
    hide: referenties die niet geprint worden; manual: referenties die al met de hand staan."""
    label_override = label_override or {}
    func_dir = func_dir or {}
    failed = []
    for side, funcs in (('F', func_labels or {}), ('B', func_labels_back or {})):
        sp = SilkPlacer(board, ox, oy, w, h, r, side=side)
        layer = sp.layer
        fps = [f for f in board.GetFootprints() if f.IsFlipped() == (side == 'B')]
        fps.sort(key=lambda f: -_area(f))     # grote onderdelen eerst
        own_of = {}
        for fp in fps:
            ref = fp.GetReference()
            if ref in inner:     # module: binnen de pads zoeken (courtyard bevat ook de antennezone)
                pb = [_box(p.GetBoundingBox()) for p in fp.Pads()]
                own_of[ref] = (min(q[0] for q in pb), min(q[1] for q in pb), max(q[2] for q in pb), max(q[3] for q in pb))
            else:
                own_of[ref] = sp.crt.get(ref) or _box(fp.GetBoundingBox(False, False))
        # 1) functielabels met vaste richting, 2) overige functielabels, 3) referenties
        for fixed in (True, False):
            for fp in fps:
                ref = fp.GetReference()
                if ref not in funcs or (ref in func_dir) != fixed:
                    continue
                t = _new_text(board, funcs[ref], layer)
                ok = (sp.place_dir(t, ref, own_of[ref], func_dir[ref], 0) if fixed
                      else sp.place(t, ref, own_of[ref]))
                if not ok:
                    board.Remove(t)
                    failed.append(ref + ' (functie)')
        for fp in fps:
            fp.Value().SetVisible(False)
            ref = fp.GetReference()
            rt = fp.Reference()
            if ref in manual:
                continue
            if ref in hide:
                rt.SetVisible(False)
                continue
            if ref in label_override:
                rt.SetVisible(False)
                t = _new_text(board, label_override[ref], layer)
                if not sp.place(t, ref, own_of[ref]):
                    board.Remove(t)
                    failed.append(ref)
                continue
            rt.SetLayer(layer)
            if side == 'B':
                rt.SetMirrored(True)
            if func_dir.get(ref) in ('up', 'down') and ref in funcs:
                ok = sp.place_dir(rt, ref, own_of[ref], func_dir[ref], 0, offset=1.4)   # boven/onder het functielabel
            else:
                ok = sp.place(rt, ref, own_of[ref], inner=ref in inner)
            if not ok:
                rt.SetLayer(pcbnew.F_Fab if side == 'F' else pcbnew.B_Fab)
                failed.append(ref)
    return failed


def _area(fp):
    b = fp.GetBoundingBox(False, False)
    return b.GetWidth() * b.GetHeight()
