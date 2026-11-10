"""Routing-stap na de plaatsing (make_pcb.py).

  prep   : binnenlagen als vlakken (In1 = GND, In2 = 3V3), keepout onder de antenne op In2,
           en export naar Specctra-DSN voor de autorouter.
  import : SES (resultaat van de autorouter) inlezen, GND-vulling op boven- en onderkant,
           alle zones vullen en het bord opslaan.

Gebruik:
  /usr/bin/python3 generator/route.py prep   <bord.kicad_pcb> <uit.dsn>
  /usr/bin/python3 generator/route.py import <bord.kicad_pcb> <in.ses>
"""
import sys

import pcbnew

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


def add_zone(board, layer, net, priority=0):
    z = pcbnew.ZONE(board)
    z.SetLayer(layer)
    z.SetNetCode(board.FindNet(net).GetNetCode())
    rect_outline(z, 0, 0, W, H)                    # randafstand (0,3 mm) knipt de vulling bij
    z.SetLocalClearance(mm(0.2))
    z.SetMinThickness(mm(0.2))
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
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


def prep(path, dsn):
    board = pcbnew.LoadBoard(path)
    for z in list(board.Zones()):                  # opnieuw beginnen
        board.Remove(z)
    board.SetLayerType(pcbnew.In1_Cu, pcbnew.LT_POWER)
    board.SetLayerType(pcbnew.In2_Cu, pcbnew.LT_POWER)
    add_zone(board, pcbnew.In1_Cu, 'GND')
    add_zone(board, pcbnew.In2_Cu, '+3V3')
    antenna_keepout(board, [pcbnew.In2_Cu])
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    pcbnew.SaveBoard(path, board)
    ok = pcbnew.ExportSpecctraDSN(board, dsn)
    print(f'vlakken In1=GND, In2=3V3, antenne-keepout In2; DSN {"geschreven" if ok else "MISLUKT"}: {dsn}')


def do_import(path, ses):
    board = pcbnew.LoadBoard(path)
    ok = pcbnew.ImportSpecctraSES(board, ses)
    print('SES ingelezen' if ok else 'SES-import MISLUKT')
    for layer in (pcbnew.F_Cu, pcbnew.B_Cu):
        add_zone(board, layer, 'GND', priority=0)
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    board.BuildConnectivity()
    pcbnew.SaveBoard(path, board)
    print(f'{len(board.GetTracks())} sporen/via\'s, zones gevuld -> {path}')


if __name__ == '__main__':
    {'prep': prep, 'import': do_import}[sys.argv[1]](sys.argv[2], sys.argv[3])
