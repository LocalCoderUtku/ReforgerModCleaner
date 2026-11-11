"""GUI kurulum kodunu (if __name__ == "__main__" bloğu) sahte bir tkinter ile baştan sona çalıştırır.
Gerçek pencere açmaz; yanlış isim, eksik çeviri anahtarı, bozuk çağrı gibi hataları yakalar."""
import os
import runpy
import sys
import time
import types
from unittest.mock import MagicMock

SCRIPT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                      "reforger_mod_cleaner.py")


class FakeVar:
    def __init__(self, value=""):
        self.v, self.cbs = value, []

    def get(self):
        return self.v

    def set(self, v):
        self.v = v
        for cb in self.cbs:
            cb()

    def trace_add(self, _mode, cb):
        self.cbs.append(cb)


def make_fake_tk():
    tk = types.ModuleType("tkinter")

    class TclError(Exception):
        pass

    root = MagicMock(name="root")
    root.winfo_screenwidth.return_value = 1366
    root.winfo_screenheight.return_value = 768
    tk.TclError, tk.TkVersion, tk.StringVar = TclError, 8.6, FakeVar
    tk.Tk = lambda: root
    for name in ("Label", "Frame", "Canvas", "Button", "Entry", "Menu", "Toplevel", "Text"):
        setattr(tk, name, MagicMock(name=name))
    subs = {}
    for sub in ("ttk", "font", "messagebox", "filedialog", "simpledialog"):
        subs[sub] = MagicMock(name=sub)
        setattr(tk, sub, subs[sub])
    return tk, subs, root


def test_gui_block_runs_and_language_switch_works(tmp_path, monkeypatch):
    tk, subs, root = make_fake_tk()
    monkeypatch.setitem(sys.modules, "tkinter", tk)
    for sub, mod in subs.items():
        monkeypatch.setitem(sys.modules, "tkinter." + sub, mod)
    monkeypatch.setitem(sys.modules, "PIL", None)            # görsel hattı devre dışı
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    monkeypatch.setenv("APPDATA", str(tmp_path))
    monkeypatch.chdir(tmp_path)
    mod_dir = tmp_path / "AAAA"
    mod_dir.mkdir()
    (mod_dir / "ServerData.json").write_text(
        '{"id":"AAAA","name":"Base","revision":{"version":"1.0","dependencies":[]}}', encoding="utf-8")

    ns = runpy.run_path(SCRIPT, run_name="__main__")

    assert root.mainloop.called
    assert ns["LANG"] in ns["STRINGS"]
    assert ns["WIN_H"] <= 768 - 100                          # 1366x768 ekrana sığıyor
    assert len(ns["_i18n"]) >= 20                            # çevrilebilir widget'lar kayıtlı

    # tarama: worker thread bitince kuyruğu ana thread boşaltır
    for _ in range(100):
        ns["_poll_scan"]()
        if not ns["_scanning"]:
            break
        time.sleep(0.02)
    g = ns["rescan"].__globals__
    assert [m["id"] for m in g["all_mods"]] == ["AAAA"]

    # dil değiştir: iki yöne de hatasız geçmeli, filtre etiketi yeni dile dönmeli, ayar kaydedilmeli
    first = g["LANG"]
    ns["toggle_language"]()
    assert g["LANG"] != first
    assert g["server_filter_var"].get() == g["T"]("all")
    assert g["settings"]["lang"] == g["LANG"]
    ns["set_language"]("tr")
    g["server_filter_var"].set(g["T"]("untagged"))
    ns["set_language"]("en")
    assert g["server_filter_var"].get() == "(Untagged)"
    assert os.path.isfile(g["SETTINGS_FILE"])

    # diğer düğme işlevleri de iki dilde çökmeden çalışmalı
    subs["filedialog"].askdirectory.return_value = str(tmp_path)
    subs["filedialog"].askopenfilename.return_value = ""
    subs["simpledialog"].askstring.return_value = "Srv"
    for lang in ("tr", "en"):
        ns["set_language"](lang)
        for fn in ("on_analyze", "on_clear_filters", "select_untagged", "auto_group_dependencies",
                   "update_gauge", "update_stats", "open_auto_tag", "open_treemap", "tag_selected",
                   "open_selected", "delete_selected", "choose_background", "reset_background",
                   "choose_server_config_dir", "on_select_folder"):
            ns[fn]()
        ns["edit_tag"](g["all_mods"][0])
        assert g["tags"] == {"AAAA": "Srv"}
    ns["wipe_local_data"]()
    assert g["tags"] == {}
    ns["on_close"]()
