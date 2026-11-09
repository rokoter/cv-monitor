"""Genereert de projectbibliotheek cv_monitor.kicad_sym (KiCad 7-formaat) met de
symbolen die in KiCad 7 ontbreken: ESP32-C3-MINI-1, TP4056, DW01A en FS8205A.
Pinnummers komen uit de datasheets (ESP32-C3-MINI-1 1-op-1 uit de officiële Espressif-bibliotheek)."""
import sys

F = '(effects (font (size 1.27 1.27)))'
FH = '(effects (font (size 1.27 1.27)) hide)'


def pin(typ, x, y, ang, length, name, num, hidden=False):
    h = ' hide' if hidden else ''
    return (f'      (pin {typ} line (at {x} {y} {ang}) (length {length}){h}\n'
            f'        (name "{name}" {F})\n        (number "{num}" {F})\n      )\n')


def symbol(name, ref, value, fp, ds, desc, rect, pins, ref_at, val_at):
    (x1, y1), (x2, y2) = rect
    s = f'  (symbol "{name}" (in_bom yes) (on_board yes)\n'
    s += f'    (property "Reference" "{ref}" (at {ref_at[0]} {ref_at[1]} 0) {F})\n'
    s += f'    (property "Value" "{value}" (at {val_at[0]} {val_at[1]} 0) {F})\n'
    s += f'    (property "Footprint" "{fp}" (at 0 0 0) {FH})\n'
    s += f'    (property "Datasheet" "{ds}" (at 0 0 0) {FH})\n'
    s += f'    (property "ki_description" "{desc}" (at 0 0 0) {FH})\n'
    s += f'    (symbol "{name}_0_1"\n'
    s += (f'      (rectangle (start {x1} {y1}) (end {x2} {y2}) '
          f'(stroke (width 0.254) (type default)) (fill (type background)))\n    )\n')
    s += f'    (symbol "{name}_1_1"\n'
    for p in pins:
        s += pin(*p)
    s += '    )\n  )\n'
    return s


def esp32c3():
    L, R = -25.4, 25.4
    pins = [
        ('power_in', 0, 30.48, 270, 5.08, '3V3', '3'),
        ('input', L, 20.32, 0, 5.08, 'EN', '8'),
        ('bidirectional', L, 15.24, 0, 5.08, 'GPIO0/ADC1_CH0', '12'),
        ('bidirectional', L, 12.7, 0, 5.08, 'GPIO1/ADC1_CH1', '13'),
        ('bidirectional', L, 7.62, 0, 5.08, 'GPIO2/ADC1_CH2', '5'),
        ('bidirectional', L, 5.08, 0, 5.08, 'GPIO3/ADC1_CH3', '6'),
        ('bidirectional', L, 2.54, 0, 5.08, 'GPIO4/ADC1_CH4', '18'),
        ('bidirectional', L, 0, 0, 5.08, 'GPIO5/ADC2_CH0', '19'),
        ('bidirectional', R, 20.32, 180, 5.08, 'GPIO18/USB_D-', '26'),
        ('bidirectional', R, 17.78, 180, 5.08, 'GPIO19/USB_D+', '27'),
        ('bidirectional', R, 12.7, 180, 5.08, 'GPIO20/U0RXD', '30'),
        ('bidirectional', R, 10.16, 180, 5.08, 'GPIO21/U0TXD', '31'),
        ('bidirectional', R, 5.08, 180, 5.08, 'GPIO6', '20'),
        ('bidirectional', R, 2.54, 180, 5.08, 'GPIO7', '21'),
        ('bidirectional', R, -2.54, 180, 5.08, 'GPIO8', '22'),
        ('bidirectional', R, -5.08, 180, 5.08, 'GPIO9', '23'),
        ('bidirectional', R, -10.16, 180, 5.08, 'GPIO10', '16'),
        ('power_in', 0, -30.48, 90, 5.08, 'GND', '1'),
    ]
    gnd_extra = ['2', '11', '14'] + [str(n) for n in range(36, 54)]
    for n in gnd_extra:
        pins.append(('passive', 0, -30.48, 90, 5.08, 'GND', n, True))
    nc = ['4', '7', '9', '10', '15', '17', '24', '25', '28', '29', '32', '33', '34', '35']
    for i, n in enumerate(nc):
        pins.append(('no_connect', -12.7 + (i % 7) * 2.54, -17.78 - (i // 7) * 2.54, 0, 0, 'NC', n, True))
    return symbol('ESP32-C3-MINI-1', 'U', 'ESP32-C3-MINI-1', 'cv_monitor:ESP32-C3-MINI-1',
                  'https://www.espressif.com/sites/default/files/documentation/esp32-c3-mini-1_datasheet_en.pdf',
                  'ESP32-C3 Wi-Fi/BLE module, 4MB flash, PCB-antenne',
                  ((-20.32, 25.4), (20.32, -25.4)), pins, (-20.32, 26.67), (-20.32, -26.67))


def esp32s3():
    """ESP32-S3-MINI-1(-N8): alle GPIO's zichtbaar (herbruikbaar), pinnummers volgens Espressif."""
    L, R = -27.94, 27.94
    left = [('input', 'EN', '45'), ('bidirectional', 'GPIO0/BOOT', '4'), ('bidirectional', 'GPIO1/ADC1_CH0', '5'),
            ('bidirectional', 'GPIO2/ADC1_CH1', '6'), ('bidirectional', 'GPIO3/STRAP', '7'),
            ('bidirectional', 'GPIO4/ADC1_CH3', '8'), ('bidirectional', 'GPIO5/ADC1_CH4', '9'),
            ('bidirectional', 'GPIO6/ADC1_CH5', '10'), ('bidirectional', 'GPIO7/ADC1_CH6', '11'),
            ('bidirectional', 'GPIO8/ADC1_CH7', '12'), ('bidirectional', 'GPIO9/ADC1_CH8', '13'),
            ('bidirectional', 'GPIO10/FSPICS0', '14'), ('bidirectional', 'GPIO11/FSPID', '15'),
            ('bidirectional', 'GPIO12/FSPICLK', '16'), ('bidirectional', 'GPIO13/FSPIQ', '17'),
            ('bidirectional', 'GPIO14', '18')]
    right = [('bidirectional', 'GPIO15', '19'), ('bidirectional', 'GPIO16', '20'), ('bidirectional', 'GPIO17', '21'),
             ('bidirectional', 'GPIO18', '22'), ('bidirectional', 'GPIO19/USB_D-', '23'),
             ('bidirectional', 'GPIO20/USB_D+', '24'), ('bidirectional', 'GPIO21', '25'),
             ('bidirectional', 'GPIO26', '26'), ('bidirectional', 'GPIO33', '28'), ('bidirectional', 'GPIO34', '29'),
             ('bidirectional', 'GPIO35', '31'), ('bidirectional', 'GPIO36', '32'), ('bidirectional', 'GPIO37', '33'),
             ('bidirectional', 'GPIO38', '34'), ('bidirectional', 'GPIO39/MTCK', '35'),
             ('bidirectional', 'GPIO40/MTDO', '36'), ('bidirectional', 'GPIO41/MTDI', '37'),
             ('bidirectional', 'GPIO42/MTMS', '38'), ('bidirectional', 'GPIO43/U0TXD', '39'),
             ('bidirectional', 'GPIO44/U0RXD', '40'), ('bidirectional', 'GPIO45/STRAP', '41'),
             ('bidirectional', 'GPIO46/STRAP', '44'), ('bidirectional', 'GPIO47', '27'),
             ('bidirectional', 'GPIO48', '30')]
    pins = [('power_in', 0, 38.1, 270, 5.08, '3V3', '3')]
    for i, (t, n, num) in enumerate(left):
        pins.append((t, L, round(30.48 - i * 2.54, 2), 0, 5.08, n, num))
    for i, (t, n, num) in enumerate(right):
        pins.append((t, R, round(30.48 - i * 2.54, 2), 180, 5.08, n, num))
    pins.append(('power_in', 0, -35.56, 90, 5.08, 'GND', '1'))
    for n in ['2', '42', '43'] + [str(i) for i in range(46, 66)]:
        pins.append(('passive', 0, -35.56, 90, 5.08, 'GND', n, True))
    return symbol('ESP32-S3-MINI-1', 'U', 'ESP32-S3-MINI-1', 'cv_monitor:ESP32-S3-MINI-1',
                  'https://www.espressif.com/sites/default/files/documentation/esp32-s3-mini-1_mini-1u_datasheet_en.pdf',
                  'ESP32-S3 Wi-Fi/BLE module, PCB-antenne',
                  ((-22.86, 33.02), (22.86, -30.48)), pins, (-22.86, 34.29), (-22.86, -31.75))


def tp4056():
    pins = [
        ('power_in', -15.24, 5.08, 0, 5.08, 'VCC', '4'),
        ('input', -15.24, 2.54, 0, 5.08, 'CE', '8'),
        ('passive', -15.24, -2.54, 0, 5.08, 'PROG', '2'),
        ('input', -15.24, -5.08, 0, 5.08, 'TEMP', '1'),
        ('power_out', 15.24, 5.08, 180, 5.08, 'BAT', '5'),
        ('open_collector', 15.24, 0, 180, 5.08, '~{CHRG}', '7'),
        ('open_collector', 15.24, -2.54, 180, 5.08, '~{STDBY}', '6'),
        ('power_in', 0, -12.7, 90, 5.08, 'GND', '3'),
        ('passive', 0, -12.7, 90, 5.08, 'EP', '9', True),
    ]
    return symbol('TP4056', 'U', 'TP4056', 'Package_SO:SOIC-8-1EP_3.9x4.9mm_P1.27mm_EP2.41x3.3mm_ThermalVias',
                  'https://www.lcsc.com/datasheet/C16581.pdf', '1A lineaire Li-ion lader, ESOP-8',
                  ((-10.16, 7.62), (10.16, -7.62)), pins, (-10.16, 8.89), (-10.16, -8.89))


def dw01a():
    pins = [
        ('power_in', -12.7, 2.54, 0, 5.08, 'VCC', '5'),
        ('input', -12.7, -2.54, 0, 5.08, 'CS', '2'),
        ('output', 12.7, 2.54, 180, 5.08, 'OD', '1'),
        ('output', 12.7, -2.54, 180, 5.08, 'OC', '3'),
        ('passive', 0, 10.16, 270, 5.08, 'TD', '4'),
        ('power_in', 0, -10.16, 90, 5.08, 'VSS', '6'),
    ]
    return symbol('DW01A', 'U', 'DW01A', 'Package_TO_SOT_SMD:SOT-23-6',
                  'https://www.lcsc.com/datasheet/C351410.pdf', '1-cel Li-ion beveiliging (over/onderspanning, overstroom)',
                  ((-7.62, 5.08), (7.62, -5.08)), pins, (-7.62, 6.35), (2.54, 6.35))


def fs8205a():
    pins = [
        ('input', -12.7, 2.54, 0, 5.08, 'G1', '4'),
        ('passive', -12.7, -2.54, 0, 5.08, 'S1', '2'),
        ('passive', -12.7, -2.54, 0, 5.08, 'S1', '3', True),
        ('input', 12.7, 2.54, 180, 5.08, 'G2', '5'),
        ('passive', 12.7, -2.54, 180, 5.08, 'S2', '6'),
        ('passive', 12.7, -2.54, 180, 5.08, 'S2', '7', True),
        ('passive', 0, 10.16, 270, 5.08, 'D', '1'),
        ('passive', 0, 10.16, 270, 5.08, 'D', '8', True),
    ]
    return symbol('FS8205A', 'Q', 'FS8205A', 'Package_SO:TSSOP-8_4.4x3mm_P0.65mm',
                  'https://www.lcsc.com/datasheet/C32254.pdf', 'Dubbele N-MOSFET, common drain, voor Li-ion beveiliging',
                  ((-7.62, 5.08), (7.62, -5.08)), pins, (-7.62, 6.35), (2.54, 6.35))


if __name__ == '__main__':
    out = '(kicad_symbol_lib (version 20220914) (generator cv_monitor_gen)\n'
    out += tp4056() + dw01a() + fs8205a() + ')\n'
    open(sys.argv[1], 'w').write(out)
    print('ok', sys.argv[1])
