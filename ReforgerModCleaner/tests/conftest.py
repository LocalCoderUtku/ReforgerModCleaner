"""Test ortamı: proje kökünü import yoluna ekler. tkinter kurulu değilse (ör. bazı Linux
konteynerleri) yerine boş bir taklit modül koyar; GUI zaten import sırasında kurulmuyor."""
import importlib.util
import os
import sys
import types

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

if importlib.util.find_spec("tkinter") is None:
    stub = types.ModuleType("tkinter")
    for sub in ("ttk", "font", "messagebox", "filedialog", "simpledialog"):
        m = types.ModuleType("tkinter." + sub)
        setattr(stub, sub, m)
        sys.modules["tkinter." + sub] = m

    class TclError(Exception):
        pass

    stub.TclError = TclError
    stub.TkVersion = 0.0
    sys.modules["tkinter"] = stub
