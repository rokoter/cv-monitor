"""Waarde, LCSC-nummers en DNP/BOM-vlaggen uit design.py overnemen in een (al gerouteerd) bord,
zonder plaatsing of routing te veranderen. Zelfde regels als make_pcb.py:
dnp of in_bom=False -> niet in BOM en niet in de positiebestanden (CPL), dnp -> ook DNP-markering.
Gebruik: /usr/bin/python3 generator/sync_attrs.py <bord.kicad_pcb>
"""
import os
import sys

import pcbnew

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from design import COMPONENTS  # noqa: E402

path = sys.argv[1]
prj = os.path.dirname(os.path.abspath(path))
board = pcbnew.LoadBoard(path)
fps = {f.GetReference(): f for f in board.GetFootprints()}
EXCL = pcbnew.FP_EXCLUDE_FROM_POS_FILES | pcbnew.FP_EXCLUDE_FROM_BOM | getattr(pcbnew, 'FP_DNP', 0)
changed = []
for c in COMPONENTS:
    fp = fps.get(c['ref'])
    if fp is None:
        continue
    lib = pcbnew.FootprintLoad(os.path.join(prj, 'cv_monitor.pretty'), fp.GetFPID().GetLibItemName().wx_str())
    attrs = (fp.GetAttributes() & ~EXCL) | (lib.GetAttributes() & EXCL)       # standaard van de footprint
    if c.get('dnp') or c.get('in_bom') is False:
        attrs |= pcbnew.FP_EXCLUDE_FROM_POS_FILES | pcbnew.FP_EXCLUDE_FROM_BOM
        if c.get('dnp'):
            attrs |= getattr(pcbnew, 'FP_DNP', 0)
    lcsc = c.get('lcsc', '')
    old = (fp.GetAttributes(), fp.GetProperty('LCSC') if fp.HasProperty('LCSC') else '', fp.GetValue())
    fp.SetAttributes(attrs)
    if lcsc:
        fp.SetProperty('LCSC', lcsc)
    fp.SetValue(c['value'])
    if old != (attrs, lcsc if lcsc else old[1], c['value']):
        changed.append(c['ref'])
pcbnew.SaveBoard(path, board)
print('bijgewerkt:', ', '.join(changed) if changed else 'niets')
