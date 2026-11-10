"""Routing-rapport: per net lengte, smalste spoor, aantal via's en lagen; plus controles:
- vermogensnetten minstens op de breedte van hun netklasse
- geen sporen/via's op de bovenlaag onder het ESP-module-lichaam
Gebruik: /usr/bin/python3 generator/route_report.py <bord.kicad_pcb>
"""
import math
import sys

import pcbnew

b = pcbnew.LoadBoard(sys.argv[1])
L = pcbnew.ToMM
stat = {}
for t in b.GetTracks():
    s = stat.setdefault(t.GetNetname(), dict(len=0.0, minw=99.0, vias=0, layers=set()))
    if t.GetClass() == 'PCB_VIA':
        s['vias'] += 1
        continue
    a, e = t.GetStart(), t.GetEnd()
    s['len'] += math.hypot(L(a.x - e.x), L(a.y - e.y))
    s['minw'] = min(s['minw'], L(t.GetWidth()))
    s['layers'].add(b.GetLayerName(t.GetLayer()))
print(f"{'net':18s} {'lengte':>8s} {'min':>5s} {'via':>4s}  lagen")
for n, s in sorted(stat.items(), key=lambda kv: -kv[1]['len']):
    print(f"{n:18s} {s['len']:7.1f}mm {s['minw']:5.2f} {s['vias']:4d}  {','.join(sorted(s['layers']))}")
fouten = []
want = {'VBUS': 0.8, 'VSYS': 0.8, 'BAT+': 0.8, 'CELL+': 0.8, 'VBUS_IN': 0.5, 'B-': 0.4}
info = []
for t in b.GetTracks():                      # versmallingen: kort stukje vlak bij een pin mag
    n = t.GetNetname()
    if t.GetClass() != 'PCB_TRACK' or n not in want or L(t.GetWidth()) >= want[n] - 1e-3:
        continue
    a, e = t.GetStart(), t.GetEnd()
    ln = math.hypot(L(a.x - e.x), L(a.y - e.y))
    near = any(p.GetNetname() == n and min(math.hypot(L(p.GetPosition().x - q.x), L(p.GetPosition().y - q.y))
                                           for q in (a, e)) < 2.5 for fp in b.GetFootprints() for p in fp.Pads())
    (info if (ln <= 2.0 and near) else fouten).append(
        f'{n}: {L(t.GetWidth()):.2f} mm over {ln:.1f} mm' + (' (versmalling bij pin)' if ln <= 2.0 and near else ''))
ko = [z for z in b.Zones() if z.GetIsRuleArea() and z.GetZoneName() == 'geen sporen onder ESP-module']
if ko:
    poly = ko[0].Outline()
    for t in b.GetTracks():
        if t.GetLayer() == pcbnew.F_Cu or t.GetClass() == 'PCB_VIA':
            pts = [t.GetPosition()] if t.GetClass() == 'PCB_VIA' else [t.GetStart(), t.GetEnd()]
            if any(poly.Contains(p) for p in pts):
                fouten.append(f'{t.GetNetname()}: {t.GetClass()} onder de ESP-module')
print(f"\n{sum(s['vias'] for s in stat.values())} via's, {sum(s['len'] for s in stat.values()):.0f} mm spoor")
for i in info:
    print('info:', i)
print('CONTROLE:', 'in orde' if not fouten else '\n  ' + '\n  '.join(fouten))
