"""Controleert de JLCPCB-BOM tegen de actuele JLCPCB-voorraad en klasse (Basic/Preferred/Extended).

Bron: de dagelijks bijgewerkte data van https://github.com/yaqwsx/jlcparts (branch gh-pages).
Alleen de benodigde bestanden worden opgehaald (git sparse/lazy), ~5 MB en ~2-3 minuten.

Gebruik (vanuit de hoofdmap van de repo):
    python3 -I generator/jlc_check.py hardware/cv_monitor/production/cv_monitor_rev0.2_bom.csv
    python3 -I generator/jlc_check.py <bom.csv> --borden 5 --data /tmp/jlcparts C12624 C2288
Extra LCSC-nummers na de opties worden als kandidaat getoond.

Definitief blijft wat de BOM-tool van JLCPCB bij het bestellen laat zien.
"""
import argparse
import csv
import glob
import gzip
import json
import os
import subprocess
import tempfile

REPO = 'https://github.com/yaqwsx/jlcparts'


def git(cwd, *args):
    subprocess.run(['git', '-c', 'gc.auto=0', *args], cwd=cwd, check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def ensure_data(root):
    repo = os.path.join(root, 'repo')
    if not os.path.isdir(repo):
        os.makedirs(root, exist_ok=True)
        git(root, 'clone', '-q', '--depth', '1', '--branch', 'gh-pages', '--filter=blob:none',
            '--no-checkout', REPO, 'repo')
    data = os.path.join(repo, 'data')
    if not glob.glob(os.path.join(data, 'lookup-*.json.gz')):
        print('opzoektabellen ophalen (eenmalig, ~2 minuten)...')
        git(repo, 'checkout', '-q', 'HEAD', '--', 'data/attributes-lut.json.gz', 'data/lookup-*.json.gz')
    return repo, data


def fmt(attr):
    if not attr:
        return ''
    s = attr.get('format', '')
    for k, (v, _t) in attr.get('values', {}).items():
        s = s.replace('${%s}' % k, str(v))
    return s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('bom')
    ap.add_argument('kandidaten', nargs='*')
    ap.add_argument('--borden', type=int, default=5)
    ap.add_argument('--data', default=os.path.join(tempfile.gettempdir(), 'jlcparts'))
    a = ap.parse_args()

    rows = [r for r in csv.DictReader(open(a.bom)) if r.get('LCSC Part #')]
    codes = [r['LCSC Part #'] for r in rows] + a.kandidaten
    repo, data = ensure_data(a.data)

    where = {}
    for f in glob.glob(os.path.join(data, 'lookup-*.json.gz')):
        for k, v in json.load(gzip.open(f)).items():
            if k in codes:
                where[k] = v
    need = sorted(set(where.values()) - {os.path.basename(p) for p in glob.glob(os.path.join(data, '*.jsonl.gz'))})
    if need:
        git(repo, 'checkout', '-q', 'HEAD', '--', *('data/' + n for n in need))

    lut = json.load(gzip.open(os.path.join(data, 'attributes-lut.json.gz')))
    info = {}
    for name in set(where.values()):
        it = gzip.open(os.path.join(data, name), 'rt')
        h = json.loads(next(it))
        for line in it:
            r = json.loads(line)
            c = r[h['lcsc']]
            if c in codes:
                at = {lut[i][0]: lut[i][1] for i in r[h['attributes']]}
                info[c] = (fmt(at.get('Basic/Extended')), r[h['stock']], r[h['mfr']])

    problems, ext = 0, 0
    print(f'{"LCSC":10} {"Referenties":24} {"nodig":>5}  {"klasse":9} {"voorraad":>10}  onderdeel')
    for r in rows:
        c, refs = r['LCSC Part #'], r['Designator']
        n = len(refs.split(',')) * a.borden
        i = info.get(c)
        if i and i[0] == 'Extended':
            ext += 1
        bad = not i or i[1] < 2 * n
        problems += bad
        print(f'{c:10} {refs[:24]:24} {n:5}  ' +
              (f'{i[0]:9} {i[1]:10}  {i[2]}' if i else 'niet (meer) in de JLCPCB-bibliotheek') +
              ('   <-- PROBLEEM' if bad else ''))
    for c in a.kandidaten:
        i = info.get(c)
        print(f'kandidaat {c:10} ' + (f'{i[0]:9} {i[1]:10}  {i[2]}' if i else 'niet in de JLCPCB-bibliotheek'))
    print(f'\n{len(rows)} regels, {ext} extended (x $3,07 bij Economic PCBA), {problems} probleem/problemen '
          f'(voorraad < 2x nodig voor {a.borden} borden)')
    return 1 if problems else 0


if __name__ == '__main__':
    raise SystemExit(main())
