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
    'F1': (11.0, 21.5, 90, 'F'),
    'C1': (11.0, 26.0, 90, 'F'),
    'U1': (11.5, 36.0, 0, 'F'),
    'R1': (11.0, 40.5, 0, 'F'),
    'R2': (11.0, 42.5, 0, 'F'),
    # ---- 2. Lader
    'D2': (9.0, 9.0, 180, 'F'), 'R4': (13.0, 9.0, 0, 'F'),
    'D3': (9.0, 11.5, 180, 'F'), 'R5': (13.0, 11.5, 0, 'F'),
    'C2': (18.0, 14.5, 90, 'F'),
    'U2': (25.0, 15.0, 0, 'F'),
    'R3': (25.0, 20.0, 0, 'F'),
    'R23': (32.5, 12.5, 0, 'F'), 'R24': (32.5, 14.5, 0, 'F'),
    'R25': (32.5, 16.5, 0, 'F'), 'JP1': (36.5, 16.5, 0, 'F'),
    # ---- 3. Power-path + LDO
    'D1': (23.0, 26.0, 0, 'F'),
    'Q1': (31.0, 26.5, 0, 'F'),
    'R8': (35.0, 23.0, 0, 'F'),
    'C5': (35.0, 30.0, 90, 'F'),
    'U4': (40.5, 27.0, 0, 'F'),
    'C6': (46.0, 27.0, 90, 'F'),
    # ---- Testpunten
    'TP1': (16.0, 40.0, 0, 'F'), 'TP2': (21.0, 40.0, 0, 'F'), 'TP3': (26.0, 40.0, 0, 'F'),
    'TP4': (31.0, 40.0, 0, 'F'), 'TP5': (36.0, 40.0, 0, 'F'),
    # ---- 4. Accu + beveiliging (boven de houder, die aan de onderkant zit)
    'BT1': (83.05, 58.7, 0, 'B'),
    'Q3': (15.0, 47.0, 0, 'F'), 'R22': (15.0, 51.0, 90, 'F'),
    'C3': (20.0, 47.0, 90, 'F'),
    'R6': (24.0, 46.0, 0, 'F'), 'C4': (24.0, 48.5, 0, 'F'),
    'U3': (30.0, 47.5, 0, 'F'), 'R7': (30.0, 51.5, 0, 'F'),
    'Q2': (38.0, 47.5, 0, 'F'),
    'D5': (22.0, 54.5, 180, 'F'), 'R26': (26.0, 54.5, 0, 'F'), 'D6': (31.0, 54.5, 180, 'F'),
    'J9': (41.5, 14.5, 0, 'F'),            # NTC: buiten de accuhouder (THT!), bij het TEMP-netwerk
    # ---- 5. ESP32-S3 (rechtsboven, antenne aan de bovenrand)
    'U5': (79.0, 13.4, 0, 'F'),            # antenne 0,65 mm van de bovenrand (silk binnen het bord)
    'C8': (65.0, 9.0, 0, 'F'), 'C9': (65.0, 11.5, 0, 'F'),
    'R9': (61.0, 13.5, 0, 'F'), 'C10': (61.0, 16.0, 0, 'F'),
    'R13': (65.0, 18.5, 0, 'F'), 'D4': (65.0, 21.0, 180, 'F'),
    'R10': (91.5, 26.0, 90, 'F'),
    # ---- 6. Metingen + sensoren (rechterrand)
    'R14': (64.0, 36.5, 0, 'F'), 'R15': (64.0, 39.5, 0, 'F'), 'C11': (68.5, 39.5, 0, 'F'),
    'R16': (73.0, 36.5, 0, 'F'), 'R17': (73.0, 39.5, 0, 'F'),
    'R18': (79.0, 40.0, 90, 'F'), 'R27': (82.0, 43.0, 0, 'F'),
    'R19': (79.0, 51.5, 90, 'F'), 'R28': (82.0, 54.5, 0, 'F'),
    'C12': (79.0, 47.0, 90, 'F'),
    'J2': (None, 45.5, 90, 'F'),           # x berekend: draadingang aan de rechterrand (pin 1 onder)
    'J3': (None, 57.0, 90, 'F'),
    # ---- 7. Bediening + uitbreiding (onderrand)
    'SW1': (11.0, 66.0, 0, 'F'), 'SW2': (19.5, 66.0, 0, 'F'), 'SW3': (28.0, 66.0, 0, 'F'),
    'R11': (28.0, 61.5, 0, 'F'),
    'J4': (56.0, 8.5, 0, 'F'),            # verticaal links van de ESP
    # ---- 8. Qwiic (onderrand, opening naar beneden)
    'R20': (50.0, 62.0, 90, 'F'), 'R21': (52.5, 62.0, 90, 'F'),
    'J5': (64.0, None, 0, 'F'), 'J6': (74.0, None, 0, 'F'),   # y berekend: opening aan de onderrand
    # ---- 9. Displays (bovenrand)
    'J8': (63.0, 30.5, 90, 'F'),           # e-ink direct onder de ESP
    'J7': (50.5, 8.5, 0, 'F'),             # OLED (THT): buiten de accuhouder, naast J4
}

# Onderdelen die met de 'opening' tegen een bordrand moeten: (rand, overstek in mm)
EDGE_ALIGN = {'J1': ('left', 0.0), 'J2': ('right', 0.0), 'J3': ('right', 0.0),
              'J5': ('bottom', 0.0), 'J6': ('bottom', 0.0)}
