"""Plaatsing van de onderdelen op de PCB (mm, t.o.v. linksboven van het bord; y naar beneden).

(x, y, rotatie in graden, zijde). Zijde 'B' = onderkant (alleen de 18650-houder).
Rotatie volgt KiCad: positief = tegen de klok in.
"""

BOARD_W, BOARD_H = 94.0, 70.0
COPPER_LAYERS = 4          # F.Cu signaal | In1 GND-vlak | In2 voeding | B.Cu signaal
CORNER_R = 3.0

# Bevestigingsgaten M3 (ook gebruikt voor de behuizing in FreeCAD)
HOLES = {'H1': (3.5, 3.5), 'H2': (3.5, 66.5), 'H3': (90.5, 66.5), 'H4': (47.0, 3.5)}

PLACE = {
    # ---- 1. USB-C ingang (linkerrand)
    'J1': (None, 30.0, 270, 'F'),          # x wordt berekend: opening gelijk met de bordrand
    'F1': (13.0, 22.0, 0, 'F'),
    'C1': (13.0, 25.5, 0, 'F'),
    'U1': (11.5, 36.0, 0, 'F'),
    'R1': (11.0, 40.5, 0, 'F'),
    'R2': (11.0, 42.5, 0, 'F'),
    # ---- 2. Lader
    'D2': (9.0, 9.0, 180, 'F'), 'R4': (13.0, 9.0, 0, 'F'),
    'D3': (9.0, 11.5, 180, 'F'), 'R5': (13.0, 11.5, 0, 'F'),
    'C2': (18.0, 14.5, 0, 'F'),
    'U2': (25.0, 15.0, 0, 'F'),
    'R3': (25.0, 20.0, 0, 'F'),
    # TEMP-netwerk als 2x2-raster, referentie boven elk onderdeel
    'R23': (32.0, 12.0, 0, 'F'), 'R24': (36.0, 12.0, 0, 'F'),
    'R25': (32.0, 16.5, 0, 'F'), 'JP1': (36.0, 16.5, 0, 'F'),
    # ---- 3. Power-path + LDO
    'D1': (23.0, 26.0, 0, 'F'),
    'Q1': (31.0, 26.5, 0, 'F'),
    'R8': (35.0, 23.0, 0, 'F'),
    'C5': (35.5, 30.0, 0, 'F'),
    'U4': (40.5, 27.0, 0, 'F'),
    'C6': (46.0, 27.0, 0, 'F'),
    # ---- Testpunten
    'TP1': (16.0, 40.0, 0, 'F'), 'TP2': (21.0, 40.0, 0, 'F'), 'TP3': (26.0, 40.0, 0, 'F'),
    'TP4': (31.0, 40.0, 0, 'F'), 'TP5': (36.0, 40.0, 0, 'F'),
    # ---- 4. Accu + beveiliging (boven de houder, die aan de onderkant zit)
    'BT1': (83.05, 58.7, 0, 'B'),
    'Q3': (15.0, 47.0, 0, 'F'), 'R22': (15.5, 51.0, 0, 'F'),
    'C3': (20.0, 47.0, 0, 'F'),
    'R6': (24.5, 46.0, 0, 'F'), 'C4': (24.5, 48.5, 0, 'F'),
    'U3': (30.5, 47.5, 0, 'F'), 'R7': (30.5, 51.5, 0, 'F'),
    'Q2': (38.5, 47.5, 0, 'F'),
    'D5': (4.5, 50.0, 0, 'B'),            # 3 mm THT-LED aan de accukant (onderkant), naast de houder
    'R26': (9.5, 47.0, 0, 'F'), 'D6': (10.0, 51.0, 0, 'F'),
    'J9': (40.5, 14.5, 0, 'F'),            # NTC: buiten de accuhouder (THT!), bij het TEMP-netwerk
    # ---- 5. ESP32-S3 (rechtsboven, antenne aan de bovenrand)
    'U5': (79.0, 13.4, 0, 'F'),            # antenne 0,65 mm van de bovenrand (silk binnen het bord)
    # ESP-randcomponenten in twee kolommen, referentie boven elk onderdeel
    'C8': (66.0, 9.5, 0, 'F'), 'C9': (66.0, 13.5, 0, 'F'), 'C10': (66.0, 17.5, 0, 'F'),
    'R9': (61.0, 9.5, 0, 'F'), 'R13': (61.0, 17.5, 0, 'F'), 'D4': (61.0, 21.5, 180, 'F'),
    'R10': (91.0, 28.5, 0, 'F'),
    # ---- 6. Metingen + sensoren (rechterrand)
    # metingen als raster rechts van de e-ink-header, referentie boven elk onderdeel
    'R14': (70.5, 31.0, 0, 'F'), 'R16': (74.5, 31.0, 0, 'F'),
    'R15': (70.5, 34.5, 0, 'F'), 'R17': (74.5, 34.5, 0, 'F'), 'C11': (70.5, 38.0, 0, 'F'),
    # sensorweerstanden in één kolom; links van de klemmen ruimte voor de pinnamen
    'R18': (78.5, 40.0, 0, 'F'), 'R27': (78.5, 43.5, 0, 'F'), 'C12': (78.5, 47.0, 0, 'F'),
    'R19': (78.5, 50.5, 0, 'F'), 'R28': (78.5, 54.0, 0, 'F'),
    'J2': (None, 43.0, 90, 'F'),           # x berekend: draadingang aan de rechterrand (pin 1 onder)
    'J3': (None, 54.5, 90, 'F'),           # pinnaam 3V3 vrij van accupad (+)
    # ---- 7. Bediening + uitbreiding (onderrand)
    # knoppen rechts van de accugaten (x 11 en 18,7): boven elke knop ruimte voor referentie + functie
    'SW1': (24.0, 66.0, 0, 'F'), 'SW2': (32.5, 66.0, 0, 'F'), 'SW3': (41.0, 66.0, 0, 'F'),
    'R11': (61.0, 13.5, 0, 'F'),           # pull-up STATUS-knop (GPIO15), bij de ESP
    'J4': (55.0, 22.0, 0, 'F'),           # verticaal, pinnamen links (boven het accuhoudergebied)
    # ---- 8. Qwiic (onderrand, opening naar beneden)
    'R20': (52.0, 60.5, 0, 'F'), 'R21': (52.0, 63.0, 0, 'F'),
    'J5': (64.0, None, 0, 'F'), 'J6': (74.0, None, 0, 'F'),   # y berekend: opening aan de onderrand
    # ---- 9. Displays (bovenrand)
    'J8': (66.5, 28.5, 0, 'F'),           # e-ink verticaal onder de ESP, pinnamen links
    'J7': (50.5, 8.5, 0, 'F'),             # OLED (THT): buiten de accuhouder, naast J4
}

# Onderdelen die met de 'opening' tegen een bordrand moeten: (rand, overstek in mm)
EDGE_ALIGN = {'J1': ('left', 0.0), 'J2': ('right', -0.6), 'J3': ('right', -0.6),
              'J5': ('bottom', 0.0), 'J6': ('bottom', 0.0)}

# Functielabels op de bovenkant (silkscreen), naast het onderdeel
FUNC_LABELS = {
    'SW1': 'RESET', 'SW2': 'BOOT', 'SW3': 'STATUS',
    'D2': 'LADEN', 'D3': 'VOL', 'D4': 'LED',
    'J1': 'USB 5V', 'J2': 'AANVOER', 'J3': 'RETOUR', 'J4': 'UITBREIDING',
    'J5': 'QWIIC', 'J6': 'QWIIC', 'J7': 'OLED', 'J8': 'E-INK', 'J9': 'NTC',
}

# Functielabels op de onderkant (onderdelen die aan de onderkant zitten)
FUNC_LABELS_BACK = {'D5': 'ACCU OMGEKEERD'}

# Labels die altijd recht boven het onderdeel moeten staan (op één lijn)
# Bij 'up'/'down' komt de referentie daar nog boven/onder (eerst functie, dan referentie).
FUNC_LABEL_DIR = {'D4': 'right', 'SW1': 'up', 'SW2': 'up', 'SW3': 'up',
                  'J2': 'up', 'J3': 'down', 'J4': 'down', 'J8': 'down'}

# Pinbenamingen op de BOVENKANT (daar steek/schroef je de draden in), één naam per regel.
# (richting t.o.v. de pad, teksthoek, {pad: tekst}, opties...)
#   'body'   : naast de behuizing (courtyard) i.p.v. naast de pad (schroefklemmen)
#   'both'   : op boven- én onderkant;  'big': grotere tekst (polariteit)
PIN_LABELS = {
    'J7': ('left', 0, {'1': 'GND', '2': '3V3', '3': 'SCL', '4': 'SDA'}),
    'J4': ('left', 0, {'1': 'VSYS', '2': '3V3', '3': 'GND', '4': 'IO6', '5': 'IO7', '6': 'IO17',
                       '7': 'IO18', '8': 'TX', '9': 'RX', '10': 'GND'}),
    'J8': ('left', 0, {'1': '3V3', '2': 'GND', '3': 'DIN', '4': 'CLK', '5': 'CS', '6': 'DC',
                       '7': 'RST', '8': 'BUSY'}),
    'J2': ('left', 0, {'1': '3V3', '2': 'DQ', '3': 'GND'}, 'body'),
    'J3': ('left', 0, {'1': '3V3', '2': 'DQ', '3': 'GND'}, 'body'),
    'D5': ('down', 0, {'2': '+'}, 'both', 'big'),   # anode van de accu-omgekeerd-LED
}
