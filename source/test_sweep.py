"""
test_sweep.py
Test del driver: genera 5 varianti con parametri diversi e verifica
che lo script gestisca la sequenza senza problemi.

Output: 5 file variant_*_full.step in variants/
Successivamente, lanciare extract_fairing.py per estrarre la sola carenatura.
"""

from pathlib import Path
from sw_driver import SolidWorksSession

SCRIPT_DIR = Path(__file__).parent.resolve()
MASTER_PATH = SCRIPT_DIR / "fairing_master.SLDPRT"
OUTPUT_DIR = SCRIPT_DIR / "variants"


PARAMETER_SETS = [
    ("baseline", {
        "fairing_length":     4000,
        "fairing_max_width":  1500,
        "fairing_max_height":  700,
    }),
    ("narrow", {
        "fairing_length":     4000,
        "fairing_max_width":  1100,
        "fairing_max_height":  700,
    }),
    ("wide", {
        "fairing_length":     4000,
        "fairing_max_width":  1800,
        "fairing_max_height":  700,
    }),
    ("low", {
        "fairing_length":     4000,
        "fairing_max_width":  1500,
        "fairing_max_height":  500,
    }),
    ("tall", {
        "fairing_length":     4000,
        "fairing_max_width":  1500,
        "fairing_max_height":  900,
    }),
]


def main():
    with SolidWorksSession(output_dir=OUTPUT_DIR, visible=True) as sw:
        sw.open_master(MASTER_PATH)
        sw.list_global_variables()

        results = []
        for variant_id, params in PARAMETER_SETS:
            print(f"\n--- Variante: {variant_id} ---")
            print(f"Parametri: {params}")
            try:
                step_path = sw.generate_variant(params, variant_id)
                size_kb = step_path.stat().st_size / 1024
                print(f"OK -> {step_path.name} ({size_kb:.1f} KB)")
                results.append((variant_id, step_path, "ok"))
            except Exception as e:
                print(f"FALLITA: {e}")
                results.append((variant_id, None, str(e)))

        print("\n" + "=" * 60)
        print("RIEPILOGO")
        print("=" * 60)
        for variant_id, path, status in results:
            print(f"  {variant_id:12s}  {status}")


if __name__ == "__main__":
    main()