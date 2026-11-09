"""Extra mechanische controles die de KiCad-DRC niet doet.

THT-pinnen en gaten gaan door het hele bord. Een through-hole pin van een onderdeel aan de
bovenkant mag dus niet binnen de courtyard van een onderdeel aan de onderkant vallen (en
andersom). KiCad vergelijkt courtyards alleen per zijde, dus dat vangt de DRC niet.
"""
import pcbnew


def tht_vs_other_side(board):
    errors = []
    fps = list(board.GetFootprints())
    for fp in fps:
        for pad in fp.Pads():
            if pad.GetAttribute() not in (pcbnew.PAD_ATTRIB_PTH, pcbnew.PAD_ATTRIB_NPTH):
                continue
            pos = pad.GetPosition()
            rad = max(pad.GetSizeX(), pad.GetSizeY()) // 2
            for other in fps:
                if other is fp or other.IsFlipped() == fp.IsFlipped():
                    continue
                layer = pcbnew.B_CrtYd if other.IsFlipped() else pcbnew.F_CrtYd
                cy = other.GetCourtyard(layer)
                if cy.OutlineCount() and cy.Collide(pos, rad):
                    errors.append(f'{fp.GetReference()} pad {pad.GetNumber() or "(gat)"} '
                                  f'@({pcbnew.ToMM(pos.x) - 100:.1f}, {pcbnew.ToMM(pos.y) - 100:.1f}) '
                                  f'gaat door {other.GetReference()} aan de '
                                  f'{"onderkant" if other.IsFlipped() else "bovenkant"}')
    return errors
