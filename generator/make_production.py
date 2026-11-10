"""Productiebestanden voor JLCPCB (PCB + Economic PCBA).

Maakt in hardware/cv_monitor/production/:
  cv_monitor_<rev>_gerber.zip   Gerbers (4 lagen + masker, pasta, silk, rand) en Excellon-boorbestanden
  cv_monitor_<rev>_bom.csv      BOM in JLCPCB-formaat (Comment, Designator, Footprint, LCSC Part #)
  cv_monitor_<rev>_cpl.csv      plaatsingsbestand (Designator, Mid X, Mid Y, Layer, Rotation)
Alleen onderdelen die niet als DNP/buiten-BOM gemarkeerd zijn en een LCSC-nummer hebben, komen in BOM/CPL.
De boor-/plaatsingsoorsprong ligt linksonder op het bord, zodat alle coördinaten positief zijn.

Gebruik: /usr/bin/python3 generator/make_production.py <bord.kicad_pcb> <rev>
"""
import csv
import os
import re
import shutil
import subprocess
import sys
import zipfile

import pcbnew

OX, OY, W, H = 100.0, 100.0, 94.0, 70.0
LAYERS = 'F.Cu,In1.Cu,In2.Cu,B.Cu,F.Paste,B.Paste,F.SilkS,B.SilkS,F.Mask,B.Mask,Edge.Cuts'

# JLCPCB gebruikt voor sommige behuizingen een andere 0°-stand dan KiCad. Alleen correcties die
# algemeen bekend zijn; alle gepolariseerde onderdelen controleren we in de JLCPCB-preview.
ROT_FIX = [
    (r'^SOT-23', 180),          # SOT-23, SOT-23-5, SOT-23-6
    (r'^SOIC-', 270),
    (r'^TSSOP-', 270),
]
CHECK_IN_PREVIEW = [r'^USB_C_', r'^JST_SH_', r'^D_SMA', r'^D_SOD-', r'^LED_', r'^SW_Push', r'^SOT-', r'^SOIC-', r'^TSSOP-']


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f'mislukt: {" ".join(cmd)}\n{r.stdout}\n{r.stderr}')


def main(path, rev):
    prj = os.path.dirname(os.path.abspath(path))
    out = os.path.join(prj, 'production')
    tmp = os.path.join(out, 'tmp')
    shutil.rmtree(tmp, ignore_errors=True)
    os.makedirs(tmp)

    board = pcbnew.LoadBoard(path)
    origin = pcbnew.VECTOR2I(pcbnew.FromMM(OX), pcbnew.FromMM(OY + H))
    board.GetDesignSettings().SetAuxOrigin(origin)
    pcbnew.SaveBoard(path, board)

    # --- Gerbers en boorbestanden
    run(['kicad-cli', 'pcb', 'export', 'gerbers', '--layers', LAYERS, '--subtract-soldermask',
         '--use-drill-file-origin', '-o', tmp + '/', path])
    run(['kicad-cli', 'pcb', 'export', 'drill', '--format', 'excellon', '--drill-origin', 'plot',
         '--excellon-units', 'mm', '--excellon-separate-th', '-o', tmp + '/', path])
    files = sorted(f for f in os.listdir(tmp) if not f.endswith('.gbrjob'))
    gz = os.path.join(out, f'cv_monitor_{rev}_gerber.zip')
    with zipfile.ZipFile(gz, 'w', zipfile.ZIP_DEFLATED) as z:
        for f in files:
            z.write(os.path.join(tmp, f), f)

    # --- BOM en CPL
    groups, cpl, missing, check = {}, [], [], []
    for fp in board.GetFootprints():
        ref = fp.GetReference()
        attrs = fp.GetAttributes()
        if attrs & pcbnew.FP_EXCLUDE_FROM_BOM:
            continue
        lcsc = fp.GetProperty('LCSC') if fp.HasProperty('LCSC') else ''
        name = fp.GetFPID().GetLibItemName().wx_str()
        if not lcsc:
            missing.append(ref)
            continue
        key = (name, lcsc)                                  # per uniek onderdeel één regel
        groups.setdefault(key, []).append((ref, fp.GetValue()))
        if attrs & pcbnew.FP_EXCLUDE_FROM_POS_FILES:
            continue
        rot = fp.GetOrientationDegrees()
        for pat, add in ROT_FIX:
            if re.match(pat, name):
                rot += add
                break
        rot %= 360
        pos = fp.GetPosition()
        cpl.append((ref, round(pcbnew.ToMM(pos.x) - OX, 4), round(OY + H - pcbnew.ToMM(pos.y), 4),
                    'Bottom' if fp.IsFlipped() else 'Top', round(rot, 1)))
        if any(re.match(p, name) for p in CHECK_IN_PREVIEW):
            check.append(ref)

    def natural(r):
        m = re.match(r'([A-Z]+)(\d+)', r)
        return (m.group(1), int(m.group(2))) if m else (r, 0)

    bom = os.path.join(out, f'cv_monitor_{rev}_bom.csv')
    with open(bom, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['Comment', 'Designator', 'Footprint', 'LCSC Part #'])
        for (name, lcsc), items in sorted(groups.items(), key=lambda kv: natural(min((r for r, v in kv[1]), key=natural))):
            refs = sorted((r for r, v in items), key=natural)
            vals = []
            for r in refs:
                v = dict(items)[r]
                if v not in vals:
                    vals.append(v)
            w.writerow([' / '.join(vals), ','.join(refs), name, lcsc])
    cplf = os.path.join(out, f'cv_monitor_{rev}_cpl.csv')
    with open(cplf, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['Designator', 'Mid X', 'Mid Y', 'Layer', 'Rotation'])
        for row in sorted(cpl, key=lambda r: natural(r[0])):
            w.writerow(row)
    shutil.rmtree(tmp)
    print(f'{os.path.basename(gz)}: {len(files)} bestanden ({", ".join(files)})')
    print(f'{os.path.basename(bom)}: {len(groups)} regels, {sum(len(v) for v in groups.values())} onderdelen')
    print(f'{os.path.basename(cplf)}: {len(cpl)} posities')
    if missing:
        print('LET OP, in BOM maar zonder LCSC-nummer:', ', '.join(sorted(missing, key=natural)))
    print('in de JLCPCB-preview op stand/pin 1 controleren:', ', '.join(sorted(check, key=natural)))


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
