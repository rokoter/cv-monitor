"""Eenvoudige 3D-preview (PNG) van een STEP-bestand met kleuren, zonder grafische kaart.

Leest het STEP met kleuren (OpenCascade/XCAF), maakt er driehoeken van en tekent die met het
schildersalgoritme (achter naar voor) met eenvoudige belichting.
Gebruik: python3 render_3d.py <bord.step> <uit.png> [boven|onder|voor] [breedte_px]
"""
import math
import sys

import numpy as np
from OCP.BRep import BRep_Tool
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.IFSelect import IFSelect_RetDone
from OCP.STEPCAFControl import STEPCAFControl_Reader
from OCP.TCollection import TCollection_ExtendedString
from OCP.TDocStd import TDocStd_Document
from OCP.TopAbs import TopAbs_FACE, TopAbs_REVERSED
from OCP.TopExp import TopExp_Explorer
from OCP.TopLoc import TopLoc_Location
from OCP.TopoDS import TopoDS
from OCP.XCAFDoc import XCAFDoc_ColorCurv, XCAFDoc_ColorGen, XCAFDoc_ColorSurf, XCAFDoc_DocumentTool
from OCP.Quantity import Quantity_Color
from OCP.TDF import TDF_LabelSequence
from PIL import Image

DEFAULT = (0.6, 0.6, 0.6)


def load(path):
    doc = TDocStd_Document(TCollection_ExtendedString('XmlOcaf'))
    r = STEPCAFControl_Reader()
    r.SetColorMode(True)
    assert r.ReadFile(path) == IFSelect_RetDone
    r.Transfer(doc)
    return doc


def color_of(ct, lab_or_shape):
    c = Quantity_Color()
    from OCP.TDF import TDF_Label
    from OCP.XCAFDoc import XCAFDoc_ColorTool
    for kind in (XCAFDoc_ColorSurf, XCAFDoc_ColorGen, XCAFDoc_ColorCurv):
        ok = (XCAFDoc_ColorTool.GetColor_s(lab_or_shape, kind, c) if isinstance(lab_or_shape, TDF_Label)
              else ct.GetColor(lab_or_shape, kind, c))
        if ok:
            return (c.Red(), c.Green(), c.Blue())
    return None


def collect(doc):
    """Geeft [(face, kleur, locatie)] voor alle vlakken in de assemblage."""
    st = XCAFDoc_DocumentTool.ShapeTool_s(doc.Main())
    ct = XCAFDoc_DocumentTool.ColorTool_s(doc.Main())
    out = []

    def walk(lab, loc, inherited):
        col = color_of(ct, lab) or inherited
        if st.IsReference_s(lab):
            ref = TDF_LabelSequence()
            from OCP.TDF import TDF_Label
            rl = TDF_Label()
            st.GetReferredShape_s(lab, rl)
            walk(rl, loc.Multiplied(st.GetLocation_s(lab)), col)
            return
        if st.IsAssembly_s(lab):
            comps = TDF_LabelSequence()
            st.GetComponents_s(lab, comps)
            for i in range(1, comps.Length() + 1):
                walk(comps.Value(i), loc, col)
            return
        shape = st.GetShape_s(lab)
        # kleuren op vlakniveau (subshapes)
        sub = []
        subs = TDF_LabelSequence()
        st.GetSubShapes_s(lab, subs)
        for i in range(1, subs.Length() + 1):
            sl = subs.Value(i)
            sc = color_of(ct, sl)
            if sc:
                ss = st.GetShape_s(sl)
                ex2 = TopExp_Explorer(ss, TopAbs_FACE)
                while ex2.More():
                    sub.append((ex2.Current(), sc))
                    ex2.Next()
        ex = TopExp_Explorer(shape, TopAbs_FACE)
        while ex.More():
            f = TopoDS.Face_s(ex.Current())
            fc = next((sc for sf, sc in sub if sf.IsSame(f)), None) or col or DEFAULT
            out.append((f, fc, loc))
            ex.Next()

    roots = TDF_LabelSequence()
    st.GetFreeShapes(roots)
    for i in range(1, roots.Length() + 1):
        walk(roots.Value(i), TopLoc_Location(), None)
    return out


def triangles(faces, defl=0.05):
    tris, cols = [], []
    for f, c, loc in faces:
        BRepMesh_IncrementalMesh(f, defl, False, 0.35, False)
        fl = TopLoc_Location()
        tri = BRep_Tool.Triangulation_s(f, fl)
        if tri is None:
            continue
        trsf = loc.Multiplied(fl).Transformation()
        pts = []
        for i in range(1, tri.NbNodes() + 1):
            p = tri.Node(i).Transformed(trsf)
            pts.append((p.X(), p.Y(), p.Z()))
        pts = np.array(pts)
        rev = f.Orientation() == TopAbs_REVERSED
        for i in range(1, tri.NbTriangles() + 1):
            a, b, cc = tri.Triangle(i).Get()
            if rev:
                b, cc = cc, b
            tris.append(pts[[a - 1, b - 1, cc - 1]])
            cols.append(c)
    return np.array(tris), np.array(cols)


def view_matrix(view):
    # KiCad-STEP: x naar rechts, y naar 'boven' op het bord (KiCad-y omgekeerd), z uit de bovenkant
    if view == 'boven':
        az, el = -35, 50
    elif view == 'onder':
        az, el = 215, -50
    else:
        az, el = -20, 20
    az, el = math.radians(az), math.radians(el)
    rz = np.array([[math.cos(az), -math.sin(az), 0], [math.sin(az), math.cos(az), 0], [0, 0, 1]])
    rx = np.array([[1, 0, 0], [0, math.cos(-(math.pi / 2 - el)), -math.sin(-(math.pi / 2 - el))],
                   [0, math.sin(-(math.pi / 2 - el)), math.cos(-(math.pi / 2 - el))]])
    return rx @ rz


def _subdivide(t2, t3, cols, shade, maxpx):
    """Splits driehoeken die op het scherm groter zijn dan maxpx in 4 (via middens van de zijden)."""
    while True:
        span = t2.max(1) - t2.min(1)
        big = (span > maxpx).any(1)
        if not big.any():
            return t2, t3, cols, shade
        b2, b3 = t2[big], t3[big]
        m2 = [(b2[:, a] + b2[:, b]) / 2 for a, b in ((0, 1), (1, 2), (2, 0))]
        m3 = [(b3[:, a] + b3[:, b]) / 2 for a, b in ((0, 1), (1, 2), (2, 0))]
        parts2 = [np.stack([b2[:, 0], m2[0], m2[2]], 1), np.stack([m2[0], b2[:, 1], m2[1]], 1),
                  np.stack([m2[2], m2[1], b2[:, 2]], 1), np.stack([m2[0], m2[1], m2[2]], 1)]
        parts3 = [np.stack([b3[:, 0], m3[0], m3[2]], 1), np.stack([m3[0], b3[:, 1], m3[1]], 1),
                  np.stack([m3[2], m3[1], b3[:, 2]], 1), np.stack([m3[0], m3[1], m3[2]], 1)]
        t2 = np.concatenate([t2[~big]] + parts2)
        t3 = np.concatenate([t3[~big]] + parts3)
        cols = np.concatenate([cols[~big]] + [cols[big]] * 4)
        shade = np.concatenate([shade[~big]] + [shade[big]] * 4)


def render(step, out, view='boven', width=1800):
    doc = load(step)
    tris, cols = triangles(collect(doc))
    m = view_matrix(view)
    v = tris @ m.T                                   # beeldcoördinaten, z = naar de kijker toe
    n = np.cross(v[:, 1] - v[:, 0], v[:, 2] - v[:, 0])
    n /= (np.linalg.norm(n, axis=1) + 1e-12)[:, None]
    light = np.array([-0.35, 0.45, 0.82])
    light /= np.linalg.norm(light)
    shade = 0.38 + 0.62 * np.clip(np.abs(n @ light), 0, 1)
    ss = 2
    W = width * ss
    xy = v[:, :, :2]
    mn, mx = xy.reshape(-1, 2).min(0), xy.reshape(-1, 2).max(0)
    scale = (W * 0.92) / (mx[0] - mn[0])
    H = int((mx[1] - mn[1]) * scale + W * 0.08)
    pad = W * 0.04
    t2 = np.empty_like(xy)
    t2[..., 0] = pad + (xy[..., 0] - mn[0]) * scale
    t2[..., 1] = H - (pad + (xy[..., 1] - mn[1]) * scale)
    t3 = np.concatenate([t2, v[:, :, 2:3]], axis=2)
    t2, t3, cols, shade = _subdivide(t2, t3, cols, shade, 14)
    zbuf = np.full(W * H, -np.inf)
    cbuf = np.full((W * H, 3), 245.0)
    G = 16
    gy, gx = np.mgrid[0:G, 0:G]
    gx, gy = gx.ravel(), gy.ravel()
    rgb = np.clip(cols * shade[:, None], 0, 1) * 255
    for k in range(0, len(t3), 4000):
        T = t3[k:k + 4000]
        x0 = np.floor(T[:, :, 0].min(1)).astype(int)
        y0 = np.floor(T[:, :, 1].min(1)).astype(int)
        px = x0[:, None] + gx[None, :] + 0.5
        py = y0[:, None] + gy[None, :] + 0.5
        (ax, ay), (bx, by), (cx, cy) = [(T[:, i, 0][:, None], T[:, i, 1][:, None]) for i in range(3)]
        area = (bx - ax) * (cy - ay) - (by - ay) * (cx - ax)
        area = np.where(np.abs(area) < 1e-9, 1e-9, area)
        w0 = ((bx - px) * (cy - py) - (by - py) * (cx - px)) / area
        w1 = ((cx - px) * (ay - py) - (cy - py) * (ax - px)) / area
        w2 = 1 - w0 - w1
        inside = (w0 >= -1e-6) & (w1 >= -1e-6) & (w2 >= -1e-6)
        z = w0 * T[:, 0, 2][:, None] + w1 * T[:, 1, 2][:, None] + w2 * T[:, 2, 2][:, None]
        pxi, pyi = px.astype(int), py.astype(int)
        inside &= (pxi >= 0) & (pxi < W) & (pyi >= 0) & (pyi < H)
        ti, gi = np.nonzero(inside)
        idx = pyi[ti, gi] * W + pxi[ti, gi]
        zz = z[ti, gi]
        order = np.lexsort((zz, idx))                 # per pixel de dichtstbijzijnde als laatste
        idx, zz, ti = idx[order], zz[order], ti[order]
        last = np.r_[idx[1:] != idx[:-1], True]
        idx, zz, ti = idx[last], zz[last], ti[last]
        better = zz > zbuf[idx]
        zbuf[idx[better]] = zz[better]
        cbuf[idx[better]] = rgb[k + ti[better]]
    img = Image.fromarray(cbuf.reshape(H, W, 3).astype(np.uint8))
    img = img.resize((width, H // ss), Image.LANCZOS)
    img.save(out)
    print(f'{len(tris)} driehoeken -> {out}')


if __name__ == '__main__':
    render(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else 'boven',
           int(sys.argv[4]) if len(sys.argv) > 4 else 1800)
