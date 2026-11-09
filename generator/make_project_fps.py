"""Maakt projectvarianten van standaard-footprints in hardware/cv_monitor/cv_monitor.pretty.

1) ESP32-S3-WROOM-1_HandSolder, handsoldeer-variant van ESP32-S3-WROOM-1:
- randpads 1-40 worden 1,0 mm langer naar buiten (ruimte voor de soldeerbout)
- de via's in het GND-pad (41) krijgen een gat van 0,4 mm i.p.v. 0,2 mm, zodat je het
  GND-pad van de achterkant kunt solderen (soldeer loopt door de via's naar boven)
2) TP4056-footprint (SOIC-8 met thermische via's) met via-gaten van 0,3 mm i.p.v. 0,2 mm,
   zodat het binnen de standaardregels (en het standaardtarief) van JLCPCB valt.

Gebruik: python3 generator/make_project_fps.py <map .pretty>
"""
import os
import re
import sys

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
open(dst, 'w').write(txt)
print(f'{n} randpads verlengd, {v} GND-via\'s vergroot -> {dst}')

# ---- 2) TP4056: thermische via's 0,3 mm
SRC2 = '/usr/share/kicad/footprints/Package_SO.pretty/SOIC-8-1EP_3.9x4.9mm_P1.27mm_EP2.41x3.3mm_ThermalVias.kicad_mod'
NAME2 = 'SOIC-8-1EP_3.9x4.9mm_P1.27mm_EP2.41x3.3mm_ThermalVias_0.3mm'
t2 = open(SRC2).read()
t2 = re.sub(r'^\(footprint "?[^"\s]+"?', f'(footprint "{NAME2}"', t2, count=1)
t2, v2 = re.subn(r'\(size 0\.5 0\.5\) \(drill 0\.2\)', '(size 0.6 0.6) (drill 0.3)', t2)
open(os.path.join(outdir, NAME2 + '.kicad_mod'), 'w').write(t2)
print(f'{v2} thermische via\'s naar 0,3 mm -> {NAME2}')
