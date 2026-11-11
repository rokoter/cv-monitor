"""Ontwerpbeschrijving CV-temperatuurmonitor (posities in rastereenheden van 2,54 mm).

Elke component: ref, lib (lib:symbool), value, gx/gy (midden), rot, footprint, LCSC, nets {pin: net}.
Netnaam 'NC' = bewust niet aangesloten (krijgt een no-connect kruisje).
"""

R0603 = 'Resistor_SMD:R_0603_1608Metric'
C0603 = 'Capacitor_SMD:C_0603_1608Metric'
C0805 = 'Capacitor_SMD:C_0805_2012Metric'
LED0603 = 'LED_SMD:LED_0603_1608Metric'

# LCSC-nummers basis-onderdelen JLCPCB (worden in de BOM-stap nogmaals gecontroleerd)
LC = {
    '5.1k': 'C23186', '2k': 'C22975', '1k': 'C21190', '100': 'C22775', '10k': 'C25804',
    '100k': 'C25803', '4.7k': 'C23162', '47k': 'C25819',
    '10u': 'C15850', '22u': 'C45783', '100n': 'C14663', '1u': 'C15849',
}

POWER_NETS = {'GND', '+3V3', 'VBUS'}


def R(ref, val, gx, gy, top, bot, rot=0, **kw):
    v = {'100': '100R'}.get(val, val)
    d = dict(ref=ref, lib='Device:R', value=v, gx=gx, gy=gy, rot=rot, fp=R0603, lcsc=LC[val],
             nets={'1': top, '2': bot})
    d.update(kw)
    return d


def C(ref, val, gx, gy, top, bot, size='0603', **kw):
    vv = {'10u': '10uF', '22u': '22uF', '100n': '100nF', '1u': '1uF'}[val]
    d = dict(ref=ref, lib='Device:C', value=vv, gx=gx, gy=gy, fp=C0805 if size == '0805' else C0603,
             lcsc=LC[val], nets={'1': top, '2': bot})
    d.update(kw)
    return d


def LED(ref, color, lcsc, gx, gy, a, k, rot=0, **kw):
    d = dict(ref=ref, lib='Device:LED', value=color, gx=gx, gy=gy, rot=rot, fp=LED0603, lcsc=lcsc,
             nets={'2': a, '1': k}, ref_at=(gx - 1.5, gy - 1.5), val_at=(gx - 1.5, gy + 2))
    d.update(kw)
    return d


COMPONENTS = [
    # ------------------------------------------------------------ 1. USB-C
    dict(ref='J1', lib='Connector:USB_C_Receptacle_USB2.0_16P', value='USB-C', gx=14, gy=20,
         fp='Connector_USB:USB_C_Receptacle_HRO_TYPE-C-31-M-12', lcsc='C165948',
         ref_at=(8, 10.5), val_at=(8, 11.5),
         nets={'A1': 'GND', 'A12': 'GND', 'B1': 'GND', 'B12': 'GND', 'S1': 'GND',
               'A4': 'VBUS_IN', 'A9': 'VBUS_IN', 'B4': 'VBUS_IN', 'B9': 'VBUS_IN',
               'A5': 'CC1', 'B5': 'CC2', 'A6': 'USB_D+', 'B6': 'USB_D+', 'A7': 'USB_D-', 'B7': 'USB_D-',
               'A8': 'NC', 'B8': 'NC'}),
    dict(ref='F1', lib='Device:Polyfuse', value='1,1A PTC', gx=36, gy=10, rot=90, lcsc='C269119',
         fp='Fuse:Fuse_1206_3216Metric', ref_at=(35, 8), val_at=(35, 12.5),
         nets={'1': 'VBUS_IN', '2': 'VBUS'}),
    R('R1', '5.1k', 28, 18, 'CC1', 'GND'),
    R('R2', '5.1k', 32, 18, 'CC2', 'GND'),
    C('C1', '1u', 36, 19, 'VBUS', 'GND'),
    dict(ref='U1', lib='Power_Protection:USBLC6-2SC6', value='USBLC6-2SC6', gx=30, gy=28,
         fp='Package_TO_SOT_SMD:SOT-23-6', lcsc='C7519', ref_at=(32, 25), val_at=(32, 31.5),
         nets={'1': 'USB_D+', '6': 'USB_D+', '3': 'USB_D-', '4': 'USB_D-', '5': 'VBUS', '2': 'GND'}),

    # ------------------------------------------------------------ 2. Lader
    dict(ref='U2', lib='cv_monitor:TP4056', value='TP4056', gx=62, gy=22, lcsc='C16581',
         label_wired={'4': True}, ref_at=(58, 18.5), val_at=(62, 18.5),
         fp='cv_monitor:SOIC-8-1EP_3.9x4.9mm_P1.27mm_EP2.41x3.3mm_ThermalVias_0.3mm',
         nets={'4': 'VBUS', '8': 'VBUS', '2': 'PROG', '1': 'TEMP', '5': 'BAT+', '7': 'CHRG',
               '6': 'STDBY', '3': 'GND', '9': 'GND'}),
    C('C2', '10u', 48, 22, 'VBUS', 'GND', '0805'),
    R('R3', '2k', 50, 28, 'PROG', 'GND'),
    R('R23', '4.7k', 68, 12, 'VBUS', 'TEMP'),
    R('R24', '47k', 72, 12, 'TEMP', 'GND'),
    R('R25', '10k', 77, 9, 'TEMP', 'NTC_JP'),
    dict(ref='JP1', lib='Jumper:SolderJumper_2_Bridged', value='zonder NTC: dicht', gx=77, gy=13.5, rot=270,
         fp='Jumper:SolderJumper-2_P1.3mm_Bridged_RoundedPad1.0x1.5mm', ref_at=(80.5, 12.8), val_at=(86, 14.8),
         nets={'1': 'NTC_JP', '2': 'GND'}),
    dict(ref='J9', lib='Connector_Generic:Conn_01x02', value='NTC 10k (accu)', gx=88, gy=19, pwr_rotate=True, dnp=True,
         fp='Connector_JST:JST_PH_B2B-PH-K_1x02_P2.00mm_Vertical', ref_at=(87, 17), val_at=(85, 22.5),
         nets={'1': 'TEMP', '2': 'GND'}),
    LED('D2', 'rood: laden', 'C2286', 73, 22, 'LEDR', 'CHRG'),
    R('R4', '1k', 78, 22, 'LEDR', 'VBUS', rot=90, ref_at=(77, 20.5), val_at=(77, 23.5)),
    LED('D3', 'groen: vol', 'C12624', 73, 27, 'LEDG', 'STDBY'),
    R('R5', '4.7k', 78, 27, 'LEDG', 'VBUS', rot=90, ref_at=(77, 25.5), val_at=(77, 28.5)),

    # ------------------------------------------------------------ 3. Power-path + LDO
    dict(ref='D1', lib='Diode:SS34', value='SS34', gx=104, gy=16, rot=180, fp='Diode_SMD:D_SMA',
         lcsc='C8678', ref_at=(103, 14), val_at=(103, 18.5), nets={'2': 'VBUS', '1': 'VSYS'}),
    dict(ref='Q1', lib='Transistor_FET:AO3401A', value='AO3401A', gx=104, gy=24,
         fp='Package_TO_SOT_SMD:SOT-23', lcsc='C15127', ref_at=(107, 23.5), val_at=(107, 25),
         nets={'1': 'VBUS', '2': 'VSYS', '3': 'BAT+'}),
    R('R8', '1k', 98, 25, 'VBUS', 'GND'),
    C('C5', '10u', 112, 22, 'VSYS', 'GND', '0805'),
    dict(ref='U4', lib='Regulator_Linear:AP2112K-3.3', value='AP2112K-3.3', gx=124, gy=18,
         fp='Package_TO_SOT_SMD:SOT-23-5', lcsc='C51118', ref_at=(121, 14.5), val_at=(121, 15.5),
         label_wired={'1': True},
         nets={'1': 'VSYS', '3': 'VSYS', '2': 'GND', '4': 'NC', '5': '+3V3'}),
    C('C6', '10u', 134, 20, '+3V3', 'GND', '0805'),

    # ------------------------------------------------------------ 4. Accu + beveiliging
    dict(ref='BT1', lib='Device:Battery_Cell', value='18650', gx=7, gy=55, extra={'MPN': 'houder MPD BK-18650-PC2'},
         fp='Battery:BatteryHolder_MPD_BH-18650-PC2', dnp=True, ref_at=(8.5, 54), val_at=(8.5, 55.5),
         nets={'1': 'CELL+', '2': 'B-'}),
    dict(ref='Q3', lib='Transistor_FET:AO3401A', value='AO3401A', gx=14, gy=50,
         fp='Package_TO_SOT_SMD:SOT-23', lcsc='C15127', ref_at=(16, 49.5), val_at=(16, 51),
         nets={'1': 'Q3_G', '3': 'CELL+', '2': 'BAT+'}),
    R('R22', '10k', 12, 53.5, 'Q3_G', 'B-'),
    C('C3', '10u', 20, 56, 'BAT+', 'GND', '0805'),
    R('R6', '100', 25, 49, 'BAT+', 'DW_VCC'),
    C('C4', '100n', 29, 49, 'DW_VCC', 'B-'),
    R('R7', '1k', 28, 58, 'DW_CS', 'GND'),
    LED('D5', 'rood 3mm THT: accu omgekeerd', '', 11, 62, 'REV_A', 'CELL+', ref_at=(10, 60.5), val_at=(6, 64.5),
        fp='LED_THT:LED_D3.0mm', dnp=True),
    R('R26', '1k', 16, 62, 'REV_A', 'REV_R', rot=90, ref_at=(15, 60.5), val_at=(15, 64)),
    dict(ref='D6', lib='Diode:1N4148W', value='1N4148W', gx=21, gy=62, fp='Diode_SMD:D_SOD-123', lcsc='C81598',
         ref_at=(20, 60.5), val_at=(19.5, 64), nets={'1': 'REV_R', '2': 'B-'}),
    dict(ref='U3', lib='cv_monitor:DW01A', value='DW01A', gx=40, gy=52, lcsc='C351410',
         fp='Package_TO_SOT_SMD:SOT-23-6', ref_at=(34, 48.5), val_at=(41, 48.5),
         nets={'5': 'DW_VCC', '2': 'DW_CS', '1': 'DW_OD', '3': 'DW_OC', '4': 'NC', '6': 'B-'}),
    dict(ref='Q2', lib='cv_monitor:FS8205A', value='AO8810 (8205A-compatibel)', gx=58, gy=52, lcsc='C21426',
         fp='Package_SO:TSSOP-8_4.4x3mm_P0.65mm', ref_at=(52, 48.5), val_at=(59, 48.5),
         nets={'4': 'DW_OD', '2': 'B-', '3': 'B-', '5': 'DW_OC', '6': 'GND', '7': 'GND',
               '1': 'NC', '8': 'NC'}),

    # ------------------------------------------------------------ 5. ESP32-S3
    dict(ref='U5', lib='RF_Module:ESP32-S3-WROOM-1', value='ESP32-S3-WROOM-1-N8 (zelf solderen)', gx=96, gy=62,
         fp='cv_monitor:ESP32-S3-WROOM-1_HandSolder', lcsc='C2913198', dnp=True, ref_at=(89, 49.5), val_at=(98, 74.5),
         nets={'2': '+3V3', '1': 'GND', '40': 'GND', '41': 'GND', '3': 'EN', '27': 'BOOT',
               '39': 'VBAT_SENSE', '38': 'VBUS_SENSE', '15': 'NC', '4': 'DQ_AANVOER', '5': 'DQ_RETOUR',
               '6': 'EXP_GPIO6', '7': 'EXP_GPIO7', '12': 'I2C_SDA', '17': 'I2C_SCL',
               '18': 'EPD_CS', '19': 'EPD_DIN', '20': 'EPD_CLK', '21': 'EPD_DC', '22': 'EPD_RST',
               '8': 'KNOP', '9': 'LED_STATUS', '10': 'EXP_GPIO17', '11': 'EXP_GPIO18',
               '13': 'USB_D-', '14': 'USB_D+', '23': 'EPD_BUSY', '37': 'UART_TX', '36': 'UART_RX',
               **{n: 'NC' for n in ['16', '24', '25', '26', '28', '29', '30', '31', '32', '33', '34', '35']}}),
    C('C8', '22u', 116, 44, '+3V3', 'GND', '0805'),
    C('C9', '100n', 120, 44, '+3V3', 'GND'),

    # ------------------------------------------------------------ 6. Metingen + sensoren
    R('R14', '100k', 132, 48, 'BAT+', 'VBAT_SENSE'),
    R('R15', '100k', 132, 54, 'VBAT_SENSE', 'GND'),
    C('C11', '100n', 140, 54, 'VBAT_SENSE', 'GND'),
    R('R16', '100k', 150, 48, 'VBUS', 'VBUS_SENSE'),
    R('R17', '100k', 150, 54, 'VBUS_SENSE', 'GND'),
    R('R18', '4.7k', 130, 64, '+3V3', 'DQ_AANVOER'),
    R('R27', '100', 142, 64, 'DQ_AANVOER', 'SENS1', rot=90, ref_at=(141, 62.5), val_at=(141, 66)),
    R('R19', '4.7k', 130, 72, '+3V3', 'DQ_RETOUR'),
    R('R28', '100', 142, 72, 'DQ_RETOUR', 'SENS2', rot=90, ref_at=(141, 70.5), val_at=(141, 74)),
    dict(ref='J2', lib='Connector:Screw_Terminal_01x03', value='SENSOR1 (aanvoer)', gx=150, gy=64, dnp=True,
         fp='TerminalBlock_Phoenix:TerminalBlock_Phoenix_PT-1,5-3-3.5-H_1x03_P3.50mm_Horizontal',
         ref_at=(152, 63), val_at=(152, 65), nets={'1': '+3V3', '2': 'SENS1', '3': 'GND'}),
    dict(ref='J3', lib='Connector:Screw_Terminal_01x03', value='SENSOR2 (retour)', gx=150, gy=72, dnp=True,
         fp='TerminalBlock_Phoenix:TerminalBlock_Phoenix_PT-1,5-3-3.5-H_1x03_P3.50mm_Horizontal',
         ref_at=(152, 71), val_at=(152, 73), nets={'1': '+3V3', '2': 'SENS2', '3': 'GND'}),
    C('C12', '100n', 159, 49, '+3V3', 'GND'),

    # ------------------------------------------------------------ 7. Bediening & uitbreiding
    R('R9', '10k', 10, 90, '+3V3', 'EN'),
    C('C10', '1u', 14, 95, 'EN', 'GND'),
    dict(ref='SW1', lib='Switch:SW_Push', value='RESET', gx=19, gy=95, rot=90,
         fp='Button_Switch_SMD:SW_Push_1P1T_XKB_TS-1187A', lcsc='C318884',
         ref_at=(20.5, 94.5), val_at=(20.5, 96), nets={'2': 'EN', '1': 'GND'}),
    R('R10', '10k', 27, 90, '+3V3', 'BOOT'),
    dict(ref='SW2', lib='Switch:SW_Push', value='BOOT', gx=32, gy=95, rot=90,
         fp='Button_Switch_SMD:SW_Push_1P1T_XKB_TS-1187A', lcsc='C318884',
         ref_at=(33.5, 94.5), val_at=(33.5, 96), nets={'2': 'BOOT', '1': 'GND'}),
    R('R11', '10k', 40, 90, '+3V3', 'KNOP'),
    dict(ref='SW3', lib='Switch:SW_Push', value='STATUS', gx=45, gy=95, rot=90,
         fp='Button_Switch_SMD:SW_Push_1P1T_XKB_TS-1187A', lcsc='C318884',
         ref_at=(46.5, 94.5), val_at=(46.5, 96), nets={'2': 'KNOP', '1': 'GND'}),
    R('R13', '1k', 54, 90, 'LED_STATUS', 'LEDB'),
    LED('D4', 'geel: status', 'C89811', 54, 96, 'LEDB', 'GND', rot=90,
        ref_at=(55.5, 95.5), val_at=(55.5, 98.5)),
    dict(ref='J4', lib='Connector_Generic:Conn_01x10', value='UITBREIDING (DNP)', gx=70, gy=96, dnp=True,
         pwr_rotate=True, stub={'2': 7.62}, fp='Connector_PinHeader_2.54mm:PinHeader_1x10_P2.54mm_Vertical',
         ref_at=(69, 90.5), val_at=(69, 103),
         nets={'1': 'VSYS', '2': '+3V3', '3': 'GND', '4': 'EXP_GPIO6', '5': 'EXP_GPIO7', '6': 'EXP_GPIO17',
               '7': 'EXP_GPIO18', '8': 'UART_TX', '9': 'UART_RX', '10': 'GND'}),

    # ------------------------------------------------------------ 8. Qwiic / STEMMA QT (I2C)
    R('R20', '4.7k', 80, 92, '+3V3', 'I2C_SDA'),
    R('R21', '4.7k', 85, 92, '+3V3', 'I2C_SCL'),
    dict(ref='J5', lib='Connector_Generic:Conn_01x04', value='QWIIC 1', gx=100, gy=93, lcsc='C160404',
         pwr_rotate=True, stub={'2': 7.62}, fp='Connector_JST:JST_SH_SM04B-SRSS-TB_1x04-1MP_P1.00mm_Horizontal',
         ref_at=(99, 90), val_at=(99, 97.5), nets={'1': 'GND', '2': '+3V3', '3': 'I2C_SDA', '4': 'I2C_SCL'}),
    dict(ref='J6', lib='Connector_Generic:Conn_01x04', value='QWIIC 2', gx=112, gy=93, lcsc='C160404',
         pwr_rotate=True, stub={'2': 7.62}, fp='Connector_JST:JST_SH_SM04B-SRSS-TB_1x04-1MP_P1.00mm_Horizontal',
         ref_at=(111, 90), val_at=(111, 97.5), nets={'1': 'GND', '2': '+3V3', '3': 'I2C_SDA', '4': 'I2C_SCL'}),

    # ------------------------------------------------------------ 9. Displays
    dict(ref='J8', lib='Connector_Generic:Conn_01x08', value='E-INK (DNP)', gx=138, gy=91, dnp=True,
         pwr_rotate=True, stub={'2': 7.62}, fp='Connector_PinHeader_2.54mm:PinHeader_1x08_P2.54mm_Vertical',
         ref_at=(137, 86.5), val_at=(140, 91),
         nets={'1': '+3V3', '2': 'GND', '3': 'EPD_DIN', '4': 'EPD_CLK', '5': 'EPD_CS', '6': 'EPD_DC',
               '7': 'EPD_RST', '8': 'EPD_BUSY'}),
    dict(ref='J7', lib='Connector_Generic:Conn_01x04', value='OLED I2C (DNP)', gx=153, gy=90, dnp=True,
         pwr_rotate=True, stub={'2': 7.62}, fp='Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical',
         ref_at=(152, 87), val_at=(150, 94.5),
         nets={'1': 'GND', '2': '+3V3', '3': 'I2C_SCL', '4': 'I2C_SDA'}),

    # ------------------------------------------------------------ Testpunten (alleen koperpads, geen BOM)
    dict(ref='TP1', lib='Connector:TestPoint', value='VBUS', gx=143, gy=37, rot=180, in_bom=False,
         fp='TestPoint:TestPoint_Pad_D1.5mm', ref_at=(143.8, 38), val_at=(143.8, 39), nets={'1': 'VBUS'}),
    dict(ref='TP2', lib='Connector:TestPoint', value='VSYS', gx=147, gy=37, rot=180, in_bom=False,
         fp='TestPoint:TestPoint_Pad_D1.5mm', ref_at=(147.8, 38), val_at=(147.8, 39), nets={'1': 'VSYS'}),
    dict(ref='TP3', lib='Connector:TestPoint', value='BAT+', gx=151, gy=37, rot=180, in_bom=False,
         fp='TestPoint:TestPoint_Pad_D1.5mm', ref_at=(151.8, 38), val_at=(151.8, 39), nets={'1': 'BAT+'}),
    dict(ref='TP4', lib='Connector:TestPoint', value='3V3', gx=155, gy=37, rot=180, in_bom=False,
         fp='TestPoint:TestPoint_Pad_D1.5mm', ref_at=(155.8, 38), val_at=(155.8, 39), nets={'1': '+3V3'}),
    dict(ref='TP5', lib='Connector:TestPoint', value='GND', gx=159, gy=36, in_bom=False,
         fp='TestPoint:TestPoint_Pad_D1.5mm', ref_at=(160, 37.5), val_at=(160, 38.5), nets={'1': 'GND'}),

    # ------------------------------------------------------------ Bevestigingsgaten M3 (behuizing)
    dict(ref='H1', lib='Mechanical:MountingHole', value='M3', gx=9, gy=110, in_bom=False,
         fp='MountingHole:MountingHole_3.2mm_M3', ref_at=(10.5, 109.5), val_at=(10.5, 111), nets={}),
    dict(ref='H2', lib='Mechanical:MountingHole', value='M3', gx=14, gy=110, in_bom=False,
         fp='MountingHole:MountingHole_3.2mm_M3', ref_at=(15.5, 109.5), val_at=(15.5, 111), nets={}),
    dict(ref='H3', lib='Mechanical:MountingHole', value='M3', gx=19, gy=110, in_bom=False,
         fp='MountingHole:MountingHole_3.2mm_M3', ref_at=(20.5, 109.5), val_at=(20.5, 111), nets={}),
    dict(ref='H4', lib='Mechanical:MountingHole', value='M3', gx=24, gy=110, in_bom=False,
         fp='MountingHole:MountingHole_3.2mm_M3', ref_at=(25.5, 109.5), val_at=(25.5, 111), nets={}),
]

# Directe draden tussen pinnen (optioneel 3e element = label midden op de draad)
WIRES = [
    (('U2', '8'), ('U2', '4')),          # CE aan VCC
    (('U2', '2'), ('R3', '1')),          # PROG -> R3
    (('U2', '7'), ('D2', '1')),          # CHRG -> rode LED kathode
    (('D2', '2'), ('R4', '1')),
    (('U2', '6'), ('D3', '1')),          # STDBY -> groene LED kathode (R5 4k7: even fel als de rode)
    (('D3', '2'), ('R5', '1')),
    (('U4', '3'), ('U4', '1')),          # EN aan VIN
    (('R13', '2'), ('D4', '2')),         # status-LED
    (('Q3', '1'), ('R22', '1')),         # gate ompoolbeveiliging
    (('D5', '2'), ('R26', '1')),         # fout-LED keten
    (('R25', '2'), ('JP1', '1')),        # vaste 10k via soldeerjumper
    (('R27', '2'), ('J2', '2')),         # serieweerstand sensor 1
    (('R28', '2'), ('J3', '2')),         # serieweerstand sensor 2
    (('R26', '2'), ('D6', '1')),
    (('R14', '2'), ('R15', '1'), 'VBAT_SENSE'),
    (('R16', '2'), ('R17', '1'), 'VBUS_SENSE'),
]

# PWR_FLAG markeringen: (soort, net, gx, gy)
FLAGS = [
    ('power', 'GND', 146, 14),
    ('power', 'VBUS', 154, 14),
    ('label', 'VSYS', 144, 24),
    ('label', 'B-', 151, 24),
    ('label', 'DW_VCC', 157, 24),
]

TEXTS = [
    dict(t='1. USB-C INGANG', gx=4, gy=6, size=2.0, bold=True),
    dict(t='F1: herstelbare zekering (1,1 A) beschermt tegen kortsluiting op het bord.\n'
           'CC1/CC2 met 5,1k naar GND: de adapter ziet een "sink" en levert 5 V.\n'
           'U1 USBLC6 (ESD): footprint aanwezig, in de POC niet bestukt. ESP32-S3 heeft native USB:\n'
           'flashen en loggen via dezelfde USB-C, geen USB-serieel chip nodig.', gx=4, gy=38),

    dict(t='2. LADER (TP4056)', gx=44, gy=6, size=2.0, bold=True),
    dict(t='Laadstroom = 1200 / R3 = 1200 / 2k = 600 mA\n'
           '(veilig voor elke 18650 en beperkt de warmte in de TP4056).\n'
           'CE aan VCC = altijd aan.\n'
           'Rode LED = bezig met laden, groene LED = vol.\n'
           'NTC: 10k B3950 op J9 tegen de accu -> laden alleen tussen ~1 en 46 C.\n'
           'Zonder NTC: JP1 dicht laten (vaste 10k = "25 C"). Met NTC: JP1 doorsnijden.', gx=44, gy=39),

    dict(t='3. POWER-PATH (UPS) + 3,3 V', gx=94, gy=6, size=2.0, bold=True),
    dict(t='USB aanwezig: gate Q1 = 5 V -> Q1 dicht. Systeem (VSYS ~4,6 V) via D1,\n'
           '   de accu wordt ongestoord geladen (TP4056 ziet alleen de accu).\n'
           'USB weg: R8 (1k) trekt de gate binnen ~10 ms naar 0 V -> Q1 geleidt -> accu voedt VSYS.\n'
           'AP2112K-3.3: LDO 600 mA, ~250 mV dropout. Werkt tot cel ~3,4 V.\n'
           'Voeding: lader >= 1 A gebruiken (laden 0,6 A + systeem); een pc-poort levert te weinig.', gx=94, gy=37),

    dict(t='PWR_FLAGS', gx=142, gy=6, size=2.0, bold=True),
    dict(t='Vertelt de ERC-controle waar een net\nzijn voeding vandaan krijgt.', gx=142, gy=30),

    dict(t='4. 18650 ACCU + BEVEILIGING', gx=4, gy=42, size=2.0, bold=True),
    dict(t='DW01A + AO8810 (8205A-type) schakelen af bij <2,4 V, >4,3 V of >~4 A.\n'
           'Let op: B- = min van de cel; GND (P-) = systeemmassa.\n'
           'De FET-schakelaar zit in de min-leiding.\n'
           'Q3 = ompoolbeveiliging: accu goed -> gate laag -> Q3 geleidt (laden en ontladen).\n'
           'Accu verkeerd om -> gate hoog -> Q3 blokkeert, er loopt geen stroom.\n'
           'D5 (rode 3 mm LED, onderkant bij de accu) brandt alleen als de accu verkeerd om zit.\n'
           'Na plaatsen van de accu: 1x USB aansluiten om de DW01A te activeren.', gx=4, gy=73),

    dict(t='5. ESP32-S3-WROOM-1-N8', gx=70, gy=42, size=2.0, bold=True),
    dict(t='Zelf solderen (randpads + GND-pad via de via\'s van onder).\n'
           'GPIO3/45/46 = strapping: bewust vrij. Antenne aan de PCB-rand!', gx=70, gy=80),

    dict(t='6. METINGEN + SENSOREN', gx=126, gy=42, size=2.0, bold=True),
    dict(t='VBAT: 100k/100k -> max 2,1 V op GPIO1 (ADC).\n'
           'VBUS: 100k/100k -> 2,5 V op GPIO2 = USB aanwezig.\n'
           'Klemmen = algemene poorten: 1 = 3V3, 2 = GPIO (4/5), 3 = GND.\n'
           'DS18B20: rood = 3V3, geel = DQ, zwart = GND (4,7k pull-up).\n'
           'R27/R28 (100R) in serie beschermen de GPIO bij lange kabels.', gx=126, gy=80.5),

    dict(t='7. BEDIENING & UITBREIDING', gx=4, gy=85, size=2.0, bold=True),
    dict(t='STATUS-knop (GPIO15): scherm verversen / accu tonen.\n'
           'J4: VSYS, 3V3, GND, GPIO6/7 (ADC), GPIO17/18, UART. Niet bestukt (DNP).', gx=4, gy=104),

    dict(t='8. QWIIC / STEMMA QT (I2C)', gx=78, gy=85, size=2.0, bold=True),
    dict(t='JST-SH: 1 = GND, 2 = 3V3, 3 = SDA (GPIO8), 4 = SCL (GPIO9).\n'
           'Doorlussen van modules (BME280, ADC, ...). Max ~300 mA uit 3V3.', gx=78, gy=104),

    dict(t='9. DISPLAYS', gx=126, gy=85, size=2.0, bold=True),
    dict(t='J8 e-ink (Waveshare-volgorde, SPI) en J7 OLED (I2C, gedeeld met Qwiic).\n'
           'Let op: controleer pinvolgorde van je module (VCC/GND verschilt soms).', gx=126, gy=98),
]
