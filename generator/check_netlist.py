"""Vergelijkt de door KiCad geëxporteerde netlist met de bedoelde netten (expected_nets.json)
en voert een eenvoudige ERC uit: niet-aangedreven power_in, netten met één pin, kortsluitingen."""
import json
import re
import sys

net_file, exp_file = sys.argv[1], sys.argv[2]
txt = open(net_file).read()
raw = json.load(open(exp_file))
flags = set(raw.pop('__flags__', []))
expected = {k: {tuple(x) for x in v} for k, v in raw.items()}

nets = {}
types = {}
for m in re.finditer(r'\(net \(code "?\d+"?\) \(name "([^"]*)"\)(.*?)\)\s*(?=\(net |\)\s*\)\s*$)', txt, re.S):
    name, body = m.group(1).lstrip("/"), m.group(2)
    nodes = set()
    for n in re.finditer(r'\(node \(ref "([^"]+)"\) \(pin "([^"]+)"\)(?: \(pinfunction "[^"]*"\))?(?: \(pintype "([^"]*)"\))?', body):
        ref, pin, pt = n.groups()
        if ref.startswith('#'):
            types.setdefault(name, set()).add(pt or '')
            continue
        nodes.add((ref, pin))
        types.setdefault(name, set()).add(pt or '')
    nets[name] = nodes

errors = 0
# 1. elk bedoeld net moet precies als één KiCad-net terugkomen
pin2net = {}
for n, nodes in nets.items():
    for p in nodes:
        pin2net[p] = n
for want, pins in sorted(expected.items()):
    got = {pin2net.get(p) for p in pins}
    if None in got:
        missing = [p for p in pins if p not in pin2net]
        print(f'FOUT  {want}: pinnen niet aangesloten: {missing}')
        errors += 1
    elif len(got) > 1:
        print(f'FOUT  {want}: opgesplitst in {sorted(got)}')
        errors += 1
    else:
        real = got.pop()
        extra = nets[real] - pins
        if extra:
            print(f'FOUT  {want}: kortsluiting met {sorted(extra)}')
            errors += 1
# 2. eenvoudige ERC
for n, t in types.items():
    if 'power_in' in t and not ({'power_out'} & t) and n not in flags:
        print(f'ERC   {n}: power_in zonder voedingsbron/PWR_FLAG')
        errors += 1
for n, nodes in nets.items():
    if len(nodes) == 1 and not n.startswith('unconnected'):
        print(f'WARN  {n}: net met maar één pin {sorted(nodes)}')
print(f'{len(nets)} netten in KiCad, {len(expected)} bedoeld, {errors} fouten')
