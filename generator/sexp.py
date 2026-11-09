"""Kleine helpers om KiCad S-expression bestanden te lezen (symbolen extraheren, pinnen tonen)."""
import re
import sys


def extract_block(text, start):
    """Geef het complete (…)-blok terug dat begint op index start."""
    depth = 0
    in_str = False
    i = start
    while i < len(text):
        c = text[i]
        if in_str:
            if c == '\\':
                i += 1
            elif c == '"':
                in_str = False
        else:
            if c == '"':
                in_str = True
            elif c == '(':
                depth += 1
            elif c == ')':
                depth -= 1
                if depth == 0:
                    return text[start:i + 1]
        i += 1
    raise ValueError("unbalanced")


def get_symbol(lib_path, name):
    text = open(lib_path, encoding="utf-8").read()
    idx = text.find(f'(symbol "{name}"')
    if idx < 0:
        raise KeyError(f"{name} niet gevonden in {lib_path}")
    return extract_block(text, idx)


PIN_RE = re.compile(
    r'\(pin (\w+) \w+\s*\(at ([-\d.]+) ([-\d.]+)(?: ([-\d.]+))?\)\s*\(length ([-\d.]+)\)(.*?)\(name "([^"]*)".*?\(number "([^"]*)"',
    re.S)


def pins(symbol_block):
    out = []
    for m in PIN_RE.finditer(symbol_block):
        out.append(dict(type=m.group(1), x=float(m.group(2)), y=float(m.group(3)),
                        rot=float(m.group(4) or 0), length=float(m.group(5)),
                        name=m.group(7), number=m.group(8)))
    return out


if __name__ == "__main__":
    lib, name = sys.argv[1], sys.argv[2]
    blk = get_symbol(lib, name)
    head = blk[:400].replace("\n", " ")
    print(head[:300])
    for p in pins(blk):
        print(p["number"], p["name"], p["type"], p["x"], p["y"], p["rot"])
