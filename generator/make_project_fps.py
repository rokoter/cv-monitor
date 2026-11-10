"""Maakt projectvarianten van standaard-footprints in hardware/cv_monitor/cv_monitor.pretty.

1) ESP32-S3-WROOM-1_HandSolder, handsoldeer-variant van ESP32-S3-WROOM-1:
- randpads 1-40 worden 1,0 mm langer naar buiten (ruimte voor de soldeerbout)
- de via's in het GND-pad (41) krijgen een gat van 0,4 mm i.p.v. 0,2 mm, zodat je het
  GND-pad van de achterkant kunt solderen (soldeer loopt door de via's naar boven)
2) TP4056-footprint (SOIC-8 met thermische via's) met via-gaten van 0,3 mm i.p.v. 0,2 mm,
   zodat het binnen de standaardregels (en het standaardtarief) van JLCPCB valt.

3) Alle overige gebruikte standaard-footprints worden naar de projectbibliotheek gekopieerd
   (KiCad-bibliotheek, CC-BY-SA 4.0 met uitzondering voor gebruik in ontwerpen). Daardoor is het
   project op zichzelf staand: je eigen KiCad-versie (8/9/10) geeft geen 'footprint wijkt af van
   bibliotheek'-meldingen, en alle 3D-modellen wijzen naar ${KIPRJMOD}/3dmodels (in de repo).

Gebruik: python3 generator/make_project_fps.py <map .pretty>
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from design import COMPONENTS  # noqa: E402
from models3d import PREFIX, SUBST, EXTRA_BY_FP  # noqa: E402

KFP = '/usr/share/kicad/footprints'


def fix_models(txt, name):
    """Modelpaden -> ${KIPRJMOD}/3dmodels/<naam>.step (+ eventueel extra model, zoals de 18650-cel)."""
    def rep(m):
        stem = os.path.splitext(os.path.basename(m.group(1)))[0]
        return f'(model "{PREFIX}{SUBST.get(stem, stem)}.step"'
    txt = re.sub(r'\(model "?([^"\s)]+)"?', rep, txt)   # pad met of zonder aanhalingstekens
    for stem in EXTRA_BY_FP.get(name, []):
        blk = (f'  (model "{PREFIX}{stem}.step"\n    (offset (xyz 0 0 0))\n'
               f'    (scale (xyz 1 1 1))\n    (rotate (xyz 0 0 0))\n  )\n')
        txt = txt.rstrip()
        assert txt.endswith(')')
        txt = txt[:-1].rstrip() + '\n' + blk + ')\n'
    return txt


SRC = '/usr/share/kicad/footprints/RF_Module.pretty/ESP32-S3-WROOM-1.kicad_mod'
outdir = sys.argv[1]
dst = os.path.join(outdir, 'ESP32-S3-WROOM-1_HandSolder.kicad_mod')
txt = open(SRC).read()
txt = txt.replace('(footprint "ESP32-S3-WROOM-1"', '(footprint "ESP32-S3-WROOM-1_HandSolder"', 1)
txt = txt.replace('(descr "', '(descr "Handsoldeer-variant (langere pads, 0.4 mm GND-via\'s). ', 1)

EXT = 1.0


def smd(m):
    num, x, y, rot, sx, sy = m.group(1), float(m.group(2)), float(m.group(3)), m.group(4), float(m.group(5)), float(m.group(6))
    if abs(abs(x) - 8.75) < 0.01:          # linker/rechter kolom: pad loopt in x-richting
        x += EXT / 2 if x > 0 else -EXT / 2
    elif abs(y - 12.5) < 0.01:             # onderste rij: pad loopt in y-richting
        y += EXT / 2
    else:
        return m.group(0)
    rot_s = f' {rot}' if rot else ''
    return f'(pad "{num}" smd rect (at {x:.3f} {y:.3f}{rot_s}) (size {sx + EXT:.2f} {sy})'


txt, n = re.subn(r'\(pad "(\d+)" smd rect \(at ([-\d.]+) ([-\d.]+)(?: (\d+))?\) \(size ([\d.]+) ([\d.]+)\)', smd, txt)
txt, v = re.subn(r'(\(pad "41" thru_hole circle \(at [-\d. ]+\)) \(size 0\.6 0\.6\) \(drill 0\.2\)',
                 r'\1 (size 0.8 0.8) (drill 0.4)', txt)
open(dst, 'w').write(fix_models(txt, 'ESP32-S3-WROOM-1_HandSolder'))
print(f'{n} randpads verlengd, {v} GND-via\'s vergroot -> {dst}')

# ---- 2) TP4056: thermische via's 0,3 mm
SRC2 = '/usr/share/kicad/footprints/Package_SO.pretty/SOIC-8-1EP_3.9x4.9mm_P1.27mm_EP2.41x3.3mm_ThermalVias.kicad_mod'
NAME2 = 'SOIC-8-1EP_3.9x4.9mm_P1.27mm_EP2.41x3.3mm_ThermalVias_0.3mm'
t2 = open(SRC2).read()
t2 = re.sub(r'^\(footprint "?[^"\s]+"?', f'(footprint "{NAME2}"', t2, count=1)
t2, v2 = re.subn(r'\(size 0\.5 0\.5\) \(drill 0\.2\)', '(size 0.6 0.6) (drill 0.3)', t2)
open(os.path.join(outdir, NAME2 + '.kicad_mod'), 'w').write(fix_models(t2, NAME2))
print(f'{v2} thermische via\'s naar 0,3 mm -> {NAME2}')

# ---- 3) overige standaard-footprints in de projectbibliotheek
used = sorted({c['fp'] for c in COMPONENTS if c.get('fp') and not c['fp'].startswith('cv_monitor:')})
names = [f.split(':')[1] for f in used]
assert len(names) == len(set(names)), 'dubbele footprintnaam over bibliotheken heen'
for f in used:
    lib, name = f.split(':')
    t3 = open(f'{KFP}/{lib}.pretty/{name}.kicad_mod').read()
    open(os.path.join(outdir, name + '.kicad_mod'), 'w').write(fix_models(t3, name))
print(f'{len(used)} standaard-footprints naar de projectbibliotheek gekopieerd')
