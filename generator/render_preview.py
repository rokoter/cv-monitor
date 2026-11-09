"""Realistische preview van een bordzijde (groen masker, witte silk, zilveren pads, koper).
    /usr/bin/python3 generator/render_preview.py <board.kicad_pcb> <uit.png> [F|B] [zoom]
"""
import os
import subprocess
import sys
import tempfile

board, out = sys.argv[1], sys.argv[2]
side = sys.argv[3] if len(sys.argv) > 3 else 'F'
zoom = sys.argv[4] if len(sys.argv) > 4 else '5'
tmp = tempfile.mkdtemp()


def layer_png(layers, name):
    svg = os.path.join(tmp, name + '.svg')
    png = os.path.join(tmp, name + '.png')
    cmd = ['kicad-cli', 'pcb', 'export', 'svg', '--layers', layers, '--black-and-white',
           '--page-size-mode', '2', '--exclude-drawing-sheet', '-o', svg, board]
    if side == 'B':
        cmd.insert(4, '--mirror')
    subprocess.run(cmd, check=True, capture_output=True)
    subprocess.run(['rsvg-convert', '-z', zoom, '-b', 'white', svg, '-o', png], check=True)
    return png


edge = layer_png('Edge.Cuts', 'edge')
cu = layer_png(f'{side}.Cu', 'cu')
mask = layer_png(f'{side}.Mask', 'mask')
silk = layer_png(f'{side}.SilkS', 'silk')

w, h = subprocess.run(['identify', '-format', '%w %h', edge], capture_output=True, text=True).stdout.split()
cx, cy = int(w) // 2, int(h) // 2 + 3
bg = os.path.join(tmp, 'bg.png')
# bordvlak groen kleuren (flood fill binnen de omtrek), buitenkant donker
subprocess.run(['convert', edge, '-fill', '#1f6b2e', '-fuzz', '10%', '-draw', f'color {cx},{cy} floodfill',
                '-fill', '#2b2b2b', '-opaque', 'white', bg], check=True)


def overlay(base, layer_png_path, color, outp):
    alpha = os.path.join(tmp, 'a.png')
    subprocess.run(['convert', layer_png_path, '-colorspace', 'gray', '-negate', alpha], check=True)
    subprocess.run(['convert', base, '(', '-size', f'{w}x{h}', f'xc:{color}', alpha,
                    '-alpha', 'off', '-compose', 'CopyOpacity', '-composite', ')',
                    '-compose', 'over', '-composite', outp], check=True)
    return outp


step = overlay(bg, cu, '#2f8f3f', os.path.join(tmp, 's1.png'))          # koper onder masker
step = overlay(step, mask, '#c9c9c9', os.path.join(tmp, 's2.png'))       # pads (HASL)
step = overlay(step, silk, '#ffffff', out)                               # silkscreen
print('preview:', out)
