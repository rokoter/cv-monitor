"""Genereert cv_monitor.kicad_sch (KiCad 7-formaat) uit een leesbare onderdelen- en netlijst.

Opzet: elk onderdeel heeft een positie en een mapping pin -> net. De generator tekent
korte draadjes vanaf elke pin met een netlabel of voedingssymbool. Optioneel kunnen pinnen
direct met een draad verbonden worden (WIRES) voor kleine lokale schakelingen.
"""
import json
import os
import sys
import uuid as _uuid

sys.path.insert(0, os.path.dirname(__file__))
from sexp import get_symbol, pins as parse_pins, extract_block  # noqa: E402

KSYM = '/usr/share/kicad/symbols'
PROJ = sys.argv[1]
PROJ_NAME = 'cv_monitor'
LOCAL_LIB = os.path.join(PROJ, 'cv_monitor.kicad_sym')

NS = _uuid.UUID('6f1c2a52-0000-4000-8000-c0ffee000001')


def U(*key):
    """Deterministische UUID zodat regeneratie stabiele bestanden geeft."""
    return str(_uuid.uuid5(NS, '/'.join(map(str, key))))


ROOT = U('root')
G = 2.54


def g(v):
    return round(v * G, 4)


# --------------------------------------------------------------------------- symbolen
def lib_path(lib):
    return LOCAL_LIB if lib == 'cv_monitor' else os.path.join(KSYM, lib + '.kicad_sym')


def children(block):
    """Top-level kind-blokken van een S-expr blok."""
    out, i, depth, in_str = [], 1, 0, False
    while i < len(block) - 1:
        c = block[i]
        if in_str:
            if c == '\\':
                i += 1
            elif c == '"':
                in_str = False
        elif c == '"':
            in_str = True
        elif c == '(':
            sub = extract_block(block, i)
            out.append(sub)
            i += len(sub)
            continue
        i += 1
    return out


SYMCACHE = {}


def load_symbol(lib_id):
    if lib_id in SYMCACHE:
        return SYMCACHE[lib_id]
    lib, name = lib_id.split(':')
    blk = get_symbol(lib_path(lib), name)
    kids = children(blk)
    ext = [k for k in kids if k.startswith('(extends ')]
    if ext:
        parent_name = ext[0].split('"')[1]
        pblk = get_symbol(lib_path(lib), parent_name)
        pkids = children(pblk)
        own_props = [k for k in kids if k.startswith('(property ')]
        body = [k for k in pkids if not k.startswith('(property ')]
        body = [k.replace(f'(symbol "{parent_name}_', f'(symbol "{name}_') for k in body]
        # attributen (in_bom, power, pin_names, ...) van de ouder overnemen
        head_attrs = pblk[len(f'(symbol "{parent_name}"'):pblk.find('(property ')]
        flat = f'(symbol "{lib_id}"{head_attrs}' + '\n'.join(own_props + body) + ')'
    else:
        flat = blk.replace(f'(symbol "{name}"', f'(symbol "{lib_id}"', 1)
    SYMCACHE[lib_id] = (flat, parse_pins(flat))
    return SYMCACHE[lib_id]


# --------------------------------------------------------------------------- geometrie
def rot(dx, dy, r):
    for _ in range((r // 90) % 4):
        dx, dy = dy, -dx
    return dx, dy


def pin_geom(comp, p):
    dx, dy = rot(p['x'], -p['y'], comp['rot'])
    ex, ey = comp['x'] + dx, comp['y'] + dy
    import math
    a = math.radians(p['rot'])
    ox, oy = rot(-round(math.cos(a)), round(math.sin(a)), comp['rot'])
    return (round(ex, 4), round(ey, 4)), (ox, oy)


# --------------------------------------------------------------------------- ontwerp
from design import COMPONENTS, WIRES, TEXTS, FLAGS, POWER_NETS  # noqa: E402

items = []
lib_ids = set()
pwr_count = [0]
flg_count = [0]


SEGS = []   # (a, b, net)
CUR_NET = [None]


def wire(a, b, key):
    SEGS.append((a, b, CUR_NET[0], key))
    items.append(f'  (wire (pts (xy {a[0]} {a[1]}) (xy {b[0]} {b[1]}))\n'
                 f'    (stroke (width 0) (type default))\n    (uuid {U("w", key)})\n  )')


def label(net, at, ang, key):
    just = {0: 'left bottom', 90: 'left bottom', 180: 'right bottom', 270: 'right bottom'}[ang]
    items.append(f'  (label "{net}" (at {at[0]} {at[1]} {ang}) (fields_autoplaced)\n'
                 f'    (effects (font (size 1.27 1.27)) (justify {just}))\n    (uuid {U("l", key)})\n  )')


def noconnect(at, key):
    items.append(f'  (no_connect (at {at[0]} {at[1]}) (uuid {U("nc", key)}))')


def text(t, at, size=1.27, bold=False, key=None):
    b = ' bold' if bold else ''
    t = t.replace('"', '\\"').replace('\n', '\\n')
    items.append(f'  (text "{t}" (at {at[0]} {at[1]} 0)\n'
                 f'    (effects (font (size {size} {size}){b}) (justify left bottom))\n    (uuid {U("t", key or t[:40])})\n  )')


def prop(name, val, at, hide=False, just=None, ang=0):
    j = f' (justify {just})' if just else ''
    h = ' hide' if hide else ''
    return (f'    (property "{name}" "{val}" (at {at[0]} {at[1]} {ang})\n'
            f'      (effects (font (size 1.27 1.27)){j}{h})\n    )\n')


def place_symbol(lib_id, ref, value, x, y, r=0, fp='', lcsc='', extra=None, ref_at=None,
                 val_at=None, dnp=False, in_bom=True, hide_ref=False, hide_val=False):
    flat, pins = load_symbol(lib_id)
    lib_ids.add(lib_id)
    ra = ref_at or (x + 2.54, y - 1.27)
    va = val_at or (x + 2.54, y + 1.27)
    s = f'  (symbol (lib_id "{lib_id}") (at {x} {y} {r}) (unit 1)\n'
    s += f'    (in_bom {"yes" if in_bom else "no"}) (on_board yes) (dnp {"yes" if dnp else "no"})\n'
    s += f'    (uuid {U("s", ref)})\n'
    fa = r if r in (90, 270) else 0
    s += prop('Reference', ref, ra, hide_ref, 'left', fa)
    s += prop('Value', value, va, hide_val, 'left', fa)
    if fp:                                  # alle footprints komen uit de projectbibliotheek
        fp = 'cv_monitor:' + fp.split(':')[-1]
    s += prop('Footprint', fp, (x, y), True)
    s += prop('Datasheet', '~', (x, y), True)
    if lcsc:
        s += prop('LCSC', lcsc, (x, y), True)
    for k, v in (extra or {}).items():
        s += prop(k, v, (x, y), True)
    for pn in sorted({p['number'] for p in pins}):
        s += f'    (pin "{pn}" (uuid {U("p", ref, pn)}))\n'
    s += (f'    (instances\n      (project "{PROJ_NAME}"\n        (path "/{ROOT}"\n'
          f'          (reference "{ref}") (unit 1)\n        )\n      )\n    )\n  )')
    items.append(s)
    return pins


def power_symbol(net, at, r, key):
    pwr_count[0] += 1
    ref = f'#PWR0{pwr_count[0]:02d}'
    lib_id = 'power:' + net
    off = (0, 3.81) if net == 'GND' else (0, -3.81)
    vat = (at[0] + rot(*off, r)[0], at[1] + rot(*off, r)[1])
    place_symbol(lib_id, ref, net, at[0], at[1], r, ref_at=at, val_at=vat, hide_ref=True)
    items[-1] = items[-1].replace('(justify left)', '')


def pwr_flag(at, r=0):
    flg_count[0] += 1
    ref = f'#FLG0{flg_count[0]:02d}'
    place_symbol('power:PWR_FLAG', ref, 'PWR_FLAG', at[0], at[1], r, ref_at=at,
                 val_at=(at[0], at[1] + (3.81 if r == 180 else -3.81)), hide_ref=True)
    items[-1] = items[-1].replace('(justify left)', '')


# ---- onderdelen plaatsen en pinnen aansluiten
wired_pins = set()
for w in WIRES:
    a, b = w[0], w[1]
    wired_pins.add(a)
    wired_pins.add(b)

endpoints = {}   # (ref,pin) -> (pos, outward)
PINPTS = []
expected = {}    # net -> set of (ref,pin)
comp_by_ref = {}
for c in COMPONENTS:
    c = dict(c)
    c['x'], c['y'] = g(c['gx']), g(c['gy'])
    c.setdefault('rot', 0)
    comp_by_ref[c['ref']] = c
    pins = place_symbol(c['lib'], c['ref'], c['value'], c['x'], c['y'], c['rot'], c.get('fp', ''),
                        c.get('lcsc', ''), c.get('extra'), dnp=c.get('dnp', False), in_bom=c.get('in_bom', True),
                        ref_at=c.get('ref_at') and (g(c['ref_at'][0]), g(c['ref_at'][1])),
                        val_at=c.get('val_at') and (g(c['val_at'][0]), g(c['val_at'][1])))
    seen_pos = {}
    for p in pins:
        net = c['nets'].get(p['number'])
        if net is None:
            if p['type'] == 'no_connect':
                continue
            raise SystemExit(f"{c['ref']} pin {p['number']} ({p['name']}) heeft geen net")
        pos, out = pin_geom(c, p)
        endpoints[(c['ref'], p['number'])] = (pos, out)
        if net != 'NC':
            expected.setdefault(net, set()).add((c['ref'], p['number']))
        if pos in seen_pos:          # gestapelde (verborgen) pinnen: één aansluiting
            if seen_pos[pos] != net:
                raise SystemExit(f"{c['ref']} gestapelde pinnen op {pos} met verschillende netten")
            continue
        seen_pos[pos] = net
        key = (c['ref'], p['number'])
        CUR_NET[0] = net
        PINPTS.append((pos, net, key))
        if net == 'NC':
            noconnect(pos, key)
            continue
        if key in wired_pins and not c.get('label_wired', {}).get(p['number']):
            continue
        stub = c.get('stub', {}).get(p['number'], 2.54)
        end = (round(pos[0] + out[0] * stub, 4), round(pos[1] + out[1] * stub, 4))
        if stub:
            wire(pos, end, key)
        if net in POWER_NETS:
            want = (0, 1) if net == 'GND' else (0, -1)
            if out == want:
                power_symbol(net, end, 0, key)
            elif c.get('pwr_rotate'):
                r = next(r for r in (0, 90, 180, 270) if rot(*want, r) == out)
                power_symbol(net, end, r, key)
            else:
                end2 = (end[0] + want[0] * 2.54, end[1] + want[1] * 2.54)
                wire(end, end2, key + ('b',))
                power_symbol(net, end2, 0, key)
        else:
            ang = {(1, 0): 0, (-1, 0): 180, (0, -1): 0, (0, 1): 0}[out]
            label(net, end, ang, key)

for w in WIRES:
    a, b = w[0], w[1]
    CUR_NET[0] = comp_by_ref[a[0]]['nets'][a[1]]
    pa, pb = endpoints[a][0], endpoints[b][0]
    if len(w) > 2:
        label(w[2], ((pa[0] + pb[0]) / 2, (pa[1] + pb[1]) / 2), 0, a + b + ('ml',))
    if pa[0] != pb[0] and pa[1] != pb[1]:      # L-vorm
        mid = (pb[0], pa[1])
        wire(pa, mid, a + b)
        wire(mid, pb, b + a)
    else:
        wire(pa, pb, a + b)

for kind, net, gx, gy in FLAGS:
    at = (g(gx), g(gy))
    CUR_NET[0] = net
    if kind == 'power':
        pwr_flag(at, 0 if net == 'GND' else 180)
        power_symbol(net, at, 0, ('flag', net))
    else:
        pwr_flag(at, 180)
        label(net, at, 0, ('flag', net))

for t in TEXTS:
    text(t['t'], (g(t['gx']), g(t['gy'])), t.get('size', 1.27), t.get('bold', False), key=t['t'][:30] + str(t['gx']))

# --------------------------------------------------------------------------- geometrische controle
def on_seg(pt, a, b):
    (x, y), (x1, y1), (x2, y2) = pt, a, b
    eps = 1e-3
    if abs((x2 - x1) * (y - y1) - (y2 - y1) * (x - x1)) > eps:
        return False
    return min(x1, x2) - eps <= x <= max(x1, x2) + eps and min(y1, y2) - eps <= y <= max(y1, y2) + eps


pts = [(p, n, k) for p, n, k in PINPTS if n != 'NC']
for a, b, n, k in SEGS:
    pts += [(a, n, k), (b, n, k)]
bad = 0
for a, b, n, k in SEGS:
    for p, n2, k2 in pts:
        if n2 != n and on_seg(p, a, b):
            print('KORTSLUITING', n, k, '<->', n2, k2, 'op', p)
            bad += 1
print('geometrie:', bad, 'conflicten')

# --------------------------------------------------------------------------- uitvoer
libsyms = '\n'.join('    ' + load_symbol(l)[0].replace('\n', '\n    ') for l in sorted(lib_ids))
out = f'''(kicad_sch (version 20230121) (generator eeschema)
  (uuid {ROOT})
  (paper "A3")
  (title_block
    (title "CV temperatuurmonitor - aanvoer/retour")
    (date "2026-11-09")
    (rev "0.5")
    (comment 1 "ESP32-S3 + 2x DS18B20 + 18650 UPS via USB-C + Qwiic + OLED/e-ink")
    (comment 2 "Opdrachtgever/controle: Koen - uitvoering: Claude")
  )
  (lib_symbols
{libsyms}
  )
{chr(10).join(items)}
  (sheet_instances
    (path "/" (page "1"))
  )
)
'''
open(os.path.join(PROJ, f'{PROJ_NAME}.kicad_sch'), 'w').write(out)
exp_out = {k: sorted(map(list, v)) for k, v in expected.items()}
exp_out['__flags__'] = [f[1] for f in FLAGS]
json.dump(exp_out,
          open(os.path.join(os.path.dirname(__file__), 'expected_nets.json'), 'w'), indent=1)
print('schema geschreven:', len(COMPONENTS), 'onderdelen,', len(expected), 'netten')
