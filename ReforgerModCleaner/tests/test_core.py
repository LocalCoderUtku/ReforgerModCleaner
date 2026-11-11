"""GUI açmadan çalışan testler: veri fonksiyonları + tarama ve silme akışı (Tk taklit nesnelerle)."""
import hashlib
import json
import os
import subprocess
import sys
import time

import pytest

import reforger_mod_cleaner as app


# ---------- yardımcılar ----------
def write_mod(base, mid, name, deps=(), version="1.0", bom=False):
    p = os.path.join(base, mid)
    os.makedirs(p)
    enc = "utf-8-sig" if bom else "utf-8"
    with open(os.path.join(p, "ServerData.json"), "w", encoding=enc) as f:
        json.dump({"id": mid, "name": name,
                   "revision": {"version": version, "dependencies": list(deps)}}, f)
    with open(os.path.join(p, "data.pak"), "wb") as f:
        f.write(b"x" * 2048)
    return p


class Var:
    def __init__(self, v=""):
        self.v = v

    def get(self):
        return self.v

    def set(self, v):
        self.v = v


class FakeRoot:
    def __init__(self):
        self.jobs = []

    def after(self, _ms, fn):
        self.jobs.append(fn)
        return len(self.jobs)

    def update_idletasks(self):
        pass

    def run(self, limit=300):
        n = 0
        while self.jobs and n < limit:
            self.jobs.pop(0)()
            n += 1
            time.sleep(0.01)


class FakeMB:
    def __init__(self, answer=True):
        self.answer = answer
        self.calls = []

    def askyesno(self, title, *_a, **_k):
        self.calls.append(("ask", title))
        return self.answer

    def showerror(self, title, *_a, **_k):
        self.calls.append(("err", title))

    def showwarning(self, title, msg="", **_k):
        self.calls.append(("warn", title, msg))

    def showinfo(self, title, *_a, **_k):
        self.calls.append(("info", title))


@pytest.fixture
def gui(monkeypatch):
    """Modülün GUI global'lerini taklit nesnelerle doldurur."""
    root, mb, status = FakeRoot(), FakeMB(), Var()
    for name, val in {
        "LANG": "tr", "root": root, "messagebox": mb, "status_var": status, "settings": {}, "tags": {},
        "all_mods": [], "dependents": {}, "silinen_count": 0,
        "alert_big": set(), "alert_old": set(), "_scanning": False,
        "populate": lambda: None, "rebuild_server_filter": lambda: None,
        "save_tags": lambda: None, "game_running": lambda: False,
    }.items():
        monkeypatch.setattr(app, name, val, raising=False)
    return root, mb, status


# ---------- saf fonksiyonlar ----------
def test_server_color_deterministic_across_processes():
    code = ("import hashlib;print(hashlib.md5(b'srv', usedforsecurity=False).hexdigest())")
    outs = {subprocess.check_output([sys.executable, "-c", code]).strip() for _ in range(3)}
    assert len(outs) == 1
    assert app.server_color("srv") == app.server_color("srv")
    assert app.server_color("") == "#5a3030"
    assert hashlib.md5(b"srv", usedforsecurity=False).digest()  # 3.9+ imzası


@pytest.mark.parametrize("tokens,expected", [
    (["Cool Mod"], {"ABC123"}),      # tam ad
    (["ace"], set()),                # alt-dize eşleşmesi yok
    (["abc123"], {"ABC123"}),        # ID büyük/küçük harf duyarsız
    (["  Y  "], {"Y"}),              # boşluklar kırpılır
])
def test_match_exact_only(tokens, expected):
    mods = [{"id": "ABC123", "name": "Cool Mod"}, {"id": "X", "name": "Peace Keeper"},
            {"id": "Y", "name": "Super Cool Mod Pack"}]
    assert app.match_mods_by_tokens(mods, tokens) == expected


def test_version_sort():
    vs = ["1.10", "1.9", "1.9.1", "2.0", "0.9b", ""]
    assert sorted(vs, key=app.version_key) == ["", "0.9b", "1.9", "1.9.1", "1.10", "2.0"]


def test_dependencies_by_id_and_ambiguous_name():
    mods = [{"id": "A", "name": "Base", "deps": []},
            {"id": "C", "name": "Other", "deps": [{"modId": "A"}]}]
    assert app.build_dependents(mods)["A"] == {"C"}
    dup = [{"id": "A", "name": "Same", "deps": []}, {"id": "B", "name": "Same", "deps": []},
           {"id": "C", "name": "Other", "deps": [{"name": "Same"}]}]
    assert app.build_dependents(dup) == {"A": set(), "B": set(), "C": set()}


def test_dependency_clusters():
    mods = [{"id": "A", "name": "a", "deps": []}, {"id": "B", "name": "b", "deps": [{"modId": "A"}]},
            {"id": "C", "name": "c", "deps": []}]
    clusters = sorted(sorted(c) for c in app.dependency_clusters(mods))
    assert clusters == [["A", "B"], ["C"]]


def test_read_mod_meta_real_format_and_bom(tmp_path):
    p = write_mod(str(tmp_path), "59673B6FBB95459F", "BetterTracers", version="1.0.5", bom=True)
    assert app.read_mod_meta(p) == ("59673B6FBB95459F", "BetterTracers", "1.0.5", [])


def test_read_mod_meta_missing_or_broken(tmp_path):
    p = tmp_path / "NOJSON"
    p.mkdir()
    assert app.read_mod_meta(str(p)) == ("NOJSON", "NOJSON", "", [])
    (p / "ServerData.json").write_text("{bozuk", encoding="utf-8")
    assert app.read_mod_meta(str(p))[1] == "NOJSON"


def test_scan_mods(tmp_path):
    write_mod(str(tmp_path), "AAAA", "Base")
    write_mod(str(tmp_path), "BBBB", "Addon", deps=[{"modId": "AAAA"}])
    mods = {m["id"]: m for m in app.scan_mods(str(tmp_path))}
    assert set(mods) == {"AAAA", "BBBB"}
    assert mods["AAAA"]["size"] > 2000


def test_parse_server_config_with_bom(tmp_path):
    f = tmp_path / "srv.json"
    f.write_text(json.dumps({"game": {"name": "S1", "mods": [{"modId": "CCCC", "name": "x"}]}}),
                 encoding="utf-8-sig")
    assert app.parse_server_config(str(f)) == ("S1", ["CCCC"])


def test_import_server_configs_respects_manual_tags(tmp_path):
    (tmp_path / "a.json").write_text(json.dumps(
        {"game": {"name": "SrvA", "mods": [{"modId": "ABC123"}, {"modId": "X"}]}}), encoding="utf-8")
    mods = [{"id": "ABC123", "name": "Cool Mod"}, {"id": "X", "name": "Other"}]
    tags = {"ABC123": "Manual"}
    assert app.import_server_configs(str(tmp_path), mods, tags) == {"SrvA": 1}
    assert tags == {"ABC123": "Manual", "X": "SrvA"}
    app.import_server_configs(str(tmp_path), mods, tags, overwrite=True)
    assert tags["ABC123"] == "SrvA"


def test_extract_tokens():
    assert app.extract_tokens('{"mods":[{"modId":"Q","name":"N"}]}') == ["Q", "N"]
    assert app.extract_tokens('a, b\n"c"\n') == ["a", "b", "c"]


def test_squarify_skips_zero_sizes():
    rects = app.squarify([(10, "a", "r"), (5, "b", "g"), (0, "c", "b")], 0, 0, 100, 50)
    assert len(rects) == 2
    assert abs(sum(r[2] * r[3] for r in rects) - 5000) < 1e-6


# ---------- tarama akışı ----------
def test_rescan_queue_flow(tmp_path, gui, monkeypatch):
    root, _mb, status = gui
    write_mod(str(tmp_path), "AAAA", "Base")
    write_mod(str(tmp_path), "BBBB", "Addon", deps=[{"modId": "AAAA"}])
    monkeypatch.setattr(app, "selected_dir", Var(str(tmp_path)), raising=False)
    app.rescan()
    assert app._scanning is True
    app.rescan()                      # tarama sürerken ikinci çağrı yok sayılır
    root.run()
    assert app._scanning is False
    assert len(app.all_mods) == 2
    assert app.dependents["AAAA"] == {"BBBB"}
    assert status.get().startswith("2 mod")


def test_rescan_error_is_reported(tmp_path, gui, monkeypatch):
    root, mb, _ = gui
    monkeypatch.setattr(app, "selected_dir", Var(str(tmp_path)), raising=False)

    def boom(*_a):
        raise RuntimeError("boom")
    monkeypatch.setattr(app, "scan_mods", boom)
    app.rescan()
    root.run()
    assert app._scanning is False
    assert any(c[0] == "err" for c in mb.calls)


# ---------- silme akışı ----------
def test_delete_continues_after_failure(tmp_path, gui, monkeypatch):
    _root, mb, status = gui
    for mid in ("AAAA", "BBBB", "CCCC"):
        write_mod(str(tmp_path), mid, mid)
    app.all_mods[:] = app.scan_mods(str(tmp_path))
    deleted = []

    def fake_trash(p):
        if p.endswith("BBBB"):
            raise OSError("kilitli")
        deleted.append(p)
    monkeypatch.setattr(app, "send2trash", fake_trash)
    app.on_delete(list(app.all_mods))
    assert len(deleted) == 2
    assert [m["id"] for m in app.all_mods] == ["BBBB"]
    assert sum(1 for c in mb.calls if c[0] == "warn") == 1      # tek özet uyarı
    assert status.get().startswith("2 mod silindi")


def test_delete_dependency_warning_cancel(gui, monkeypatch):
    _root, mb, _ = gui
    mb.answer = False
    monkeypatch.setattr(app, "send2trash", lambda p: pytest.fail("silinmemeliydi"))
    app.all_mods[:] = [{"id": "A", "name": "A", "deps": [], "size": 1, "path": "/yok/A"},
                       {"id": "B", "name": "B", "deps": [{"modId": "A"}], "size": 1, "path": "/yok/B"}]
    monkeypatch.setattr(app, "dependents", app.build_dependents(app.all_mods))
    app.on_delete([app.all_mods[0]])
    assert mb.calls[0] == ("ask", "⚠ Bağımlılık Uyarısı")
    assert len(app.all_mods) == 2


def test_dependents_rebuilt_after_delete(tmp_path, gui, monkeypatch):
    write_mod(str(tmp_path), "AAAA", "Base")
    write_mod(str(tmp_path), "BBBB", "Addon", deps=[{"modId": "AAAA"}])
    app.all_mods[:] = app.scan_mods(str(tmp_path))
    monkeypatch.setattr(app, "dependents", app.build_dependents(app.all_mods))
    monkeypatch.setattr(app, "send2trash", lambda p: None)
    addon = next(m for m in app.all_mods if m["id"] == "BBBB")
    app.on_delete([addon])
    assert app.dependents == {"AAAA": set()}       # Base artık 'gerekli' değil


# ---------- dil / i18n ----------
def test_languages_have_same_keys_and_placeholders():
    import string
    tr, en = app.STRINGS["tr"], app.STRINGS["en"]
    assert set(tr) == set(en)
    fields = lambda s: {f for _, f, _, _ in string.Formatter().parse(s) if f}
    for key in tr:
        assert fields(tr[key]) == fields(en[key]), key


def test_T_switches_language_and_formats(monkeypatch):
    monkeypatch.setattr(app, "LANG", "en")
    assert app.T("all") == "(All)"
    assert app.T("deleted_status", n=2, mb=5) == "Deleted 2 mod(s) (~5 MB)."
    monkeypatch.setattr(app, "LANG", "tr")
    assert app.T("all") == "(Hepsi)"
    monkeypatch.setattr(app, "LANG", "xx")          # bilinmeyen dil İngilizceye düşer
    assert app.T("all") == "(All)"


def test_column_titles_are_translation_keys():
    for _key, title_key, *_ in app.COLUMNS:
        assert title_key in app.STRINGS["en"]


def test_delete_flow_in_english(tmp_path, gui, monkeypatch):
    _root, mb, status = gui
    monkeypatch.setattr(app, "LANG", "en")
    write_mod(str(tmp_path), "AAAA", "Base")
    app.all_mods[:] = app.scan_mods(str(tmp_path))
    monkeypatch.setattr(app, "send2trash", lambda p: None)
    app.on_delete(list(app.all_mods))
    assert mb.calls[0] == ("ask", "Confirm")
    assert status.get().startswith("Deleted 1 mod(s)")


def test_bundled_assets_exist():
    for name in ("background.png", "icon.ico"):
        assert os.path.isfile(app.resource_path(os.path.join("assets", name)))
