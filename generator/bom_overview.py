"""Maakt docs/BOM_JLCPCB.md: welke onderdelen JLCPCB plaatst, welke Koen zelf soldeert,
en welke 'extended' zijn (opstartkosten per uniek onderdeel bij JLCPCB).

De classificatie is handmatig gecontroleerd op de JLCPCB-onderdeelpagina's (datum in de kop).
Definitief is altijd wat de BOM-tool van JLCPCB bij het bestellen laat zien.
"""
import os
import sys
from collections import OrderedDict

sys.path.insert(0, os.path.dirname(__file__))
from design import COMPONENTS  # noqa: E402

CHECKED = '2026-11-09'
# lcsc -> (klasse, opmerking)
JLC = {
    'C15127': ('Basic', ''), 'C8678': ('Basic', ''), 'C318884': ('Basic', ''),
    'C2913206': ('Extended', 'ESP32-S3-MINI: Standard PCBA + X-ray'),
    'C165948': ('Extended', ''), 'C7519': ('Extended', 'ESD, optioneel'),
    'C351410': ('Extended', ''), 'C5148694': ('Extended', 'vervangt uitverkochte C32254'),
    'C51118': ('Extended', ''), 'C523825': ('Extended', 'geen basic PTC beschikbaar'),
    'C160404': ('Extended', 'liggende JST-SH (Qwiic)'), 'C16581': ('Extended*', '*mogelijk "preferred" (geen toeslag)'),
}
BASIC_PASSIVE = {'C14663', 'C15849', 'C15850', 'C45783', 'C21190', 'C22775', 'C22975', 'C23162', 'C23186',
                 'C25803', 'C25804', 'C25819', 'C2286', 'C72041', 'C72043', 'C81598'}

lines = OrderedDict()
for c in COMPONENTS:
    fp = c.get('fp', '').split(':')[-1]
    key = (c.get('lcsc', ''), '' if c.get('lcsc') else c['ref'], fp)
    lines.setdefault(key, []).append(c)

jlc_rows, self_rows, n_ext = [], [], 0
for (lcsc, _, fp), comps in lines.items():
    refs = ', '.join(sorted((x['ref'] for x in comps), key=lambda r: (r.rstrip('0123456789'), int(r[len(r.rstrip('0123456789')):] or 0))))
    val = ' / '.join(dict.fromkeys(x['value'] for x in comps))
    if comps[0].get('dnp') or not lcsc:
        if fp.startswith('SolderJumper'):
            continue
        self_rows.append(f'| {refs} | {val} | {fp} |')
        continue
    cls, note = JLC.get(lcsc, ('Basic' if lcsc in BASIC_PASSIVE else '?', ''))
    if cls.startswith('Extended'):
        n_ext += 1
    jlc_rows.append(f'| {refs} | {val} | {fp} | {lcsc} | {cls} | {len(comps)} | {note} |')

out = [f'# BOM voor JLCPCB-assemblage\n',
       f'Gegenereerd uit `generator/design.py`. Klasse gecontroleerd op {CHECKED}; '
       'bij bestellen telt wat de JLCPCB-BOM-tool toont.\n',
       '## Door JLCPCB geplaatst (SMD)\n',
       '| Referenties | Waarde | Footprint | LCSC | Klasse | Aantal | Opmerking |',
       '|---|---|---|---|---|---|---|', *jlc_rows,
       f'\n**{len(jlc_rows)} unieke onderdelen, waarvan {n_ext} extended** '
       '(extended = eenmalige opstartkosten per uniek onderdeel per order).\n',
       '## Zelf solderen (THT, niet in de JLCPCB-BOM)\n',
       '| Referenties | Waarde | Footprint |', '|---|---|---|', *self_rows]
path = os.path.join(os.path.dirname(__file__), '..', 'docs', 'BOM_JLCPCB.md')
open(path, 'w').write('\n'.join(out) + '\n')
print(f'{len(jlc_rows)} JLCPCB-regels ({n_ext} extended), {len(self_rows)} zelf solderen -> docs/BOM_JLCPCB.md')
