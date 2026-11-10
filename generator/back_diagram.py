"""Blokschema van de werking op de silkscreen aan de achterkant (B.SilkS).

Het schema wordt getekend in 'achteraanzicht'-coördinaten (u naar rechts, v omlaag, in mm, zoals je
het ziet als je het bord omdraait) en daarna gespiegeld naar bordcoördinaten: x = X0 - u, y = v.
Het staat in de bovenste helft van de achterkant (de onderste helft is de accuhouder), tussen de
pinnen van J7/J4 (links in achteraanzicht) en USB-C (rechts), om het via-veld van de lader (U2) heen.

    USB-C 5V ──────────┬──────> VSYS
       │               │          │
     LADER 0,6 A <─NTC │       3V3 LDO
       │               │          │
     BEVEILIGING       │       ESP32-S3
       │               │          │
     ACCU 18650 ───────┘   ┌──────┼───────┬─────────┐
                         1-WIRE  I2C     SPI       GPIO
                         AANVOER OLED    E-INK     UITBREIDING
                         RETOUR  QWIIC
"""
import pcbnew

mm = pcbnew.FromMM
LW = 0.18          # lijndikte (JLCPCB minimaal 0,15 mm)
TXT = (0.9, 1.0)   # tekstbreedte x hoogte (mm); hoogte 1,0 mm = JLCPCB-minimum
TXT_W = 0.15


class BackDiagram:
    def __init__(self, board, ox, oy, x0):
        self.board, self.ox, self.oy, self.x0 = board, ox, oy, x0
        self.layer = pcbnew.B_SilkS

    def P(self, u, v):
        return pcbnew.VECTOR2I(mm(self.ox + self.x0 - u), mm(self.oy + v))

    def _add(self, s):
        s.SetLayer(self.layer)
        self.board.Add(s)
        return s

    def line(self, u1, v1, u2, v2):
        s = pcbnew.PCB_SHAPE(self.board)
        s.SetShape(pcbnew.SHAPE_T_SEGMENT)
        s.SetStart(self.P(u1, v1))
        s.SetEnd(self.P(u2, v2))
        s.SetWidth(mm(LW))
        return self._add(s)

    def rect(self, u1, v1, u2, v2):
        for a, b, c, d in ((u1, v1, u2, v1), (u2, v1, u2, v2), (u2, v2, u1, v2), (u1, v2, u1, v1)):
            self.line(a, b, c, d)

    def text(self, t, u, v):
        tx = pcbnew.PCB_TEXT(self.board)
        tx.SetText(t)
        tx.SetLayer(self.layer)
        tx.SetMirrored(True)                      # leesbaar vanaf de achterkant
        tx.SetTextSize(pcbnew.VECTOR2I(mm(TXT[0]), mm(TXT[1])))
        tx.SetTextThickness(mm(TXT_W))
        tx.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_CENTER)
        tx.SetVertJustify(pcbnew.GR_TEXT_V_ALIGN_CENTER)
        tx.SetPosition(self.P(u, v))
        self.board.Add(tx)
        return tx

    def box(self, label, uc, vc, w, h=2.2):
        self.rect(uc - w / 2, vc - h / 2, uc + w / 2, vc + h / 2)
        self.text(label, uc, vc)

    def arrow(self, u1, v1, u2, v2, head=0.9, half=0.42):
        """Lijn van (u1,v1) naar (u2,v2) met een gevulde pijlpunt op het eind."""
        du, dv = u2 - u1, v2 - v1
        n = (du * du + dv * dv) ** 0.5
        du, dv = du / n, dv / n
        bu, bv = u2 - du * head, v2 - dv * head          # basis van de pijlpunt
        self.line(u1, v1, bu, bv)
        poly = pcbnew.SHAPE_POLY_SET()
        poly.NewOutline()
        for (a, b) in ((u2, v2), (bu - dv * half, bv + du * half), (bu + dv * half, bv - du * half)):
            poly.Append(self.P(a, b))
        s = pcbnew.PCB_SHAPE(self.board)
        s.SetShape(pcbnew.SHAPE_T_POLY)
        s.SetPolyShape(poly)
        s.SetFilled(True)
        s.SetWidth(mm(0.05))
        self._add(s)

    def dot(self, u, v, r=0.35):
        s = pcbnew.PCB_SHAPE(self.board)
        s.SetShape(pcbnew.SHAPE_T_CIRCLE)
        s.SetCenter(self.P(u, v))
        s.SetEnd(self.P(u + r, v))
        s.SetFilled(True)
        s.SetWidth(mm(0.05))
        self._add(s)


def draw(board, ox, oy, x0=48.5):
    d = BackDiagram(board, ox, oy, x0)
    H = 2.2                       # boxhoogte
    PW, PU = 15.0, 8.5            # vermogenskolom: breedte, midden (u)
    SW, SU = 11.0, 34.5           # systeemkolom: breedte, midden (u)
    r1, r2, r3, r4 = 8.6, 12.6, 16.6, 20.6     # rijen (v, midden van de boxen)
    JU = 27.0                     # verzamelpunt accu + USB -> VSYS

    d.text('WERKING', 20.5, 5.4)

    # vermogenskolom: USB -> lader -> beveiliging -> accu
    d.box('USB-C 5V', PU, r1, PW)
    d.box('LADER 0,6 A', PU, r2, PW)
    d.box('BEVEILIGING', PU, r3, PW)
    d.box('ACCU 18650', PU, r4, PW)
    for a, b in ((r1, r2), (r2, r3), (r3, r4)):
        d.arrow(PU, a + H / 2, PU, b - H / 2)
    d.arrow(19.6, r2, PU + PW / 2, r2)          # NTC -> lader
    d.text('NTC', 21.0, r2)

    # systeemkolom: VSYS -> 3V3 -> ESP32
    d.box('VSYS', SU, r1, SW)
    d.box('3V3 LDO', SU, r2, SW)
    d.box('ESP32-S3', SU, r3, SW)
    for a, b in ((r1, r2), (r2, r3)):
        d.arrow(SU, a + H / 2, SU, b - H / 2)

    # USB en accu samen naar VSYS (wie de hoogste spanning heeft levert)
    d.arrow(PU + PW / 2, r1, SU - SW / 2, r1)
    d.line(PU + PW / 2, r4, JU, r4)
    d.arrow(JU, r4, JU, r1 + 0.6)
    d.dot(JU, r1)

    # uitgangen van de ESP32
    vb, vt = 24.5, 26.6           # verdeellijn, bovenkant van de pijlpunten
    outs = [(5.0, ('1-WIRE', 'AANVOER', 'RETOUR')), (15.0, ('I2C', 'OLED', 'QWIIC')),
            (24.0, ('SPI', 'E-INK')), (SU, ('GPIO', 'UITBREIDING'))]
    d.line(SU, r3 + H / 2, SU, vb)
    d.line(outs[0][0], vb, SU, vb)
    d.dot(SU, vb)
    for u, lines in outs:
        d.arrow(u, vb, u, vt)
        for k, t in enumerate(lines):
            d.text(t, u, vt + 1.2 + 1.6 * k)
    return d
