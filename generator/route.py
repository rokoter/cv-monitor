"""Routing-stap na de plaatsing (make_pcb.py).

  prep   : binnenlagen als vlakken (In1 = GND, In2 = 3V3), keepout onder de antenne op In2,
           en export naar Specctra-DSN voor de autorouter.
  import : SES (resultaat van de autorouter) inlezen, GND-vulling op boven- en onderkant,
           alle zones vullen en het bord opslaan.

Gebruik:
  /usr/bin/python3 generator/route.py prep   <bord.kicad_pcb> <uit.dsn>
  /usr/bin/python3 generator/route.py import <bord.kicad_pcb> <in.ses>
"""
import os
import sys

import pcbnew

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

mm = pcbnew.FromMM
OX, OY = 100.0, 100.0
W, H = 94.0, 70.0


def P(x, y):
    return pcbnew.VECTOR2I(mm(OX + x), mm(OY + y))


def rect_outline(z, x0, y0, x1, y1):
    o = z.Outline()
    o.NewOutline()
    for x, y in ((x0, y0), (x1, y0), (x1, y1), (x0, y1)):
        o.Append(mm(OX + x), mm(OY + y))


NETS = {}   # netnaam -> NETINFO_ITEM, opgehaald direct na het laden (KiCad 7: FindNet geeft na
            # het verwijderen van zones soms een kaal object terug)


def load(path):
    board = pcbnew.LoadBoard(path)
    NETS.clear()
    for name, ni in board.GetNetsByName().items():
        NETS[str(name)] = ni
    return board


def add_zone(board, layer, net, priority=0):
    z = pcbnew.ZONE(board)
    z.SetLayer(layer)
    z.SetNetCode(NETS[net].GetNetCode())
    rect_outline(z, 0, 0, W, H)                    # randafstand (0,3 mm) knipt de vulling bij
    z.SetLocalClearance(mm(0.2))
    z.SetMinThickness(mm(0.2))
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_THT_THERMAL)   # SMD massief, THT met thermal (handsolderen)
    z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
    z.SetThermalReliefGap(mm(0.3))
    z.SetThermalReliefSpokeWidth(mm(0.4))
    z.SetAssignedPriority(priority)
    z.SetZoneName(f'{net} {board.GetLayerName(layer)}')
    board.Add(z)
    return z


def antenna_keepout(board, layers):
    """Neemt de antenne-keepout van de ESP-footprint over voor lagen die daar ontbreken (In2)."""
    u5 = next(f for f in board.GetFootprints() if f.GetReference() == 'U5')
    src = next(z for z in u5.Zones() if z.GetIsRuleArea())
    k = pcbnew.ZONE(board)
    k.SetIsRuleArea(True)
    ls = pcbnew.LSET()
    for layer in layers:
        ls.AddLayer(layer)
    k.SetLayerSet(ls)
    k.SetDoNotAllowTracks(True)
    k.SetDoNotAllowVias(True)
    k.SetDoNotAllowCopperPour(True)
    k.SetDoNotAllowPads(False)
    k.SetDoNotAllowFootprints(False)
    k.Outline().Append(src.Outline())
    k.SetZoneName('antenne-keepout In2')
    board.Add(k)


def cutout_keepouts(board, margin=0.45):
    """Uitsparingen binnen het bord (NTC-sleuf): Freerouting houdt daar geen randafstand aan,
    dus een verbodszone (sporen/via's, alle koperlagen) die 0,45 mm groter is."""
    bx = None
    for d in board.GetDrawings():
        if d.GetLayer() != pcbnew.Edge_Cuts:
            continue
        b = d.GetBoundingBox()
        l, t, r, bt = (pcbnew.ToMM(v) - o for v, o in ((b.GetLeft(), OX), (b.GetTop(), OY), (b.GetRight(), OX), (b.GetBottom(), OY)))
        if l > 1 and r < W - 1 and t > 1 and bt < H - 1:
            bx = (l, t, r, bt) if bx is None else (min(bx[0], l), min(bx[1], t), max(bx[2], r), max(bx[3], bt))
    if bx is None:
        return
    k = pcbnew.ZONE(board)
    k.SetIsRuleArea(True)
    ls = pcbnew.LSET()
    for layer in (pcbnew.F_Cu, pcbnew.In1_Cu, pcbnew.In2_Cu, pcbnew.B_Cu):
        ls.AddLayer(layer)
    k.SetLayerSet(ls)
    k.SetDoNotAllowTracks(True)
    k.SetDoNotAllowVias(True)
    k.SetDoNotAllowCopperPour(False)
    k.SetDoNotAllowPads(False)
    k.SetDoNotAllowFootprints(False)
    rect_outline(k, bx[0] - margin, bx[1] - margin, bx[2] + margin, bx[3] + margin)
    k.SetZoneName('geen sporen bij NTC-sleuf')
    board.Add(k)


def module_keepout(board):
    """Geen sporen/via's op de bovenlaag onder het ESP-module-lichaam (tussen de padrijen);
    GND-vulling mag wel (warmte, afscherming). De antennezone heeft al een eigen keepout."""
    u5 = next(f for f in board.GetFootprints() if f.GetReference() == 'U5')
    edge = [p for p in u5.Pads() if p.GetNumber().isdigit() and 1 <= int(p.GetNumber()) <= 40]
    cx, cy = u5.GetPosition().x, u5.GetPosition().y
    left = max(p.GetBoundingBox().GetRight() for p in edge if p.GetPosition().x < cx - mm(8))
    right = min(p.GetBoundingBox().GetLeft() for p in edge if p.GetPosition().x > cx + mm(8))
    bottom = min(p.GetBoundingBox().GetTop() for p in edge if p.GetPosition().y > cy + mm(10))
    src = next(z for z in u5.Zones() if z.GetIsRuleArea())
    top = src.Outline().BBox().GetBottom()
    m = mm(0.3)
    k = pcbnew.ZONE(board)
    k.SetIsRuleArea(True)
    k.SetLayer(pcbnew.F_Cu)
    k.SetDoNotAllowTracks(True)
    k.SetDoNotAllowVias(True)
    k.SetDoNotAllowCopperPour(False)
    k.SetDoNotAllowPads(False)
    k.SetDoNotAllowFootprints(False)
    o = k.Outline()
    o.NewOutline()
    for x, y in ((left + m, top), (right - m, top), (right - m, bottom - m), (left + m, bottom - m)):
        o.Append(int(x), int(y))
    k.SetZoneName('geen sporen onder ESP-module')
    board.Add(k)


def prep(path, dsn):
    import rules
    rules.apply(os.path.splitext(path)[0] + '.kicad_pro')     # vóór het laden: netklassen
    board = load(path)
    if board.GetAreaCount() or len(board.GetTracks()):
        sys.exit('bord bevat al zones/sporen: eerst generator/make_pcb.py opnieuw draaien')
    board.SetLayerType(pcbnew.In1_Cu, pcbnew.LT_POWER)
    board.SetLayerType(pcbnew.In2_Cu, pcbnew.LT_POWER)
    add_zone(board, pcbnew.In1_Cu, 'GND')
    add_zone(board, pcbnew.In2_Cu, '+3V3')
    antenna_keepout(board, [pcbnew.In2_Cu])
    module_keepout(board)
    cutout_keepouts(board)
    from fanout import fanout, usb_preroute
    usb_preroute(board)
    done, failed = fanout(board)
    print(f'fanout: {done} pads met via naar het vlak' + (f'; GEEN plek: {", ".join(failed)}' if failed else ''))
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    pcbnew.SaveBoard(path, board)
    ok = pcbnew.ExportSpecctraDSN(board, dsn)
    txt = open(dsn).read().split('\n', 1)
    open(dsn, 'w').write(f'(pcb {os.path.splitext(os.path.basename(dsn))[0]}\n' + txt[1])
    print(f'vlakken In1=GND, In2=3V3, antenne-keepout In2; DSN {"geschreven" if ok else "MISLUKT"}: {dsn}')


def sexp(text):
    """Minimale s-expressieparser (Specctra): geeft geneste lijsten met strings."""
    import re
    toks = re.findall(r'"[^"]*"|\(|\)|[^\s()]+', text)
    stack, cur = [], []
    for t in toks:
        if t == '(':
            stack.append(cur)
            cur = []
        elif t == ')':
            done = cur
            cur = stack.pop()
            cur.append(done)
        else:
            cur.append(t.strip('"'))
    return cur[0]


def find(node, key):
    return [c for c in node if isinstance(c, list) and c and c[0] == key]


def import_ses(board, ses):
    """Leest sporen en via's uit een Freerouting-sessie (KiCad 7 kan dat alleen vanuit de editor)."""
    root = sexp(open(ses).read())
    routes = find(root, 'routes')[0]
    res = find(routes, 'resolution')[0]
    unit = {'um': 1e-3, 'mm': 1.0, 'mil': 0.0254, 'inch': 25.4}[res[1]] / float(res[2])   # -> mm
    to = lambda x, y: pcbnew.VECTOR2I(mm(float(x) * unit), mm(-float(y) * unit))
    stacks = {}
    for ps in find(find(routes, 'library_out')[0], 'padstack') if find(routes, 'library_out') else []:
        circ = [sh[1] for sh in find(ps, 'shape') if isinstance(sh[1], list) and sh[1][0] == 'circle']
        dia = float(circ[0][2]) * unit
        drill = float(ps[1].split(':')[1].split('_')[0]) / 1000.0     # "Via[0-3]_800:400_um"
        stacks[ps[1]] = (dia, drill)
    layers = {board.GetLayerName(l): l for l in board.GetEnabledLayers().CuStack()}
    key = lambda a, b2, l: (l,) + tuple(sorted([(a.x // 1000, a.y // 1000), (b2.x // 1000, b2.y // 1000)]))
    have_t = {key(t.GetStart(), t.GetEnd(), t.GetLayer()) for t in board.GetTracks() if t.GetClass() == 'PCB_TRACK'}
    have_v = {(v.GetPosition().x // 1000, v.GetPosition().y // 1000) for v in board.GetTracks() if v.GetClass() == 'PCB_VIA'}
    nt = nv = 0
    for net in find(find(routes, 'network_out')[0], 'net'):
        ni = NETS[net[1]]
        for w in find(net, 'wire'):
            for path in find(w, 'path'):
                layer, width, pts = layers[path[1]], float(path[2]) * unit, path[3:]
                xy = [(pts[i], pts[i + 1]) for i in range(0, len(pts) - 1, 2)]
                for (x1, y1), (x2, y2) in zip(xy, xy[1:]):
                    if key(to(x1, y1), to(x2, y2), layer) in have_t:
                        continue
                    t = pcbnew.PCB_TRACK(board)
                    t.SetStart(to(x1, y1))
                    t.SetEnd(to(x2, y2))
                    t.SetWidth(mm(width))
                    t.SetLayer(layer)
                    t.SetNet(ni)
                    board.Add(t)
                    nt += 1
        for v in find(net, 'via'):
            dia, drill = stacks.get(v[1], (0.6, 0.3))
            pos = to(v[2], v[3])
            if (pos.x // 1000, pos.y // 1000) in have_v:
                continue
            via = pcbnew.PCB_VIA(board)
            via.SetViaType(pcbnew.VIATYPE_THROUGH)
            via.SetPosition(to(v[2], v[3]))
            via.SetWidth(mm(dia))
            via.SetDrill(mm(drill))
            via.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
            via.SetNet(ni)
            board.Add(via)
            nv += 1
    return nt, nv


def do_import(path, ses):
    board = load(path)
    if any(not t.IsLocked() for t in board.GetTracks()) or \
            any(not z.GetIsRuleArea() and z.GetLayer() in (pcbnew.F_Cu, pcbnew.B_Cu) for z in board.Zones()):
        sys.exit('bord is al gerouteerd: eerst make_pcb.py + route.py prep opnieuw draaien')
    nt, nv = import_ses(board, ses)
    print(f'SES ingelezen: {nt} spoorsegmenten, {nv} via\'s')
    # opruimen: piepkleine stukjes spoor en via's die maar op één laag verbonden zijn
    removed = 0
    for t in list(board.GetTracks()):
        if t.GetClass() == 'PCB_TRACK' and not t.IsLocked() and (t.GetStart() - t.GetEnd()).EuclideanNorm() < mm(0.005):
            board.Remove(t)
            removed += 1
    def on_seg(p, a, b2):
        d = b2 - a
        L2 = d.x * d.x + d.y * d.y
        if L2 == 0:
            return (p - a).EuclideanNorm() < 1000
        t = max(0.0, min(1.0, ((p.x - a.x) * d.x + (p.y - a.y) * d.y) / L2))
        q = pcbnew.VECTOR2I(int(a.x + t * d.x), int(a.y + t * d.y))
        return (p - q).EuclideanNorm() < 1000                        # < 1 µm
    fixed = [t for t in board.GetTracks() if t.GetClass() == 'PCB_TRACK' and t.IsLocked()]
    for t in [t for t in board.GetTracks() if t.GetClass() == 'PCB_TRACK' and not t.IsLocked()]:
        if any(f.GetNetCode() == t.GetNetCode() and f.GetLayer() == t.GetLayer() and
               on_seg(t.GetStart(), f.GetStart(), f.GetEnd()) and on_seg(t.GetEnd(), f.GetStart(), f.GetEnd())
               for f in fixed):
            board.Remove(t)                                          # ligt volledig op een vast spoor
            removed += 1
    planes = {'GND', '+3V3'}
    for v in [t for t in board.GetTracks() if t.GetClass() == 'PCB_VIA' and not t.IsLocked()]:
        if v.GetNetname() in planes:
            continue
        pos, r = v.GetPosition(), v.GetWidth() // 2
        layers = {t.GetLayer() for t in board.GetTracks() if t.GetClass() == 'PCB_TRACK' and t.GetNetCode() == v.GetNetCode()
                  and min((t.GetStart() - pos).EuclideanNorm(), (t.GetEnd() - pos).EuclideanNorm()) < r}
        on_pad = any(p.GetNetCode() == v.GetNetCode() and p.HitTest(pos) for fp in board.GetFootprints() for p in fp.Pads())
        if len(layers) <= 1 and not on_pad:
            board.Remove(v)
            removed += 1
    if removed:
        print(f'opgeruimd: {removed} overbodige spoorstukjes/via\'s')
    # koper zonder net in footprints (brug van soldeerjumper JP1): geen vulling eromheen laten lopen
    for fp in board.GetFootprints():
        for it in fp.GraphicalItems():
            if it.GetLayer() in (pcbnew.F_Cu, pcbnew.B_Cu) and it.GetClass() != 'FP_TEXT':
                bb = it.GetBoundingBox()
                k = pcbnew.ZONE(board)
                k.SetIsRuleArea(True)
                k.SetLayer(it.GetLayer())
                k.SetDoNotAllowCopperPour(True)
                k.SetDoNotAllowTracks(False)
                k.SetDoNotAllowVias(False)
                k.SetDoNotAllowPads(False)
                k.SetDoNotAllowFootprints(False)
                o = k.Outline()
                o.NewOutline()
                m = mm(0.3)
                for x, y in ((bb.GetLeft() - m, bb.GetTop() - m), (bb.GetRight() + m, bb.GetTop() - m),
                             (bb.GetRight() + m, bb.GetBottom() + m), (bb.GetLeft() - m, bb.GetBottom() + m)):
                    o.Append(int(x), int(y))
                k.SetZoneName(f'geen vulling: {fp.GetReference()}')
                board.Add(k)
    for layer in (pcbnew.F_Cu, pcbnew.B_Cu):
        add_zone(board, layer, 'GND', priority=0)
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    board.BuildConnectivity()
    pcbnew.SaveBoard(path, board)
    print(f'{len(board.GetTracks())} sporen/via\'s, zones gevuld -> {path}')


if __name__ == '__main__':
    {'prep': prep, 'import': do_import}[sys.argv[1]](sys.argv[2], sys.argv[3])
