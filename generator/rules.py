"""Ontwerpregels en netklassen in het KiCad-project (cv_monitor.kicad_pro) zetten.

Wordt aangeroepen na make_pcb.py (dat bij het opslaan een nieuw projectbestand schrijft) en vóór
het routen. JLCPCB 4-laags kan veel fijner; dit zijn ruime waarden voor een betrouwbaar prototype.
"""
import json
import sys

CLASSES = [
    # naam,     clearance, spoor, via-diameter, via-gat
    ('Default', 0.15, 0.2, 0.6, 0.3),
    ('Power',   0.2,  0.8, 0.8, 0.4),   # 5V na de zekering, VSYS, accu: tot ~1 A (lange accuweg: breed)
    ('PowerIn', 0.2,  0.5, 0.8, 0.4),   # USB-C VBUS-pinnen (0,5 mm steek): smaller
    ('Batt',    0.2,  0.4, 0.8, 0.4),   # B- (via de 8205A in TSSOP-8: 0,4 mm past op de pads)
    ('Supply',  0.2,  0.4, 0.6, 0.3),   # GND en 3V3 (vooral via de binnenvlakken)
]
PATTERNS = ([('Power', n) for n in ('VBUS', 'VSYS', 'BAT+', 'CELL+')] + [('PowerIn', 'VBUS_IN')] +
            [('Batt', 'B-')] + [('Supply', n) for n in ('GND', '+3V3')])
RULES = dict(min_copper_edge_clearance=0.3, min_track_width=0.15, min_clearance=0.15, min_via_diameter=0.5,
             min_through_hole_diameter=0.3, min_hole_clearance=0.25)


def apply(pro):
    d = json.load(open(pro))
    base = d['net_settings']['classes'][0]
    classes = []
    for name, clr, tw, vd, vdr in CLASSES:
        c = dict(base)
        c.update(name=name, clearance=clr, track_width=tw, via_diameter=vd, via_drill=vdr)
        classes.append(c)
    d['net_settings']['classes'] = classes
    d['net_settings']['netclass_patterns'] = [{'netclass': c, 'pattern': n} for c, n in PATTERNS]
    d['board']['design_settings']['rules'].update(RULES)
    json.dump(d, open(pro, 'w'), indent=2)


if __name__ == '__main__':
    apply(sys.argv[1])
    print('ontwerpregels en netklassen gezet:', ', '.join(c[0] for c in CLASSES))
