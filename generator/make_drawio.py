"""Maakt accubeveiliging_DW01A_FS8205A.drawio (uitleg voor Koen)."""
import sys
from xml.sax.saxutils import escape

cells = []
_id = [10]


def nid():
    _id[0] += 1
    return f'c{_id[0]}'


def box(label, x, y, w, h, style):
    i = nid()
    cells.append(f'<mxCell id="{i}" value="{escape(label, {chr(34): "&quot;"})}" style="{style}" vertex="1" parent="1">'
                 f'<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/></mxCell>')
    return i


def edge(src, dst, label='', style='', pts=None):
    i = nid()
    p = ''
    if pts:
        p = '<Array as="points">' + ''.join(f'<mxPoint x="{a}" y="{b}"/>' for a, b in pts) + '</Array>'
    cells.append(f'<mxCell id="{i}" value="{escape(label, {chr(34): "&quot;"})}" style="{style}" edge="1" parent="1" '
                 f'source="{src}" target="{dst}"><mxGeometry relative="1" as="geometry">{p}</mxGeometry></mxCell>')
    return i


def arrow(x1, y1, x2, y2, label, style):
    i = nid()
    cells.append(f'<mxCell id="{i}" value="{escape(label)}" style="{style}" edge="1" parent="1">'
                 f'<mxGeometry relative="1" as="geometry"><mxPoint x="{x1}" y="{y1}" as="sourcePoint"/>'
                 f'<mxPoint x="{x2}" y="{y2}" as="targetPoint"/></mxGeometry></mxCell>')


H = 'html=1;whiteSpace=wrap;'
BOX = H + 'rounded=1;strokeWidth=2;fontSize=13;'
NODE = H + 'ellipse;fillColor=#333333;fontColor=#ffffff;fontSize=12;fontStyle=1;strokeColor=none;'
WIRE = 'endArrow=none;html=1;strokeWidth=3;strokeColor=#333333;edgeStyle=orthogonalEdgeStyle;fontSize=12;labelBackgroundColor=#ffffff;'
CTRL = 'endArrow=block;html=1;strokeWidth=2;dashed=1;strokeColor=#6c8ebf;edgeStyle=orthogonalEdgeStyle;fontSize=12;fontColor=#1f4e79;fontStyle=1;labelBackgroundColor=#ffffff;'
SENSE = 'endArrow=block;html=1;strokeWidth=2;dashed=1;strokeColor=#9673a6;edgeStyle=orthogonalEdgeStyle;fontSize=12;fontColor=#5b2c6f;labelBackgroundColor=#ffffff;'

# titel
box('<b style="font-size:20px">Accubeveiliging: DW01A + FS8205A</b><br>'
    'De DW01A is de <b>bewaker</b> die meet; de FS8205A bevat twee <b>schakelaars</b> (MOSFET\'s) in de min-leiding van de cel.',
    40, 20, 1080, 60, H + 'text;align=left;verticalAlign=top;fontSize=14;')

# hoofdcomponenten
cell = box('<b>18650 cel</b><br>(BT1)<br><br>+ boven<br>&minus; onder', 60, 150, 130, 230,
           BOX + 'fillColor=#fff2cc;strokeColor=#d6b656;')
sysb = box('<b>BAT+</b><br>naar lader (TP4056) en systeem (VSYS)<br><i>via Q3 ompoolbeveiliging</i>',
           840, 110, 270, 80, BOX + 'fillColor=#dae8fc;strokeColor=#6c8ebf;')
dw = box('<b>DW01A</b><br>de bewaker<br><span style="font-size:11px">meet celspanning (VCC&minus;VSS)<br>en stroom (via CS)</span>',
         400, 210, 210, 110, BOX + 'fillColor=#e1d5e7;strokeColor=#9673a6;')
rc = box('<b>R6 100&Omega; + C4 100nF</b><br><span style="font-size:11px">filter: schone voeding<br>voor de DW01A</span>',
         235, 180, 150, 60, BOX + 'fillColor=#f5f5f5;strokeColor=#666666;fontSize=12;')
bneg = box('B&minus;', 215, 445, 50, 50, NODE)
fet1 = box('<b>FET1 = ONTLAAD-schakelaar</b><br><span style="font-size:11px">FS8205A pin 2/3 (S1), 4 (G1)<br>'
           'body-diode laat alleen <b>laad</b>stroom door &rarr;</span>',
           310, 420, 220, 100, BOX + 'fillColor=#ffe6cc;strokeColor=#d79b00;')
dnode = box('D', 565, 450, 40, 40, NODE)
fet2 = box('<b>FET2 = LAAD-schakelaar</b><br><span style="font-size:11px">FS8205A pin 6/7 (S2), 5 (G2)<br>'
           '&larr; body-diode laat alleen <b>ontlaad</b>stroom door</span>',
           640, 420, 220, 100, BOX + 'fillColor=#d5e8d4;strokeColor=#82b366;')
gnd = box('<b>P&minus; = GND</b><br>systeemmassa<br>(lader en ESP32)', 900, 430, 210, 80,
          BOX + 'fillColor=#dae8fc;strokeColor=#6c8ebf;')
r7 = box('<b>R7 1k</b>', 760, 300, 80, 36, BOX + 'fillColor=#f5f5f5;strokeColor=#666666;fontSize=12;')

# stroomdraden
edge(cell, sysb, 'cel + = BAT+', WIRE + 'exitX=0.5;exitY=0;entryX=0;entryY=0.5;', pts=[(125, 150)])
edge(cell, bneg, 'cel &minus;', WIRE + 'exitX=0.5;exitY=1;entryX=0;entryY=0.5;', pts=[(125, 470)])
edge(bneg, fet1, '', WIRE + 'exitX=1;exitY=0.5;entryX=0;entryY=0.5;')
edge(fet1, dnode, '', WIRE + 'exitX=1;exitY=0.5;entryX=0;entryY=0.5;')
edge(dnode, fet2, '', WIRE + 'exitX=1;exitY=0.5;entryX=0;entryY=0.5;')
edge(fet2, gnd, '', WIRE + 'exitX=1;exitY=0.5;entryX=0;entryY=0.5;')

# voeding & meting DW01A
edge(cell, rc, 'BAT+', WIRE + 'strokeWidth=2;exitX=1;exitY=0.2;entryX=0;entryY=0.5;')
edge(rc, dw, 'VCC (pin 5)', SENSE + 'exitX=1;exitY=0.5;entryX=0;entryY=0.2;')
edge(bneg, dw, 'VSS (pin 6) = B&minus;', SENSE + 'exitX=0.5;exitY=0;entryX=0;entryY=0.75;', pts=[(240, 292)])
edge(gnd, r7, '', SENSE + 'exitX=0.5;exitY=0;entryX=1;entryY=0.5;', pts=[(1005, 318)])
edge(r7, dw, 'CS (pin 2): spanning over<br>beide FET\'s = stroom &times; ~50 m&Omega;', SENSE + 'exitX=0;exitY=0.5;entryX=1;entryY=0.75;')

# sturing
edge(dw, fet1, 'OD (pin 1)', CTRL + 'exitX=0.25;exitY=1;entryX=0.5;entryY=0;')
edge(dw, fet2, 'OC (pin 3)', CTRL + 'exitX=0.75;exitY=1;entryX=0.5;entryY=0;', pts=[(557, 380), (750, 380)])

# stroomrichtingen
arrow(270, 560, 880, 560, 'LAADstroom: van lader via GND &rarr; FET2 &rarr; FET1 &rarr; cel &minus;  (stroomt hier van rechts naar links)',
      'endArrow=none;startArrow=block;startFill=1;html=1;strokeWidth=4;strokeColor=#2e7d32;fontColor=#2e7d32;fontSize=12;fontStyle=1;labelBackgroundColor=#ffffff;')
arrow(270, 600, 880, 600, 'ONTLAADstroom: cel &minus; &larr; FET1 &larr; FET2 &larr; GND van het systeem  (stroomt hier van links naar rechts... terug naar de cel)',
      'endArrow=none;startArrow=none;html=1;strokeWidth=0;strokeColor=none;fontSize=1;')

# corrigeer: duidelijke richtingspijlen (conventionele stroom)
cells.pop()
cells.pop()
arrow(880, 560, 270, 560, 'LAADSTROOM  GND &rarr; FET2 &rarr; FET1 &rarr; cel&minus;',
      'endArrow=block;endFill=1;html=1;strokeWidth=4;strokeColor=#2e7d32;fontColor=#2e7d32;fontSize=13;fontStyle=1;labelBackgroundColor=#ffffff;')
arrow(270, 600, 880, 600, 'ONTLAADSTROOM  cel&minus; &rarr; FET1 &rarr; FET2 &rarr; GND',
      'endArrow=block;endFill=1;html=1;strokeWidth=4;strokeColor=#d79b00;fontColor=#b36b00;fontSize=13;fontStyle=1;labelBackgroundColor=#ffffff;')

box('<b>Waarom twee FET\'s rug-aan-rug?</b><br>Een MOSFET heeft een ingebouwde <i>body-diode</i> en kan daardoor maar '
    'in één richting blokkeren. Door twee FET\'s met de drains tegen elkaar (D) te zetten kan de DW01A <b>laden</b> en '
    '<b>ontladen</b> los van elkaar blokkeren. Is één FET uit, dan kan de stroom in de andere richting nog via de '
    'body-diode: zo kun je een lege cel altijd weer laden.',
    40, 640, 520, 130, H + 'rounded=1;fillColor=#fffbe6;strokeColor=#d6b656;align=left;verticalAlign=top;spacing=10;fontSize=12;')
box('<b>In dit ontwerp</b><br>De TP4056 stopt al netjes op 4,2 V en het systeem trekt &lt; 0,5 A. '
    'De DW01A is dus het <b>vangnet</b>: hij grijpt alleen in als er iets misgaat (lader defect, kortsluiting, '
    'accu leeg getrokken tijdens een lange stroomstoring).',
    590, 640, 520, 130, H + 'rounded=1;fillColor=#eef5ff;strokeColor=#6c8ebf;align=left;verticalAlign=top;spacing=10;fontSize=12;')

TD = 'style="border:1px solid #999;padding:4px"'
TH = 'style="border:1px solid #999;padding:4px;background:#e1d5e7"'
rows = [
    ('Normaal', '2,4 &ndash; 4,3 V, stroom &lt; ~3 A', 'hoog &rarr; AAN', 'hoog &rarr; AAN', 'laden en ontladen', '&ndash;'),
    ('Overladen', 'cel &gt; ~4,3 V', 'AAN', '<b>laag &rarr; UIT</b>', 'laden stopt; ontladen kan nog (body-diode FET2)', 'cel zakt onder ~4,1 V'),
    ('Te diep ontladen', 'cel &lt; ~2,4 V', '<b>laag &rarr; UIT</b>', 'AAN', 'ontladen stopt (systeem valt uit); laden kan nog (body-diode FET1)', 'lader aansluiten, cel &gt; ~3,0 V'),
    ('Overstroom', 'CS &gt; 0,15 V (&asymp; 3 A)', '<b>laag &rarr; UIT</b>', 'AAN', 'ontladen stopt', 'belasting weg'),
    ('Kortsluiting', 'CS &gt; ~1,35 V', '<b>direct UIT</b>', 'AAN', 'binnen microseconden af', 'belasting weg'),
]
html = (f'<table style="border-collapse:collapse;font-size:12px;width:100%"><tr>'
        + ''.join(f'<th {TH}>{h}</th>' for h in ['Situatie', 'DW01A ziet', 'OD &rarr; FET1 (ontladen)',
                                                   'OC &rarr; FET2 (laden)', 'Gevolg', 'Herstelt als'])
        + '</tr>' + ''.join('<tr>' + ''.join(f'<td {TD}>{c}</td>' for c in r) + '</tr>' for r in rows) + '</table>')
box(html, 40, 790, 1070, 190, H + 'text;align=left;verticalAlign=top;overflow=fill;')

xml = ('<mxfile host="app.diagrams.net"><diagram id="dw01a" name="DW01A + FS8205A">'
       '<mxGraphModel dx="1200" dy="1000" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" '
       'fold="1" page="1" pageScale="1" pageWidth="1169" pageHeight="1010" math="0" shadow="0"><root>'
       '<mxCell id="0"/><mxCell id="1" parent="0"/>' + ''.join(cells) + '</root></mxGraphModel></diagram></mxfile>')
open(sys.argv[1], 'w', encoding='utf-8').write(xml)
print('ok', len(cells), 'elementen')
