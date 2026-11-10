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


def silk_text_checks(board):
    """Silkscreen-afspraken: alle zichtbare tekst horizontaal (0°) en geen tekst op de fab-laag
    terwijl hij op silk had gemoeten. Geeft een lijst met afwijkingen terug."""
    issues = []
    silk = (pcbnew.F_SilkS, pcbnew.B_SilkS)
    texts = [(fp.GetReference(), t) for fp in board.GetFootprints()
             for t in (fp.Reference(), fp.Value()) if t.IsVisible()]
    texts += [(fp.GetReference(), t) for fp in board.GetFootprints()
              for t in fp.GraphicalItems() if isinstance(t, pcbnew.FP_TEXT) and t.IsVisible()]
    texts += [('bord', t) for t in board.GetDrawings() if isinstance(t, pcbnew.PCB_TEXT)]
    for owner, t in texts:
        if t.GetLayer() not in silk:
            continue
        rot = t.GetDrawRotation().AsDegrees() if hasattr(t, 'GetDrawRotation') else t.GetTextAngle().AsDegrees()
        if abs(((rot + 180) % 360) - 180) > 0.01:
            issues.append(f'{owner}: tekst "{t.GetShownText()}" staat op {rot:.0f}°')
    return issues


def passive_orientation(board):
    """Afspraak: alle R's, C's, diodes en LED's horizontaal (0° of 180°)."""
    issues = []
    for fp in board.GetFootprints():
        ref = fp.GetReference()
        if ref.rstrip('0123456789') in ('R', 'C', 'D', 'F'):
            o = fp.GetOrientationDegrees() % 180
            if abs(o) > 0.01:
                issues.append(f'{ref}: staat op {fp.GetOrientationDegrees():.0f}° (moet horizontaal)')
    return issues
