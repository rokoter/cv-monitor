# 3D-modellen

Alle footprints in `../cv_monitor.pretty` verwijzen naar deze map via `${KIPRJMOD}/3dmodels/…`.
Daardoor werkt de 3D-viewer in elke KiCad-versie, los van welke bibliotheekversie je hebt
geïnstalleerd. Dezelfde STEP-bestanden gebruiken we later voor de behuizing in FreeCAD.

Bekijken in KiCad: open `cv_monitor.kicad_pcb` en kies **Beeld → 3D-viewer** (Alt+3).

## Herkomst

| Bestand(en) | Bron | Licentie |
|---|---|---|
| alle overige `.step` | KiCad-3D-bibliotheek 7.0.11 (Ubuntu-pakket `kicad-packages3d`) | CC-BY-SA 4.0 met uitzondering voor gebruik in ontwerpen |
| `JST_SH_SM04B-SRSS-TB_1x04-1MP_P1.00mm_Horizontal.step` | KiCad-3D-bibliotheek 10.0.7 (zit niet in 7.0.11) | idem |
| `SOIC-8-1EP_…_EP2.35x2.35mm.step` | KiCad 7.0.11; gebruikt voor de TP4056 (EP 2,41 × 3,3 mm heeft geen eigen model; alleen de onderpad verschilt) | idem |
| `USB_C_Receptacle_HRO_TYPE-C-31-M-12.step` | zelf gegenereerd (`generator/make_3dmodels.py`): 8,94 × 7,3 × 3,2 mm, ovale voorkant | eigen werk |
| `SW_Push_1P1T_XKB_TS-1187A.step` | zelf gegenereerd: 5,1 × 5,1 mm, 1,5 mm hoog (TS-1187A-B-A-B, C318884) | eigen werk |
| `Cell_18650.step` | zelf gegenereerd: Ø 18,5 × 65 mm, als tweede model in de accuhouder | eigen werk |

De zelfgemaakte modellen zijn vereenvoudigd (buitenmaten kloppen, details niet). KiCad heeft voor
de HRO-USB-C en de XKB-drukknop geen 3D-model, ook niet in versie 10.

## Opnieuw maken

```
python3 generator/make_3dmodels.py <map met uitgepakte STEP-bestanden> hardware/cv_monitor/3dmodels
python3 generator/make_project_fps.py hardware/cv_monitor/cv_monitor.pretty
```
