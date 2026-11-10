"""3D-modellen voor de CV-monitor in hardware/cv_monitor/3dmodels zetten.

1. Bibliotheekmodellen (STEP) kopiëren uit een uitgepakte KiCad-3D-bibliotheek:
   - KiCad 7.0.11 (Ubuntu-pakket kicad-packages3d), plus
   - JST_SH_SM04B-SRSS-TB...Horizontal uit KiCad 10.0.7 (zit niet in 7.0.11).
2. Drie modellen die KiCad niet heeft zelf genereren (vereenvoudigd, maar met de juiste buitenmaten):
   - USB-C HRO TYPE-C-31-M-12: 8,94 x 7,3 x 3,2 mm, ovale (stadion) voorkant
   - drukknop XKB TS-1187A-B-A-B (C318884): 5,1 x 5,1 mm, 1,5 mm hoog, ronde knop
   - 18650-cel (Ø 18,5 x 65 mm) als tweede model in de accuhouder, handig voor de behuizing

Gebruik:  python3 make_3dmodels.py <map met bibliotheek-STEP-bestanden> <uitvoermap>
Nodig: cadquery-ocp (OpenCascade voor Python).
"""
import os
import shutil
import sys

from OCP.BRepAlgoAPI import BRepAlgoAPI_Fuse
from OCP.BRepFilletAPI import BRepFilletAPI_MakeFillet
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCylinder
from OCP.gp import gp_Ax2, gp_Dir, gp_Pnt
from OCP.IFSelect import IFSelect_RetDone
from OCP.Quantity import Quantity_Color, Quantity_TOC_RGB
from OCP.STEPCAFControl import STEPCAFControl_Writer
from OCP.STEPControl import STEPControl_AsIs
from OCP.TCollection import TCollection_ExtendedString
from OCP.TDocStd import TDocStd_Document
from OCP.TopAbs import TopAbs_EDGE
from OCP.TopExp import TopExp_Explorer
from OCP.TopoDS import TopoDS
from OCP.XCAFDoc import XCAFDoc_ColorSurf, XCAFDoc_DocumentTool

# Bibliotheekmodellen die het bord gebruikt (bestandsnaam zonder .step)
LIBRARY = [
    'BatteryHolder_MPD_BH-18650-PC2', 'C_0603_1608Metric', 'C_0805_2012Metric',
    'JST_PH_B2B-PH-K_1x02_P2.00mm_Vertical', 'JST_SH_SM04B-SRSS-TB_1x04-1MP_P1.00mm_Horizontal',
    'PinHeader_1x04_P2.54mm_Vertical', 'PinHeader_1x08_P2.54mm_Vertical', 'PinHeader_1x10_P2.54mm_Vertical',
    'D_SMA', 'D_SOD-123', 'Fuse_1206_3216Metric', 'LED_0603_1608Metric', 'LED_D3.0mm',
    'TSSOP-8_4.4x3mm_P0.65mm', 'SOIC-8-1EP_3.9x4.9mm_P1.27mm_EP2.35x2.35mm',
    'SOT-23', 'SOT-23-5', 'SOT-23-6', 'R_0603_1608Metric',
    'TerminalBlock_Phoenix_PT-1,5-3-3.5-H_1x03_P3.50mm_Horizontal', 'ESP32-S3-WROOM-1',
]

# Celpositie in de houder (footprint-coördinaten, mm): tussen de contacten (pad 1 op x=0, pad 2 op
# x=72) en rustend op de ronde bodem (as 9,6 mm boven de print, bepaald uit het houdermodel).
CELL = dict(x0=36.0 - 32.5, length=65.0, radius=9.25, z_axis=9.6)


def rgb(r, g, b):
    return Quantity_Color(r, g, b, Quantity_TOC_RGB)


def box(x0, y0, z0, dx, dy, dz):
    return BRepPrimAPI_MakeBox(gp_Pnt(x0, y0, z0), dx, dy, dz).Shape()


def cyl(px, py, pz, dx, dy, dz, r, h):
    return BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(px, py, pz), gp_Dir(dx, dy, dz)), r, h).Shape()


def write_step(path, parts):
    """parts: [(shape, kleur)] -> STEP met kleuren (KiCad en FreeCAD tonen die)."""
    doc = TDocStd_Document(TCollection_ExtendedString('XmlOcaf'))
    st = XCAFDoc_DocumentTool.ShapeTool_s(doc.Main())
    ct = XCAFDoc_DocumentTool.ColorTool_s(doc.Main())
    for shape, color in parts:
        lab = st.AddShape(shape, False)
        ct.SetColor(lab, color, XCAFDoc_ColorSurf)
    w = STEPCAFControl_Writer()
    w.SetColorMode(True)
    w.Transfer(doc, STEPControl_AsIs)
    assert w.Write(path) == IFSelect_RetDone, path


def usb_c():
    """HRO TYPE-C-31-M-12: footprint-fab 8,94 x 7,3 mm rond de oorsprong; 3,2 mm hoog; stadionvorm."""
    w, d, h, r = 8.94, 7.3, 3.2, 1.45
    body = box(-w / 2, -d / 2, 0, w, d, h)
    mk = BRepFilletAPI_MakeFillet(body)
    ex = TopExp_Explorer(body, TopAbs_EDGE)
    while ex.More():
        e = TopoDS.Edge_s(ex.Current())
        from OCP.BRep import BRep_Tool
        c = BRep_Tool.Curve_s(e, 0, 1)
        p1, p2 = c.Value(0), c.Value(1)
        if abs(p1.X() - p2.X()) < 1e-6 and abs(p1.Z() - p2.Z()) < 1e-6:   # randen evenwijdig aan y
            mk.Add(r, e)
        ex.Next()
    return [(mk.Shape(), rgb(0.78, 0.78, 0.80))]


def tactile():
    """XKB TS-1187A-B-A-B: huis 5,1 x 5,1 x 1,0 mm, ronde knop tot 1,5 mm."""
    base = box(-2.55, -2.55, 0, 5.1, 5.1, 1.0)
    knob = cyl(0, 0, 1.0, 0, 0, 1, 1.3, 0.5)
    return [(base, rgb(0.15, 0.15, 0.15)), (knob, rgb(0.85, 0.70, 0.30))]


def cell():
    c = CELL
    body = cyl(c['x0'], 0, c['z_axis'], 1, 0, 0, c['radius'], c['length'] - 1.0)
    nub = cyl(c['x0'] + c['length'] - 1.0, 0, c['z_axis'], 1, 0, 0, 3.5, 1.0)   # pluspool
    return [(BRepAlgoAPI_Fuse(body, nub).Shape(), rgb(0.10, 0.35, 0.75))]


def main(src, out):
    os.makedirs(out, exist_ok=True)
    missing = []
    for name in LIBRARY:
        for cand in (name + '.step', name + '.step.v10'):
            p = os.path.join(src, cand)
            if os.path.exists(p):
                shutil.copyfile(p, os.path.join(out, name + '.step'))
                break
        else:
            missing.append(name)
    write_step(os.path.join(out, 'USB_C_Receptacle_HRO_TYPE-C-31-M-12.step'), usb_c())
    write_step(os.path.join(out, 'SW_Push_1P1T_XKB_TS-1187A.step'), tactile())
    write_step(os.path.join(out, 'Cell_18650.step'), cell())
    print(f'{len(LIBRARY) - len(missing)} bibliotheekmodellen gekopieerd, 3 gegenereerd -> {out}')
    if missing:
        print('ONTBREEKT:', ', '.join(missing))
        sys.exit(1)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
