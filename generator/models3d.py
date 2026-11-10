"""3D-modellen: altijd uit de projectmap (${KIPRJMOD}/3dmodels).

De modelpaden staan in de footprints van de projectbibliotheek (make_project_fps.py zet ze goed).
Zo werkt de 3D-viewer in elke KiCad-versie (7 t/m 10) zonder dat de juiste bibliotheekversie
geïnstalleerd hoeft te zijn, en zijn de STEP-bestanden direct bruikbaar voor de FreeCAD-behuizing.
"""
import os

PREFIX = '${KIPRJMOD}/3dmodels/'
# model dat KiCad niet heeft -> vervanger met hetzelfde huis (alleen de onderpad verschilt)
SUBST = {'SOIC-8-1EP_3.9x4.9mm_P1.27mm_EP2.41x3.3mm': 'SOIC-8-1EP_3.9x4.9mm_P1.27mm_EP2.35x2.35mm'}
# extra modellen per footprint: de 18650-cel in de accuhouder
EXTRA_BY_FP = {'BatteryHolder_MPD_BH-18650-PC2': ['Cell_18650']}


def check_models(board, model_dir):
    """Geeft de modellen terug waarnaar een footprint verwijst maar die niet in model_dir staan."""
    missing = set()
    for fp in board.GetFootprints():
        for m in fp.Models():
            fn = m.m_Filename
            if not fn.startswith(PREFIX):
                missing.add(f'{fp.GetReference()}: {fn} (niet uit de projectmap)')
            elif not os.path.exists(os.path.join(model_dir, fn[len(PREFIX):])):
                missing.add(fn[len(PREFIX):])
    return sorted(missing)
