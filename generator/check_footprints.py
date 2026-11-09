"""Controleert per onderdeel of de pinnummers van het symbool overeenkomen met de padnummers
van de footprint. Een mismatch betekent dat een net op de PCB op de verkeerde pad belandt
(of dat een pad zwevend blijft)."""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
from sexp import get_symbol, pins  # noqa: E402
from design import COMPONENTS  # noqa: E402

ROOT = os.path.join(os.path.dirname(__file__), '..', 'hardware', 'cv_monitor')
KSYM = '/usr/share/kicad/symbols'
KFP = '/usr/share/kicad/footprints'


def sym_pins(lib_id):
    lib, name = lib_id.split(':')
    path = os.path.join(ROOT, 'cv_monitor.kicad_sym') if lib == 'cv_monitor' else f'{KSYM}/{lib}.kicad_sym'
    blk = get_symbol(path, name)
    m = re.search(r'\(extends "([^"]+)"\)', blk[:300])
    if m:
        blk = get_symbol(path, m.group(1))
    return {p['number'] for p in pins(blk)}


def fp_pads(fp):
    lib, name = fp.split(':')
    path = os.path.join(ROOT, 'cv_monitor.pretty', name + '.kicad_mod') if lib == 'cv_monitor' \
        else f'{KFP}/{lib}.pretty/{name}.kicad_mod'
    txt = open(path).read()
    return set(re.findall(r'\(pad "?([^"\s)]*)"?\s', txt))


errors = 0
seen = set()
for c in COMPONENTS:
    key = (c['lib'], c['fp'])
    if key in seen:
        continue
    seen.add(key)
    sp = sym_pins(c['lib'])
    fpp = fp_pads(c['fp'])
    mech = {p for p in fpp if p in ('', 'MP') or not p}
    missing = sp - fpp            # symboolpin zonder pad
    extra = fpp - sp - mech       # pad zonder symboolpin (zou zwevend zijn)
    status = 'OK ' if not missing and not extra else 'FOUT'
    if missing or extra:
        errors += 1
    print(f'{status} {c["ref"]:4} {c["lib"]:40} {c["fp"].split(":")[1][:45]:45} '
          f'{"ontbreekt op footprint: " + str(sorted(missing)) if missing else ""}'
          f'{" zwevende pads: " + str(sorted(extra)) if extra else ""}'
          f'{" (mech: " + str(sorted(mech)) + ")" if mech else ""}')
print(f'\n{len(seen)} symbool/footprint-combinaties, {errors} met mismatch')
sys.exit(1 if errors else 0)
