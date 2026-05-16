"""
sw_driver.py
Driver per SolidWorks via COM. Espone una classe SolidWorksSession che
mantiene aperta una singola istanza di SolidWorks e permette di generare
varianti parametriche del fairing_master come file STEP.

Esporta lo STEP completo (carenatura + proxy). Per estrarre solo la
carenatura, usa lo script extract_fairing.py dopo questo.
"""

import time
import pythoncom
import win32com.client
from pathlib import Path

SW_DOC_PART = 1


class SolidWorksSession:
    """Context manager per una sessione SolidWorks."""

    def __init__(self, output_dir, visible=True):
        self.output_dir = Path(output_dir).resolve()
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.visible = visible
        self.sw = None
        self.model = None

    def __enter__(self):
        pythoncom.CoInitialize()
        print("Connessione a SolidWorks...")
        self.sw = win32com.client.Dispatch("SldWorks.Application")
        self.sw.Visible = self.visible
        self.sw.UserControl = False
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pythoncom.CoUninitialize()
        return False

    def open_master(self, master_path):
        master_path = Path(master_path).resolve()
        if not master_path.exists():
            raise FileNotFoundError(f"Master non trovato: {master_path}")

        # Verifica se il file e' gia' aperto in SolidWorks
        opened_docs = self.sw.GetDocuments
        if opened_docs:
            for doc in opened_docs:
                if Path(doc.GetPathName).resolve() == master_path:
                    print(f"File gia' aperto, riuso: {master_path.name}")
                    self.model = doc
                    return self.model

        print(f"Apertura {master_path.name}...")
        errors = win32com.client.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, 0)
        warnings = win32com.client.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, 0)
        self.model = self.sw.OpenDoc6(
            str(master_path), SW_DOC_PART, 0, "", errors, warnings
        )
        if self.model is None:
            raise RuntimeError(f"Apertura fallita. errors={errors.value}")
        time.sleep(1)
        return self.model

    def list_global_variables(self):
        """Stampa tutte le equazioni (utile per debug)."""
        eq_mgr = self.model.GetEquationMgr
        n = eq_mgr.GetCount
        print(f"Equazioni nel modello ({n}):")
        for i in range(n):
            print(f"  [{i}] {eq_mgr.Equation(i)}")

    def list_bodies(self):
        """Stampa il nome di tutti i body solidi presenti nel modello."""
        bodies = self.model.GetBodies2(0, False)
        if bodies is None:
            print("Nessun body trovato.")
            return []
        names = []
        print(f"Body solidi nel modello ({len(bodies)}):")
        for i, body in enumerate(bodies):
            name = body.Name
            print(f"  [{i}] {name}")
            names.append(name)
        return names

    def set_global_variable(self, name, value):
        """Aggiorna una Global Variable. Solleva KeyError se non esiste."""
        eq_mgr = self.model.GetEquationMgr
        n = eq_mgr.GetCount
        prefix = f'"{name}"'
        for i in range(n):
            eq_str = eq_mgr.Equation(i)
            if eq_str.lstrip().startswith(prefix):
                new_eq = f'{prefix} = {value}'
                eq_mgr.Equation(i, new_eq)
                return
        raise KeyError(
            f"Global variable '{name}' non trovata. "
            f"Verifica che esista in Strumenti -> Equazioni."
        )

    def rebuild(self):
        """Force rebuild. Solleva RuntimeError se la geometria fallisce."""
        if not self.model.ForceRebuild3(False):
            raise RuntimeError("Rebuild fallito (geometria invalida).")

    def export_step(self, output_path):
        """Esporta il modello attuale come STEP completo."""
        output_path = Path(output_path)
        if output_path.exists():
            output_path.unlink()
        self.model.SaveAs(str(output_path))
        time.sleep(2)
        if not output_path.exists():
            raise RuntimeError(f"Export fallito: file non creato {output_path}")
        return output_path

    def generate_variant(self, params, variant_id):
        """Genera una variante: applica parametri, rebuild, esporta STEP completo.

        Args:
            params: dict {nome_global_var: valore}
            variant_id: stringa identificativa del variant

        Returns:
            Path dello STEP completo generato (suffisso _full).
        """
        for name, value in params.items():
            self.set_global_variable(name, value)
        self.rebuild()
        out_path = self.output_dir / f"variant_{variant_id}_full.step"
        self.export_step(out_path)
        return out_path