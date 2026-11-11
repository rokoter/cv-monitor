# BOM voor JLCPCB-assemblage

Gegenereerd uit `generator/design.py`. Klasse gecontroleerd op 2026-11-11; bij bestellen telt wat de JLCPCB-BOM-tool toont.

## Door JLCPCB geplaatst (SMD)

| Referenties | Waarde | Footprint | LCSC | Klasse | Aantal | Opmerking |
|---|---|---|---|---|---|---|
| J1 | USB-C | USB_C_Receptacle_HRO_TYPE-C-31-M-12 | C165948 | Extended | 1 |  |
| F1 | 1,1A PTC | Fuse_1206_3216Metric | C269119 | Extended | 1 | geen basic PTC; C523825 uitverkocht |
| R1, R2 | 5.1k | R_0603_1608Metric | C23186 | Basic | 2 |  |
| C1, C10 | 1uF | C_0603_1608Metric | C15849 | Basic | 2 |  |
| U1 | USBLC6-2SC6 | SOT-23-6 | C7519 | Extended | 1 | ESD; D+/D- lopen door de chip, dus niet weglaten |
| U2 | TP4056 | SOIC-8-1EP_3.9x4.9mm_P1.27mm_EP2.41x3.3mm_ThermalVias_0.3mm | C16581 | Preferred | 1 | geen toeslag |
| C2, C3, C5, C6 | 10uF | C_0805_2012Metric | C15850 | Basic | 4 |  |
| R3 | 2k | R_0603_1608Metric | C22975 | Basic | 1 |  |
| R18, R19, R20, R21, R23 | 4.7k | R_0603_1608Metric | C23162 | Basic | 5 |  |
| R24 | 47k | R_0603_1608Metric | C25819 | Basic | 1 |  |
| R9, R10, R11, R22, R25 | 10k | R_0603_1608Metric | C25804 | Basic | 5 |  |
| D2 | rood: laden | LED_0603_1608Metric | C2286 | Basic | 1 |  |
| R4, R5, R7, R8, R13, R26 | 1k | R_0603_1608Metric | C21190 | Basic | 6 |  |
| D3 | wit: vol | LED_0603_1608Metric | C2290 | Basic | 1 | wit i.p.v. groen: groen/blauw 0603 zijn extended |
| D1 | SS34 | D_SMA | C8678 | Basic | 1 |  |
| Q1, Q3 | AO3401A | SOT-23 | C15127 | Basic | 2 |  |
| U4 | AP2112K-3.3 | SOT-23-5 | C51118 | Extended | 1 |  |
| R6, R27, R28 | 100R | R_0603_1608Metric | C22775 | Basic | 3 |  |
| C4, C9, C11, C12 | 100nF | C_0603_1608Metric | C14663 | Basic | 4 |  |
| D6 | 1N4148W | D_SOD-123 | C81598 | Basic | 1 |  |
| U3 | DW01A | SOT-23-6 | C351410 | Extended | 1 |  |
| Q2 | AO8810 (8205A-compatibel) | TSSOP-8_4.4x3mm_P0.65mm | C21426 | Extended | 1 | AOS, pin-compatibel met 8205A; C5148694 niet meer leverbaar |
| C8 | 22uF | C_0805_2012Metric | C45783 | Basic | 1 |  |
| R14, R15, R16, R17 | 100k | R_0603_1608Metric | C25803 | Basic | 4 |  |
| SW1, SW2, SW3 | RESET / BOOT / STATUS | SW_Push_1P1T_XKB_TS-1187A | C318884 | Basic | 3 |  |
| D4 | geel: status | LED_0603_1608Metric | C89811 | Preferred | 1 | geel i.p.v. blauw; preferred = geen toeslag |
| J5, J6 | QWIIC 1 / QWIIC 2 | JST_SH_SM04B-SRSS-TB_1x04-1MP_P1.00mm_Horizontal | C160404 | Extended | 2 | liggende JST-SH (Qwiic) |

**27 unieke onderdelen, waarvan 7 extended** (extended = eenmalige opstartkosten per uniek onderdeel per order).

## Zelf solderen (THT, niet in de JLCPCB-BOM)

| Referenties | Waarde | Footprint |
|---|---|---|
| J9 | NTC 10k (accu) | JST_PH_B2B-PH-K_1x02_P2.00mm_Vertical |
| BT1 | 18650 – houder MPD BK-18650-PC2 | BatteryHolder_MPD_BH-18650-PC2 |
| D5 | rood 3mm THT: accu omgekeerd | LED_D3.0mm |
| U5 | ESP32-S3-WROOM-1-N8 (zelf solderen) | ESP32-S3-WROOM-1_HandSolder |
| J2 | SENSOR1 (aanvoer) | TerminalBlock_Phoenix_PT-1,5-3-3.5-H_1x03_P3.50mm_Horizontal |
| J3 | SENSOR2 (retour) | TerminalBlock_Phoenix_PT-1,5-3-3.5-H_1x03_P3.50mm_Horizontal |
| J4 | UITBREIDING (DNP) | PinHeader_1x10_P2.54mm_Vertical |
| J8 | E-INK (DNP) | PinHeader_1x08_P2.54mm_Vertical |
| J7 | OLED I2C (DNP) | PinHeader_1x04_P2.54mm_Vertical |
