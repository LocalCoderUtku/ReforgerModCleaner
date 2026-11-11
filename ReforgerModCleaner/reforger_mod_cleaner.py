"""Reforger Mod Cleaner (unofficial) — tag Arma Reforger mods by server, free up space, clean up safely.

Arayüz Türkçe ve İngilizce; metinler STRINGS tablosunda.

Konsolsuz çalıştırmak için:  pythonw reforger_mod_cleaner.py
Exe üretmek için:            build.bat
"""
import os
import sys
import ctypes
import json
import math
import random
import hashlib
import logging
import tempfile
import queue
import threading
import subprocess
import colorsys
import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog, ttk
from tkinter import font as tkfont
from datetime import datetime

try:
    from send2trash import send2trash
except ImportError:
    send2trash = None

try:
    from PIL import Image, ImageEnhance, ImageFilter, ImageTk
    HAVE_PIL = True
except ImportError:
    HAVE_PIL = False

APP_NAME = "ReforgerModCleaner"
APP_VERSION = "1.0.0"

# --- Loglama: sessiz except'lerin yerine %TEMP%/ReforgerModCleaner.log ---
LOG_FILE = os.path.join(tempfile.gettempdir(), APP_NAME + ".log")
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, encoding="utf-8",
                    format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(APP_NAME)

# --- Tema (askeri-fütüristik HUD) ---
BG_COLOR = "#0a141b"
PANEL_BG = "#0b1820"       # cam panellerin iç widget zemini
GLASS_TINT = (10, 28, 36)  # cam katman rengi
HEADER_COLOR = "#27e8d6"   # ana cyan (başlık, vurgu, kenarlık)
BTN_HOVER = "#16c7c0"      # ikincil cyan (hover)
ROW_EVEN = "#11212b"
ROW_ODD = "#0d1a22"
SELECT_BG = "#1d5a59"
FG_COLOR = "#dff6f8"
BTN_COLOR = "#0e2a33"
BADGE_COLOR = "#e0d35a"
ORPHAN_COLOR = "#ff8e8e"
REQUIRED_COLOR = "#9ec5ff"
DIM = "#8fb3bd"

# --- Veri dosyaları ---
HOME = os.path.expanduser("~")
_DATA_DIR = os.path.join(os.environ.get("APPDATA", HOME), APP_NAME) if os.name == "nt" \
    else os.path.join(HOME, ".config", APP_NAME)
TAG_FILE = os.path.join(_DATA_DIR, "tags.json")
SETTINGS_FILE = os.path.join(_DATA_DIR, "settings.json")
# Eski sürüm (~/.arma_reforger_mod_*.json) dosyaları varsa ilk açılışta oradan okunur
_OLD_TAG_FILE = os.path.join(HOME, ".arma_reforger_mod_tags.json")
_OLD_SETTINGS_FILE = os.path.join(HOME, ".arma_reforger_mod_settings.json")

GAME_EXES = ("ArmaReforgerSteam.exe", "ArmaReforger.exe")

# Pencere/yerleşim: ekran boyutuna göre root oluşturulduktan sonra hesaplanır (compute_layout)
WIN_W, WIN_H = 1180, 740
M = 16
R_HEADER = R_TOOLBAR = R_RIGHT = R_TABLE = (0, 0, 0, 0)

# (anahtar, başlık çeviri anahtarı, genişlik, hizalama)
COLUMNS = [
    ("name", "col_name", 250, "w"),
    ("version", "col_version", 80, "w"),
    ("size", "col_size", 90, "e"),
    ("date", "col_date", 140, "center"),
    ("server", "col_server", 150, "w"),
]


# ==================== DİL / LANGUAGE ====================
LANG = "en"   # açılışta ayardan ya da sistem dilinden belirlenir

STRINGS = {
    "tr": {
        "t_warn": "Uyarı", "t_info": "Bilgi", "t_err": "Hata", "t_result": "Sonuç", "t_done": "Bitti",
        "all": "(Hepsi)", "untagged": "(Etiketsiz)",
        "win_title": "Reforger Mod Cleaner v{v} — resmî değildir",
        "subtitle": "modları sunuculara göre yönet · yer aç · güvenle temizle   |   "
                    "resmî değildir — Bohemia Interactive ile bağlantısı yoktur",
        "lang_btn": "Dil: TR",
        "col_name": "İSİM", "col_version": "SÜRÜM", "col_size": "BOYUT", "col_date": "TARİH",
        "col_server": "SUNUCU",
        "b_folder": "▣ Klasör", "b_refresh": "⟳ Yenile", "b_analyze": "⚠ Analiz",
        "b_treemap": "▦ Boyut Haritası", "b_bg": "▨ Arka Plan", "b_wipe": "✕ Yerel Veriyi Sil",
        "l_search": "Ara:", "l_minmb": "Min MB:", "l_server": "Sunucu:",
        "l_hint": "(başlığa tıkla = sırala  •  satıra çift tık = etiketle)",
        "b_sel_untagged": "Etiketsizleri Seç", "b_open": "Seçileni Aç", "b_tag": "Seçilenleri Etiketle",
        "b_autotag": "Otomatik Etiketle", "b_group": "Bağımlılığa Göre Grupla",
        "b_cfg": "Sunucu Config Klasörü", "b_delete": "Seçilenleri Sil", "b_clear": "Filtreleri Temizle",
        "h_dist": "SUNUCU DAĞILIMI",
        "transparency": "İnternete bağlanmaz. Yalnızca kendi etiket/ayar ve hata günlüğü dosyalarına yazar.",
        "legend": "⛓ = başka mod buna bağımlı (silme!)\nKırmızı = etiketsiz ve bağımsız (işaretlenmemiş)",
        "m_open": "Klasörü Aç", "m_tag": "Etiketle…", "m_delete": "Sil",
        "tags_save_fail": "Etiketler kaydedilemedi.\n{path}",
        "folder_open_fail": "Klasör açılamadı:\n{err}",
        "need_pillow": "Arka plan için Pillow gerekiyor:\npip install Pillow",
        "bg_pick_title": "Arka plan görseli seç", "ft_images": "Görseller", "ft_all": "Tümü",
        "scanning": "Taranıyor…", "scanning_n": "Taranıyor… {i}/{n}",
        "scan_err_status": "Tarama hatası — ayrıntı günlükte",
        "scan_err_msg": "Klasör taranamadı:\n{err}\n\nGünlük: {log}",
        "status_mods": "{n} mod • {folder}",
        "status_mapped": "{n} mod • {m} yeni mod eşlendi ({s} sunucu)",
        "analyze_done": "En büyük ve en eski modlar ⚠ işaretlendi.",
        "tag_title": "Sunucu / Etiket",
        "tag_prompt": "{name}\n(ID: {id})\n\nHangi sunucuya ait?  (Boş = etiketi sil)",
        "select_first": "Önce listeden mod seç (Ctrl/Shift ile çoklu).",
        "bulk_title": "Toplu Etiket",
        "bulk_prompt": "Seçili {n} mod hangi sunucuya ait?  (Boş = sil)",
        "game_title": "⚠ Oyun Açık",
        "game_msg": "Arma Reforger şu an çalışıyor. Oyun açıkken mod klasörü silmek dosya kilidi "
                    "yüzünden yarım kalabilir ve modu bozabilir.\n\nYine de devam edilsin mi?",
        "dep_title": "⚠ Bağımlılık Uyarısı",
        "dep_line": "• {name}  ←  gerekiyor: {names}",
        "dep_msg": "Silmek üzere olduğun bazı modlara, SİLMEYECEĞİN modlar bağımlı.\n"
                   "Silersen o modlar düzgün çalışmayabilir:\n\n{lines}\n\nYine de devam edilsin mi?",
        "del_title": "Dikkat",
        "del_msg": "{n} mod Geri Dönüşüm Kutusu'na gönderilsin mi?\nAçılacak yer: ~{mb} MB\n\n{names}",
        "no_s2t": "send2trash kurulu değil.\npip install Send2Trash",
        "deleting": "Siliniyor…", "deleted_status": "{n} mod silindi (~{mb} MB).",
        "del_failed": "{n} mod silinemedi:\n\n{lines}\n\nAyrıntı: {log}",
        "gauge": "Seçili: {mb} MB  ({pct}% / 10 GB)",
        "stats": "Görünen: {shown}/{total}\nEtiketsiz: {orphans}\nBağımsız+etiketsiz: {free}\n"
                 "Bu oturumda silinen: {deleted}",
        "no_data": "Henüz veri yok.",
        "scan_first": "Önce bir klasör tara.",
        "at_title": "Sunucu Listesinden Otomatik Etiketle", "at_server": "Sunucu adı:",
        "at_hint": "Mod listesini yapıştır (her satıra bir mod ID veya TAM mod adı;\n"
                   "sunucu config JSON'u da olur — Reforger mod preset JSON'u dahil):",
        "at_need_server": "Sunucu adı gir.",
        "at_none": "Eşleşen mod bulunamadı.\n(ID veya mod adı birebir eşleşmeli.)",
        "at_done": "{n} mod '{server}' olarak etiketlendi.", "at_apply": "Eşleştir ve Etiketle",
        "su_hint": "Henüz hiçbir mod etiketlenmemiş; bu durumda bağımsız modların TAMAMI seçilir.\n"
                   "Önce kullandığın sunucuların modlarını etiketle (satıra çift tık / Sunucu Config "
                   "Klasörü), sonra kalanları seç.",
        "su_status": "{n} etiketsiz/bağımsız mod seçildi — gözden geçirip silebilirsin.",
        "su_none": "Etiketsiz + bağımsız mod yok.",
        "group_name": "Otomatik Grup {i}",
        "group_done": "{n} mod, bağımlılıklarına göre {g} gruba ayrıldı.\n"
                      "Bir grubu yeniden adlandırmak için etikete çift tıkla.",
        "group_none": "Gruplanacak bağımlı (etiketsiz) mod bulunamadı.",
        "cfg_pick_title": "Sunucu config (.json) klasörünü seç",
        "cfg_saved_title": "Kaydedildi",
        "cfg_saved": "Config klasörü kaydedildi. Mod listesi taranınca otomatik eşlenecek.",
        "cfg_over_title": "Mevcut etiketler",
        "cfg_over_msg": "Config'lerdeki sunucu adları, elle verdiğin mevcut etiketlerin ÜZERİNE "
                        "yazılsın mı?\nHayır = sadece etiketsiz modlar doldurulur.",
        "cfg_done_title": "Eşlendi",
        "cfg_done": "{n} mod, {s} sunucuya etiketlendi.\nBundan sonra her açılışta bu klasör taranıp "
                    "yalnızca ETİKETSİZ modlar doldurulur.",
        "cfg_none": "Bu klasördeki config'lerde yeni eşleşen mod bulunamadı.\n"
                    "(Reforger sunucu config.json dosyaları olmalı.)",
        "tm_title": "Boyut Haritası — alan ∝ disk kullanımı",
        "tm_info": "Renk = sunucu • Büyük kutu = çok yer kaplıyor • Tıkla = bilgi",
        "tm_click": "{name}  •  {mb} MB  •  Sunucu: {server}  •  {dep}",
        "tm_dep_yes": "başka modlar buna bağımlı", "tm_dep_no": "bağımlı yok",
        "wipe_title": "Yerel Veriyi Sil",
        "wipe_msg": "Şu dosyalar diskten silinecek:\n\n  • {tags}\n  • {settings}\n\n"
                    "Bu, etiketlediğin tüm mod→sunucu eşlemelerini ve seçtiğin arka plan/config "
                    "klasörünü geri alamayacağın şekilde silecek. Mod dosyalarına dokunmaz.\n\n"
                    "Devam edilsin mi?",
        "wipe_done": "{n} dosya silindi. Etiketler de sıfırlandı.",
    },
    "en": {
        "t_warn": "Warning", "t_info": "Info", "t_err": "Error", "t_result": "Result", "t_done": "Done",
        "all": "(All)", "untagged": "(Untagged)",
        "win_title": "Reforger Mod Cleaner v{v} — unofficial",
        "subtitle": "manage mods by server · free up space · clean up safely   |   "
                    "unofficial — not affiliated with Bohemia Interactive",
        "lang_btn": "Language: EN",
        "col_name": "NAME", "col_version": "VERSION", "col_size": "SIZE", "col_date": "DATE",
        "col_server": "SERVER",
        "b_folder": "▣ Folder", "b_refresh": "⟳ Refresh", "b_analyze": "⚠ Analyze",
        "b_treemap": "▦ Size Map", "b_bg": "▨ Background", "b_wipe": "✕ Wipe Local Data",
        "l_search": "Search:", "l_minmb": "Min MB:", "l_server": "Server:",
        "l_hint": "(click a header = sort  •  double-click a row = tag)",
        "b_sel_untagged": "Select Untagged", "b_open": "Open Selected", "b_tag": "Tag Selected",
        "b_autotag": "Auto-Tag", "b_group": "Group by Dependency",
        "b_cfg": "Server Config Folder", "b_delete": "Delete Selected", "b_clear": "Clear Filters",
        "h_dist": "SERVER BREAKDOWN",
        "transparency": "Works offline. Writes only its own tag/settings files and an error log.",
        "legend": "⛓ = another mod depends on it (keep!)\nRed = untagged, nothing depends on it",
        "m_open": "Open Folder", "m_tag": "Tag…", "m_delete": "Delete",
        "tags_save_fail": "Could not save tags.\n{path}",
        "folder_open_fail": "Could not open the folder:\n{err}",
        "need_pillow": "Custom backgrounds need Pillow:\npip install Pillow",
        "bg_pick_title": "Choose a background image", "ft_images": "Images", "ft_all": "All files",
        "scanning": "Scanning…", "scanning_n": "Scanning… {i}/{n}",
        "scan_err_status": "Scan failed — see the log",
        "scan_err_msg": "Could not scan the folder:\n{err}\n\nLog: {log}",
        "status_mods": "{n} mods • {folder}",
        "status_mapped": "{n} mods • {m} newly tagged ({s} servers)",
        "analyze_done": "Largest and oldest mods are marked ⚠.",
        "tag_title": "Server / Tag",
        "tag_prompt": "{name}\n(ID: {id})\n\nWhich server is it for?  (Empty = remove tag)",
        "select_first": "Select mods in the list first (Ctrl/Shift for several).",
        "bulk_title": "Bulk Tag",
        "bulk_prompt": "Which server do the {n} selected mod(s) belong to?  (Empty = remove)",
        "game_title": "⚠ Game Is Running",
        "game_msg": "Arma Reforger is running. Deleting a mod folder while the game is open can stop "
                    "halfway because of locked files and leave the mod broken.\n\nContinue anyway?",
        "dep_title": "⚠ Dependency Warning",
        "dep_line": "• {name}  ←  needed by: {names}",
        "dep_msg": "Mods you are NOT deleting depend on some of the mods you are about to delete.\n"
                   "Those mods may stop working:\n\n{lines}\n\nContinue anyway?",
        "del_title": "Confirm",
        "del_msg": "Send {n} mod(s) to the Recycle Bin?\nSpace to free: ~{mb} MB\n\n{names}",
        "no_s2t": "send2trash is not installed.\npip install Send2Trash",
        "deleting": "Deleting…", "deleted_status": "Deleted {n} mod(s) (~{mb} MB).",
        "del_failed": "{n} mod(s) could not be deleted:\n\n{lines}\n\nDetails: {log}",
        "gauge": "Selected: {mb} MB  ({pct}% / 10 GB)",
        "stats": "Shown: {shown}/{total}\nUntagged: {orphans}\nUntagged+independent: {free}\n"
                 "Deleted this session: {deleted}",
        "no_data": "No data yet.",
        "scan_first": "Scan a folder first.",
        "at_title": "Auto-Tag from a Server Mod List", "at_server": "Server name:",
        "at_hint": "Paste the mod list (one mod ID or EXACT mod name per line;\n"
                   "a server config JSON or the Reforger mod preset JSON also works):",
        "at_need_server": "Enter a server name.",
        "at_none": "No matching mods found.\n(The ID or mod name must match exactly.)",
        "at_done": "{n} mod(s) tagged as '{server}'.", "at_apply": "Match and Tag",
        "su_hint": "No mods are tagged yet, so ALL independent mods will be selected.\n"
                   "Tag the mods of the servers you play on first (double-click a row / Server Config "
                   "Folder), then select the rest.",
        "su_status": "{n} untagged/independent mod(s) selected — review before deleting.",
        "su_none": "No untagged + independent mods.",
        "group_name": "Auto Group {i}",
        "group_done": "{n} mods were put into {g} groups by their dependencies.\n"
                      "Double-click a row to rename its group.",
        "group_none": "No dependent (untagged) mods to group.",
        "cfg_pick_title": "Choose the server config (.json) folder",
        "cfg_saved_title": "Saved",
        "cfg_saved": "Config folder saved. Mods will be matched once the scan finishes.",
        "cfg_over_title": "Existing tags",
        "cfg_over_msg": "Should server names from the configs OVERWRITE the tags you set by hand?\n"
                        "No = only untagged mods are filled in.",
        "cfg_done_title": "Matched",
        "cfg_done": "{n} mods tagged across {s} servers.\nFrom now on this folder is read on every "
                    "start and only UNTAGGED mods are filled in.",
        "cfg_none": "No new matching mods in this folder's configs.\n"
                    "(It should contain Reforger server config.json files.)",
        "tm_title": "Size Map — area ∝ disk usage",
        "tm_info": "Colour = server • Bigger box = more disk space • Click = details",
        "tm_click": "{name}  •  {mb} MB  •  Server: {server}  •  {dep}",
        "tm_dep_yes": "other mods depend on it", "tm_dep_no": "no dependents",
        "wipe_title": "Wipe Local Data",
        "wipe_msg": "These files will be deleted from disk:\n\n  • {tags}\n  • {settings}\n\n"
                    "This permanently removes all your mod→server tags and the background/config "
                    "folder you chose. Mod files are not touched.\n\nContinue?",
        "wipe_done": "{n} files deleted. Tags were reset.",
    },
}


def T(key, **kw):
    """Geçerli dildeki metin. Eksik anahtar İngilizceye düşer."""
    s = STRINGS.get(LANG, STRINGS["en"]).get(key) or STRINGS["en"][key]
    return s.format(**kw) if kw else s


def detect_language():
    """Windows arayüz dili Türkçe ise 'tr', değilse 'en'."""
    try:
        if os.name == "nt":
            lang_id = ctypes.windll.kernel32.GetUserDefaultUILanguage()
            return "tr" if (lang_id & 0x3FF) == 0x1F else "en"
        return "tr" if os.environ.get("LANG", "").lower().startswith("tr") else "en"
    except (OSError, AttributeError):
        return "en"


_i18n = []   # dil değişince yeniden çağrılan güncelleyiciler


def tr_text(widget, key):
    """Widget metnini çeviri anahtarına bağlar; dil değişince otomatik güncellenir."""
    def apply():
        widget.config(text=T(key))
    apply()
    _i18n.append(apply)
    return widget


def set_language(lang):
    global LANG
    old_orphan = T("untagged")
    cur = server_filter_var.get()
    LANG = lang
    settings["lang"] = lang
    save_settings()
    for fn in _i18n:
        fn()
    root.title(T("win_title", v=APP_VERSION))
    update_headings()
    if cur == old_orphan:
        server_filter_var.set(T("untagged"))
    rebuild_server_filter()      # eski "(Hepsi)" listede yoksa yeni dildekine döner
    populate()
    status_var.set("")


def toggle_language():
    set_language("en" if LANG == "tr" else "tr")


def version_key(v):
    """'1.10.2' > '1.9' olacak şekilde sayısal sıralama anahtarı."""
    if not v:
        return []          # sürümsüz mod en başa
    parts = []
    for p in str(v).replace("-", ".").split("."):
        parts.append((0, int(p)) if p.isdigit() else (1, p.lower()))
    return parts


SORT_KEYS = {
    "name": lambda m: m["name"].lower(),
    "version": lambda m: version_key(m["version"]),
    "size": lambda m: m["size"],
    "date": lambda m: m["mtime"],
    "server": lambda m: tags.get(m["id"], "").lower(),
}


def resource_path(rel):
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, rel)


# ==================== VERİ / YARDIMCILAR (GUI'den bağımsız) ====================
def default_addons_dir():
    for c in [
        os.path.join(HOME, "Documents", "My Games", "ArmaReforger", "addons"),
        os.path.join(HOME, "OneDrive", "Documents", "My Games", "ArmaReforger", "addons"),
        os.path.join(HOME, "OneDrive", "Belgeler", "My Games", "ArmaReforger", "addons"),
        os.path.join(HOME, "Belgeler", "My Games", "ArmaReforger", "addons"),
    ]:
        if os.path.isdir(c):
            return c
    return os.getcwd()


def folder_size(folder):
    size = 0
    for dirpath, _d, filenames in os.walk(folder):
        for f in filenames:
            try:
                size += os.path.getsize(os.path.join(dirpath, f))
            except OSError:
                pass
    return size


def read_mod_meta(folder):
    """ServerData.json -> (id, name, version, deps). Reforger formatı:
    {"id": "...", "name": "...", "revision": {"version": "...", "dependencies": [...]}}"""
    folder_name = os.path.basename(folder)
    mid, name, version, deps = folder_name, folder_name, "", []
    sd = os.path.join(folder, "ServerData.json")
    if not os.path.isfile(sd):
        # büyük/küçük harf farkı için tek tarama
        try:
            for fn in os.listdir(folder):
                if fn.lower() == "serverdata.json":
                    sd = os.path.join(folder, fn)
                    break
        except OSError as e:
            log.warning("Cannot read folder %s: %s", folder, e)
            return mid, name, version, deps
    try:
        with open(sd, encoding="utf-8-sig") as f:
            data = json.load(f)
        if isinstance(data, dict):
            mid = str(data.get("id") or folder_name)
            name = data.get("name") or name
            rev = data.get("revision", {})
            if isinstance(rev, dict):
                version = rev.get("version", "") or ""
                deps = rev.get("dependencies", []) or []
    except (OSError, ValueError) as e:
        log.warning("Cannot read ServerData.json in %s: %s", folder, e)
    return mid, name, version, deps


def dep_id_name(dep):
    if isinstance(dep, dict):
        did = dep.get("modId") or dep.get("id") or dep.get("guid") or ""
        dname = dep.get("name") or dep.get("modName") or ""
        return str(did), str(dname)
    return str(dep), ""


def scan_mods(folder, progress=None):
    mods = []
    try:
        entries = [e for e in os.listdir(folder) if os.path.isdir(os.path.join(folder, e))]
    except OSError as e:
        log.error("Cannot read addons folder %s: %s", folder, e)
        return mods
    total = len(entries)
    seen_ids = set()
    for idx, e in enumerate(entries, 1):
        path = os.path.join(folder, e)
        mid, name, version, deps = read_mod_meta(path)
        if mid in seen_ids:          # aynı id iki klasörde: klasör adıyla ayır
            mid = e
        seen_ids.add(mid)
        try:
            mtime = os.path.getmtime(path)
        except OSError:
            mtime = 0
        mods.append({"id": mid, "folder": e, "name": name, "version": version, "deps": deps,
                     "size": folder_size(path), "mtime": mtime, "path": path})
        if progress:
            progress(idx, total)
    log.info("%d mods scanned: %s", len(mods), folder)
    return mods


def _name_index(mods):
    """Küçük harf isim -> mod. Aynı isimli birden fazla mod varsa o isim indekse girmez (çakışma)."""
    counts = {}
    for m in mods:
        counts[m["name"].lower()] = counts.get(m["name"].lower(), 0) + 1
    return {m["name"].lower(): m for m in mods if counts[m["name"].lower()] == 1}


def _resolve_dep(d, by_id, by_name):
    did, dname = dep_id_name(d)
    if did and did in by_id:
        return by_id[did]
    if dname and dname.lower() in by_name:
        return by_name[dname.lower()]
    return None


def build_dependents(mods):
    by_id = {m["id"]: m for m in mods}
    by_name = _name_index(mods)
    dependents = {m["id"]: set() for m in mods}
    for m in mods:
        for d in m["deps"]:
            target = _resolve_dep(d, by_id, by_name)
            if target and target["id"] != m["id"]:
                dependents[target["id"]].add(m["id"])
    return dependents


def extract_tokens(text):
    text = text.strip()
    tokens = []
    if text.startswith("{") or text.startswith("["):
        try:
            data = json.loads(text)

            def walk(o):
                if isinstance(o, dict):
                    for k, v in o.items():
                        if k.lower() in ("modid", "id", "guid", "name", "modname") and isinstance(v, str):
                            tokens.append(v)
                        else:
                            walk(v)
                elif isinstance(o, list):
                    for it in o:
                        walk(it)
            walk(data)
            if tokens:
                return tokens
        except ValueError:
            pass
    for line in text.replace(",", "\n").splitlines():
        t = line.strip().strip('"').strip("'")
        if t:
            tokens.append(t)
    return tokens


def match_mods_by_tokens(mods, tokens):
    """Yalnızca TAM eşleşme: token == mod id  veya  token == mod adı (büyük/küçük harf duyarsız).
    Alt-dize eşleşmesi bilerek yok: 'ACE' tokeni 'Peace Keeper'ı etiketlememeli."""
    low = {t.strip().lower() for t in tokens if t.strip()}
    matched = set()
    for m in mods:
        if m["id"].lower() in low or m["name"].lower() in low:
            matched.add(m["id"])
    return matched


def load_json(path, default):
    try:
        with open(path, encoding="utf-8-sig") as f:
            d = json.load(f)
            return d if isinstance(d, type(default)) else default
    except FileNotFoundError:
        return default
    except (OSError, ValueError) as e:
        log.warning("Cannot read JSON %s: %s", path, e)
        return default


def save_json(path, data):
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except OSError as e:
        log.error("Cannot write JSON %s: %s", path, e)
        return False


def save_tags():
    if not save_json(TAG_FILE, tags):
        messagebox.showwarning(T("t_warn"), T("tags_save_fail", path=TAG_FILE))


def save_settings():
    """SADECE kullanıcının açıkça seçtiği yollar ve dil kaydedilir. Son klasör, sıralama,
    filtre, pencere konumu KAYDEDİLMEZ — her açılış sıfırdan başlar."""
    save_json(SETTINGS_FILE, {
        "bg_path": settings.get("bg_path", ""),
        "server_config_dir": settings.get("server_config_dir", ""),
        "lang": settings.get("lang", ""),
    })


def open_in_explorer(path):
    try:
        if os.name == "nt":
            os.startfile(path)  # type: ignore[attr-defined]
        elif sys.platform == "darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])
    except OSError as e:
        messagebox.showwarning(T("t_warn"), T("folder_open_fail", err=e))


def game_running():
    """Windows'ta Reforger süreci çalışıyor mu (tasklist). Bilinemiyorsa False."""
    if os.name != "nt":
        return False
    try:
        exe = os.path.join(os.environ.get("SystemRoot", r"C:\Windows"), "System32", "tasklist.exe")
        out = subprocess.run([exe, "/NH"], capture_output=True, text=True,
                             stdin=subprocess.DEVNULL, creationflags=0x08000000,
                             timeout=5).stdout.lower()
        return any(exe.lower() in out for exe in GAME_EXES)
    except (OSError, subprocess.SubprocessError) as e:
        log.warning("tasklist failed: %s", e)
        return False


def safe_get_min_size():
    v = size_var.get().strip()
    if not v:
        return None
    try:
        return max(int(v), 0)
    except ValueError:
        return None


def filtered_sorted():
    text = search_var.get().lower().strip()
    min_size = safe_get_min_size()
    server = server_filter_var.get()
    out = []
    for m in all_mods:
        if text and text not in m["name"].lower() and text not in m["id"].lower():
            continue
        if min_size and m["size"] < min_size * 1024 * 1024:
            continue
        tag = tags.get(m["id"], "")
        if server == T("untagged") and tag:
            continue
        if server not in (T("all"), T("untagged")) and tag != server:
            continue
        out.append(m)
    out.sort(key=SORT_KEYS[sort_col], reverse=sort_reverse)
    return out


def is_required(mid):
    return bool(dependents.get(mid))


def untagged_independent(m):
    """Etiketsiz VE başka mod bağımlı değil. 'Güvenli' demek değil; kullanıcı henüz işaretlememiş demek."""
    return not tags.get(m["id"]) and not is_required(m["id"])


def parse_server_config(path):
    """Reforger sunucu config.json -> (sunucu_adı, [modId...]).
    Beklenen: {"game": {"name": "...", "mods": [{"modId": "...", "name": "...", "version": "..."}]}}"""
    try:
        with open(path, encoding="utf-8-sig") as f:
            data = json.load(f)
    except (OSError, ValueError) as e:
        log.warning("Cannot read server config %s: %s", path, e)
        return None, []
    name, mods = "", []
    game = data.get("game", data) if isinstance(data, dict) else {}
    if isinstance(game, dict):
        name = game.get("name") or game.get("serverName") or ""
        ml = game.get("mods")
        if isinstance(ml, list):
            mods = ml
    if not mods and isinstance(data, dict) and isinstance(data.get("mods"), list):
        mods = data["mods"]
    ids = []
    for m in mods:
        if isinstance(m, dict):
            mid = m.get("modId") or m.get("id") or m.get("guid")
            if mid:
                ids.append(str(mid))
        elif isinstance(m, str):
            ids.append(m)
    if not name:
        name = os.path.splitext(os.path.basename(path))[0]
    return name, ids


def import_server_configs(folder, mods, tagmap, overwrite=False):
    """Klasördeki .json sunucu config'lerini okuyup eşleşen modları etiketler.
    overwrite=False: mevcut (elle verilmiş) etiketlere DOKUNMAZ, sadece etiketsizleri doldurur.
    Döndürür: {sunucu_adı: yeni_etiketlenen_mod_sayısı}."""
    result = {}
    try:
        files = [f for f in os.listdir(folder) if f.lower().endswith(".json")]
    except OSError as e:
        log.warning("Cannot read config folder %s: %s", folder, e)
        return result
    for fn in files:
        sname, ids = parse_server_config(os.path.join(folder, fn))
        if not ids:
            continue
        n = 0
        for mid in match_mods_by_tokens(mods, ids):
            if overwrite or not tagmap.get(mid):
                tagmap[mid] = sname
                n += 1
        if n:
            result[sname] = n
    return result


def dependency_clusters(mods):
    """Bağımlılıkla birbirine bağlı modları kümelere (bağlı bileşenler) ayırır."""
    by_id = {m["id"]: m for m in mods}
    by_name = _name_index(mods)
    adj = {m["id"]: set() for m in mods}
    for m in mods:
        for d in m["deps"]:
            t = _resolve_dep(d, by_id, by_name)
            if t and t["id"] != m["id"]:
                adj[m["id"]].add(t["id"])
                adj[t["id"]].add(m["id"])
    seen, clusters = set(), []
    for mid in adj:
        if mid in seen:
            continue
        stack, comp = [mid], []
        while stack:
            cur = stack.pop()
            if cur in seen:
                continue
            seen.add(cur)
            comp.append(cur)
            stack.extend(adj[cur] - seen)
        clusters.append(comp)
    return clusters


def server_color(name):
    """Sunucu adı -> sabit renk. hashlib: her açılışta aynı renk (Python hash() rastgele tohumlu)."""
    if not name:
        return "#5a3030"
    h = hashlib.md5(name.encode("utf-8"), usedforsecurity=False).digest()
    hue = (h[0] * 256 + h[1]) / 65536.0
    r, g, b = colorsys.hls_to_rgb(hue, 0.42, 0.55)
    return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"


# ==================== GÖRSEL PIPELINE ====================
def _cover_fit(img, w, h):
    sw, sh = img.size
    scale = max(w / sw, h / sh)
    rs = img.resize((max(1, int(sw * scale)), max(1, int(sh * scale))), Image.LANCZOS)
    left = (rs.width - w) // 2
    top = (rs.height - h) // 2
    return rs.crop((left, top, left + w, top + h))


def load_base_image():
    """Kullanıcının seçtiği (yoksa gömülü) arka planı pencere boyutunda döndürür."""
    candidates = []
    bp = settings.get("bg_path", "")
    if bp and os.path.isfile(bp):
        candidates.append(bp)
    candidates.append(resource_path(os.path.join("assets", "background.png")))
    for c in candidates:
        try:
            return _cover_fit(Image.open(c).convert("RGB"), WIN_W, WIN_H)
        except (OSError, ValueError) as e:
            log.warning("Cannot open background %s: %s", c, e)
    return None


def _glass(base, region, bright=0.55, blur=3, tint_a=0.42):
    x, y, w, h = region
    crop = base.crop((x, y, x + w, y + h))
    crop = ImageEnhance.Brightness(crop).enhance(bright).filter(ImageFilter.GaussianBlur(blur))
    ov = Image.new("RGB", crop.size, GLASS_TINT)
    return Image.blend(crop, ov, tint_a)


IMG = {}  # PhotoImage referansları (GC koruması)


def rebuild_visuals():
    """Arka plan + cam panelleri (yeniden) üretir ve widget'lara basar."""
    if not HAVE_PIL:
        backdrop_label.config(image="", bg=BG_COLOR)
        return
    base = load_base_image()
    if base is None:
        backdrop_label.config(image="", bg=BG_COLOR)
        return
    bd = ImageEnhance.Brightness(base).enhance(0.62)
    bd = Image.blend(bd, Image.new("RGB", bd.size, (6, 14, 20)), 0.15)
    IMG["backdrop"] = ImageTk.PhotoImage(bd)
    backdrop_label.config(image=IMG["backdrop"])

    hdr = _glass(base, R_HEADER, bright=0.78, blur=1, tint_a=0.10)
    IMG["header"] = ImageTk.PhotoImage(hdr)
    header_canvas.itemconfig(header_bg_item, image=IMG["header"])

    for key, region, label in (("toolbar", R_TOOLBAR, toolbar_bg),
                               ("right", R_RIGHT, right_bg),
                               ("table", R_TABLE, table_bg)):
        IMG[key] = ImageTk.PhotoImage(_glass(base, region))
        label.config(image=IMG[key])


def choose_background():
    if not HAVE_PIL:
        messagebox.showinfo(T("t_info"), T("need_pillow"))
        return
    p = filedialog.askopenfilename(
        title=T("bg_pick_title"),
        filetypes=[(T("ft_images"), "*.png *.jpg *.jpeg *.webp *.bmp *.gif"), (T("ft_all"), "*.*")])
    if not p:
        return
    settings["bg_path"] = p
    save_settings()
    rebuild_visuals()


def reset_background():
    settings["bg_path"] = ""
    save_settings()
    rebuild_visuals()


# ==================== TARAMA ====================
_scan_q = queue.Queue()
_scanning = False


def rescan():
    """Arka planda tarar. Worker thread Tk'ye hiç dokunmaz; sonuçları kuyruğa yazar,
    ana thread _poll_scan ile okur. Tarama sürerken yeni tarama başlatılmaz."""
    global alert_big, alert_old, _scanning
    if _scanning:
        return
    _scanning = True
    alert_big, alert_old = set(), set()   # eski klasörün işaretleri kalmasın
    folder = selected_dir.get()
    status_var.set(T("scanning"))

    def worker():
        try:
            mods = scan_mods(folder, lambda i, n: _scan_q.put(("progress", i, n)))
            _scan_q.put(("done", folder, mods))
        except Exception as e:  # beklenmeyen hata: kuyruğa bildir ki arayüz takılı kalmasın
            log.exception("Scan failed")
            _scan_q.put(("error", folder, e))

    threading.Thread(target=worker, daemon=True).start()
    root.after(100, _poll_scan)


def _poll_scan():
    global all_mods, dependents, _scanning
    last_progress = None
    try:
        while True:
            msg = _scan_q.get_nowait()
            if msg[0] == "progress":
                last_progress = msg
                continue
            _scanning = False
            if msg[0] == "error":
                status_var.set(T("scan_err_status"))
                messagebox.showerror(T("t_err"), T("scan_err_msg", err=msg[2], log=LOG_FILE))
                return
            _, folder, mods = msg
            all_mods = mods
            dependents = build_dependents(mods)
            text = T("status_mods", n=len(mods), folder=os.path.basename(folder) or folder)
            cfg = settings.get("server_config_dir", "")
            if cfg and os.path.isdir(cfg):
                res = import_server_configs(cfg, all_mods, tags)   # elle etiketleri ezmez
                if res:
                    save_tags()
                    text = T("status_mapped", n=len(mods), m=sum(res.values()), s=len(res))
            rebuild_server_filter()
            populate()
            status_var.set(text)
            return
    except queue.Empty:
        pass
    if last_progress:
        status_var.set(T("scanning_n", i=last_progress[1], n=last_progress[2]))
    root.after(100, _poll_scan)


def update_headings():
    for key, title, *_ in COLUMNS:
        arrow = ("  ▼" if sort_reverse else "  ▲") if key == sort_col else ""
        tree.heading(key, text=T(title) + arrow)


def on_sort(col):
    global sort_col, sort_reverse
    if sort_col == col:
        sort_reverse = not sort_reverse
    else:
        sort_col = col
        sort_reverse = col in ("size", "date")
    update_headings()
    populate()


def populate():
    keep = set(tree.selection())
    tree.delete(*tree.get_children())
    for i, m in enumerate(filtered_sorted()):
        tag = tags.get(m["id"], "")
        size_mb = m["size"] // (1024 * 1024)
        date = datetime.fromtimestamp(m["mtime"]).strftime("%d.%m.%Y %H:%M") if m["mtime"] else "-"
        rtags = ["even" if i % 2 else "odd"]
        if m["id"] in alert_big or m["id"] in alert_old:
            rtags.append("alert")
        if is_required(m["id"]):
            rtags.append("required")
        elif not tag:
            rtags.append("orphan")
        req = " ⛓" if is_required(m["id"]) else ""
        tree.insert("", "end", iid=m["id"],
                    values=(m["name"] + req, m["version"] or "-", f"{size_mb} MB", date, tag or "—"),
                    tags=rtags)
    for iid in keep:
        if tree.exists(iid):
            tree.selection_add(iid)
    update_gauge()
    update_stats()


def mod_by_id(iid):
    for m in all_mods:
        if m["id"] == iid:
            return m
    return None


def selected_mods():
    ids = set(tree.selection())
    return [m for m in all_mods if m["id"] in ids]


# ==================== OLAYLAR ====================
def on_select_folder():
    p = filedialog.askdirectory(initialdir=selected_dir.get())
    if p:
        selected_dir.set(p)
        rescan()


def on_clear_filters():
    search_var.set("")
    size_var.set("")
    server_filter_var.set(T("all"))
    populate()


def on_analyze():
    global alert_big, alert_old
    if not all_mods:
        return
    by_size = sorted(all_mods, key=lambda m: -m["size"])
    by_time = sorted(all_mods, key=lambda m: m["mtime"])
    alert_big = {m["id"] for m in by_size[:2] if m["size"] > 0}
    alert_old = {m["id"] for m in by_time[:2]}
    populate()
    status_var.set(T("analyze_done"))
    root.after(3000, lambda: status_var.set(""))


def edit_tag(mod):
    if not mod:
        return
    cur = tags.get(mod["id"], "")
    val = simpledialog.askstring(
        T("tag_title"), T("tag_prompt", name=mod["name"], id=mod["id"]),
        initialvalue=cur, parent=root)
    if val is None:
        return
    val = val.strip()
    if val:
        tags[mod["id"]] = val
    else:
        tags.pop(mod["id"], None)
    save_tags()
    rebuild_server_filter()
    populate()


def tag_selected():
    sel = selected_mods()
    if not sel:
        messagebox.showinfo(T("t_info"), T("select_first"))
        return
    val = simpledialog.askstring(T("bulk_title"), T("bulk_prompt", n=len(sel)), parent=root)
    if val is None:
        return
    val = val.strip()
    for m in sel:
        if val:
            tags[m["id"]] = val
        else:
            tags.pop(m["id"], None)
    save_tags()
    rebuild_server_filter()
    populate()


def open_selected():
    sel = selected_mods()
    if sel:
        open_in_explorer(sel[0]["path"])


def _confirm_delete(mods):
    """Silmeden önceki tüm onaylar. Hepsi geçilirse True."""
    if game_running() and not messagebox.askyesno(
            T("game_title"), T("game_msg")):
        return False
    del_ids = {m["id"] for m in mods}
    warnings = []
    for m in mods:
        needers = dependents.get(m["id"], set()) - del_ids
        if needers:
            names = ", ".join(mod_by_id(x)["name"] for x in list(needers)[:5] if mod_by_id(x))
            warnings.append(T("dep_line", name=m["name"], names=names))
    if warnings and not messagebox.askyesno(
            T("dep_title"), T("dep_msg", lines="\n".join(warnings[:10]))):
        return False
    total_mb = sum(m["size"] for m in mods) // 1024 // 1024
    names = "\n".join(m["name"] for m in mods[:15]) + ("\n…" if len(mods) > 15 else "")
    return messagebox.askyesno(T("del_title"), T("del_msg", n=len(mods), mb=total_mb, names=names))


def on_delete(mods):
    global silinen_count, dependents
    if not mods:
        return
    if send2trash is None:
        messagebox.showerror(T("t_err"), T("no_s2t"))
        return
    if not _confirm_delete(mods):
        return
    status_var.set(T("deleting"))
    root.update_idletasks()
    done, freed, failed = 0, 0, []
    for m in mods:
        if os.path.exists(m["path"]):
            try:
                send2trash(m["path"])   # uzun yol prefix'ini send2trash kendisi yönetir
            except Exception as e:  # tek modun hatası döngüyü kesmesin, kalanlar silinsin
                log.exception("Delete failed: %s", m["path"])
                failed.append(f"• {m['name']}: {e}")
                continue
            done += 1
            freed += m["size"]
            log.info("Deleted: %s (%s)", m["name"], m["path"])
        if m in all_mods:          # silindi ya da zaten yoktu: listeden çıkar
            all_mods.remove(m)
    dependents = build_dependents(all_mods)   # silinenler artık kimseyi 'gerekli' yapmasın
    silinen_count += done                     # yalnızca bu oturum; diske yazılmaz
    populate()
    status_var.set(T("deleted_status", n=done, mb=freed // 1024 // 1024))
    root.after(2500, lambda: status_var.set(""))
    if failed:
        lines = "\n".join(failed[:10]) + ("\n…" if len(failed) > 10 else "")
        messagebox.showwarning(T("t_warn"), T("del_failed", n=len(failed), lines=lines, log=LOG_FILE))


def delete_selected():
    on_delete(selected_mods())


def rebuild_server_filter():
    vals = [T("all"), T("untagged"), *sorted(set(tags.values()))]
    server_cb["values"] = vals
    if server_filter_var.get() not in vals:
        server_filter_var.set(T("all"))


def update_gauge():
    size = sum(m["size"] for m in selected_mods())
    gauge_canvas.delete("all")
    r = 28
    gauge_canvas.create_oval(8, 8, 8 + r * 2, 8 + r * 2, outline=BTN_COLOR, width=6)
    pct = min(size / (10 * 1024 ** 3), 1) if size else 0
    if pct > 0:
        gauge_canvas.create_arc(8, 8, 8 + r * 2, 8 + r * 2, start=90, extent=-360 * pct,
                                style="arc", outline=HEADER_COLOR, width=6)
    gauge_canvas.create_text(8 + r, 8 + r, fill=FG_COLOR, font=("Consolas", 10, "bold"),
                             text=f"{size//1024//1024}\nMB", anchor="center")
    gauge_label.config(text=T("gauge", mb=size // 1024 // 1024, pct=int(pct * 100)))


def update_stats():
    orphans = sum(1 for m in all_mods if not tags.get(m["id"]))
    free = sum(1 for m in all_mods if untagged_independent(m))
    shown = len(tree.get_children())
    stats_label.config(text=T("stats", shown=shown, total=len(all_mods), orphans=orphans,
                              free=free, deleted=silinen_count))
    by = {}
    for m in all_mods:
        t = tags.get(m["id"]) or T("untagged")
        s = by.get(t, [0, 0])
        s[0] += 1
        s[1] += m["size"]
        by[t] = s
    lines = [f"{t}: {c} • {sz//1024//1024} MB" for t, (c, sz) in sorted(by.items(), key=lambda kv: -kv[1][1])]
    summary_label.config(text="\n".join(lines[:5]) if lines else T("no_data"))


def open_auto_tag():
    if not all_mods:
        messagebox.showinfo(T("t_info"), T("scan_first"))
        return
    win = tk.Toplevel(root)
    win.title(T("at_title"))
    win.configure(bg=PANEL_BG)
    win.geometry("520x460")
    win.transient(root)
    tk.Label(win, text=T("at_server"), bg=PANEL_BG, fg=FG_COLOR, font=FONT_LABEL).pack(anchor="w", padx=16, pady=(14, 2))
    sv = tk.StringVar()
    tk.Entry(win, textvariable=sv, font=FONT_LABEL, bg=BTN_COLOR, fg=FG_COLOR,
             bd=0, insertbackground=HEADER_COLOR).pack(fill="x", padx=16, ipady=4)
    tk.Label(win, text=T("at_hint"),
             bg=PANEL_BG, fg=DIM, font=FONT_SUB, justify="left").pack(anchor="w", padx=16, pady=(12, 2))
    txt = tk.Text(win, height=14, bg=ROW_ODD, fg=FG_COLOR, bd=0, insertbackground=HEADER_COLOR,
                  font=FONT_DATA)
    txt.pack(fill="both", expand=True, padx=16, pady=4)

    def apply_tags():
        server = sv.get().strip()
        if not server:
            messagebox.showinfo(T("t_info"), T("at_need_server"), parent=win)
            return
        tokens = extract_tokens(txt.get("1.0", "end"))
        matched = match_mods_by_tokens(all_mods, tokens) if tokens else set()
        if not matched:
            messagebox.showinfo(T("t_result"), T("at_none"), parent=win)
            return
        for mid in matched:
            tags[mid] = server
        save_tags()
        rebuild_server_filter()
        populate()
        messagebox.showinfo(T("t_done"), T("at_done", n=len(matched), server=server), parent=win)
        win.destroy()

    tk.Button(win, text=T("at_apply"), command=apply_tags, font=FONT_BTN,
              bg=BTN_COLOR, fg=HEADER_COLOR, activebackground=BTN_HOVER, activeforeground=BG_COLOR,
              bd=0, cursor="hand2").pack(fill="x", padx=16, pady=12, ipady=5)


def select_untagged():
    """Görünenler arasında etiketsiz + bağımlı olmayan modları seçer. Silmez."""
    if not tags:
        messagebox.showinfo(T("t_info"), T("su_hint"))
    tree.selection_remove(*tree.selection())
    ids = [m["id"] for m in filtered_sorted() if untagged_independent(m)]
    for iid in ids:
        if tree.exists(iid):
            tree.selection_add(iid)
    if ids:
        tree.see(ids[0])
        status_var.set(T("su_status", n=len(ids)))
    else:
        status_var.set(T("su_none"))
    update_gauge()


def auto_group_dependencies():
    """Etiketsiz modları bağımlılık kümelerine göre otomatik gruplar."""
    if not all_mods:
        return
    clusters = [c for c in dependency_clusters(all_mods) if len(c) > 1]
    n = 0
    for i, comp in enumerate(sorted(clusters, key=lambda c: -len(c)), 1):
        existing = next((tags[mid] for mid in comp if tags.get(mid)), None)
        gname = existing or T("group_name", i=i)
        for mid in comp:
            if not tags.get(mid):
                tags[mid] = gname
                n += 1
    if n:
        save_tags()
        rebuild_server_filter()
        populate()
        messagebox.showinfo(T("t_done"), T("group_done", n=n, g=len(clusters)))
    else:
        messagebox.showinfo(T("t_info"), T("group_none"))


def choose_server_config_dir():
    """Sunucu config.json klasörünü seçer; açılışta otomatik eşleme için kaydeder."""
    p = filedialog.askdirectory(title=T("cfg_pick_title"))
    if not p:
        return
    settings["server_config_dir"] = p
    save_settings()
    if not all_mods:
        messagebox.showinfo(T("cfg_saved_title"), T("cfg_saved"))
        return
    overwrite = False
    if tags:
        overwrite = messagebox.askyesno(T("cfg_over_title"), T("cfg_over_msg"))
    res = import_server_configs(p, all_mods, tags, overwrite=overwrite)
    if res:
        save_tags()
        rebuild_server_filter()
        populate()
        total = sum(res.values())
        messagebox.showinfo(T("cfg_done_title"), T("cfg_done", n=total, s=len(res)))
    else:
        messagebox.showinfo(T("t_result"), T("cfg_none"))


def squarify(items, x, y, w, h):
    rects = []
    items = [it for it in items if it[0] > 0]
    total = sum(it[0] for it in items)
    if total <= 0:
        return rects
    scaled = [(it[0] / total * (w * h), it[1], it[2]) for it in items]

    def worst(row, length):
        s = sum(r[0] for r in row)
        if s == 0 or length == 0:
            return float("inf")
        mx = max(r[0] for r in row)
        mn = min(r[0] for r in row)
        return max((length ** 2 * mx) / (s ** 2), (s ** 2) / (length ** 2 * mn))

    def layout_row(row, x, y, w, h, horizontal):
        s = sum(r[0] for r in row)
        out = []
        if horizontal:
            rw = s / h if h else 0
            cy = y
            for r in row:
                rh = (r[0] / s * h) if s else 0
                out.append((x, cy, rw, rh, r[1], r[2]))
                cy += rh
            return out, x + rw, y, w - rw, h
        else:
            rh = s / w if w else 0
            cx = x
            for r in row:
                rw = (r[0] / s * w) if s else 0
                out.append((cx, y, rw, rh, r[1], r[2]))
                cx += rw
            return out, x, y + rh, w, h - rh

    def recurse(items, x, y, w, h):
        if not items:
            return
        horizontal = w >= h
        length = h if horizontal else w
        row = []
        while items:
            if row and worst(row, length) < worst(row + [items[0]], length):
                break
            row.append(items.pop(0))
            if not items:
                break
        placed, nx, ny, nw, nh = layout_row(row, x, y, w, h, horizontal)
        rects.extend(placed)
        recurse(items, nx, ny, nw, nh)

    recurse(list(scaled), x, y, w, h)
    return rects


def open_treemap():
    if not all_mods:
        messagebox.showinfo(T("t_info"), T("scan_first"))
        return
    win = tk.Toplevel(root)
    win.title(T("tm_title"))
    win.configure(bg=PANEL_BG)
    W, H = 900, 600
    win.geometry(f"{W}x{H+40}")
    win.transient(root)
    info = tk.Label(win, text=T("tm_info"),
                    bg=PANEL_BG, fg=DIM, font=("Consolas", 9))
    info.pack(anchor="w", padx=10, pady=(8, 0))
    cv = tk.Canvas(win, bg=PANEL_BG, highlightthickness=0, width=W, height=H)
    cv.pack(fill="both", expand=True, padx=10, pady=8)
    items = sorted(all_mods, key=lambda m: -m["size"])
    rects = squarify([(m["size"], m, server_color(tags.get(m["id"], ""))) for m in items], 2, 2, W - 4, H - 4)
    for x, y, w, h, m, color in rects:
        if w < 1 or h < 1:
            continue
        rid = cv.create_rectangle(x, y, x + w, y + h, fill=color, outline=PANEL_BG, width=1)
        if w > 60 and h > 26:
            mb = m["size"] // 1024 // 1024
            cv.create_text(x + 4, y + 4, anchor="nw", fill="#ffffff", font=("Consolas", 9, "bold"),
                           text=f"{m['name'][:int(w/8)]}\n{mb} MB")

        def show(_e, mm=m):
            t = tags.get(mm["id"], "—")
            info.config(text=T("tm_click", name=mm["name"], mb=mm["size"] // 1024 // 1024, server=t,
                               dep=T("tm_dep_yes") if is_required(mm["id"]) else T("tm_dep_no")))
        cv.tag_bind(rid, "<Button-1>", show)


def animate_radar(angle=0):
    global _radar_job
    try:
        if root.state() == "iconic":
            _radar_job = root.after(1000, lambda: animate_radar(angle))
            return
    except tk.TclError:
        return  # pencere kapanmış
    cx = R_HEADER[2] - 38
    cy = R_HEADER[3] // 2
    r = 22
    header_canvas.delete("radar")
    header_canvas.create_oval(cx - r, cy - r, cx + r, cy + r,
                              outline=HEADER_COLOR, width=2, tags="radar")
    for rr in (10, 16):
        header_canvas.create_oval(cx - rr, cy - rr, cx + rr, cy + rr,
                                  outline=HEADER_COLOR, width=1, dash=(2, 4), tags="radar")
    header_canvas.create_line(cx - r + 2, cy, cx + r - 2, cy, fill=HEADER_COLOR, width=1, dash=(1, 3), tags="radar")
    header_canvas.create_line(cx, cy - r + 2, cx, cy + r - 2, fill=HEADER_COLOR, width=1, dash=(1, 3), tags="radar")
    a = angle % 360
    for f in range(0, 56, 8):
        col = f"#{int(20+f):02x}{255-int(f*3.7):02x}{255-int(f*4.2):02x}"
        x = cx + (r - 2) * math.cos(math.radians(a - f))
        y = cy + (r - 2) * math.sin(math.radians(a - f))
        header_canvas.create_line(cx, cy, x, y, fill=col, width=2 if f == 0 else 1, tags="radar")
    if random.random() < 0.5:
        ea, er = random.uniform(0, 360), random.uniform(6, r - 4)
        ex = cx + er * math.cos(math.radians(ea))
        ey = cy + er * math.sin(math.radians(ea))
        header_canvas.create_oval(ex - 2, ey - 2, ex + 2, ey + 2,
                                  fill="#ff3838", outline="#ff3838", tags="radar")
    header_canvas.create_oval(cx - 2, cy - 2, cx + 2, cy + 2,
                              outline=HEADER_COLOR, fill=HEADER_COLOR, tags="radar")
    _radar_job = root.after(400, lambda: animate_radar(a + 10))


_radar_job = None


def on_close():
    if _radar_job:
        root.after_cancel(_radar_job)
    root.destroy()


def wipe_local_data():
    """Yerel olarak saklanan TÜM dosyaları siler (etiketler dahil). Geri alınamaz."""
    if not messagebox.askyesno(
            T("wipe_title"), T("wipe_msg", tags=TAG_FILE, settings=SETTINGS_FILE)):
        return
    removed = []
    for p in (TAG_FILE, SETTINGS_FILE, _OLD_TAG_FILE, _OLD_SETTINGS_FILE):
        try:
            if os.path.isfile(p):
                os.remove(p)
                removed.append(p)
        except OSError as e:
            log.error("Cannot remove %s: %s", p, e)
    tags.clear()
    settings.clear()
    rebuild_server_filter()
    rebuild_visuals()
    populate()
    messagebox.showinfo(T("t_done"), T("wipe_done", n=len(removed)))


def corner_ticks(canvas, w, h, c=HEADER_COLOR, n=14):
    """HUD köşe çentikleri."""
    for (cx, cy, dx, dy) in [(2, 2, 1, 1), (w - 2, 2, -1, 1), (2, h - 2, 1, -1), (w - 2, h - 2, -1, -1)]:
        canvas.create_line(cx, cy, cx + dx * n, cy, fill=c, width=2)
        canvas.create_line(cx, cy, cx, cy + dy * n, fill=c, width=2)


def compute_layout():
    """Pencere boyutunu ekrana göre seçer (1366x768'de taşmasın) ve panel bölgelerini hesaplar."""
    global WIN_W, WIN_H, R_HEADER, R_TOOLBAR, R_RIGHT, R_TABLE
    sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
    WIN_W = max(960, min(1180, sw - 24))
    WIN_H = max(600, min(740, sh - 110))     # başlık çubuğu + görev çubuğu payı
    R_HEADER = (M, M, WIN_W - 2 * M, 64)
    R_TOOLBAR = (M, 88, WIN_W - 2 * M, 92)
    cy = 188
    R_RIGHT = (WIN_W - M - 300, cy, 300, WIN_H - cy - M)
    R_TABLE = (M, cy, R_RIGHT[0] - M - 14, WIN_H - cy - M)


def pick_font(preferred, fallback):
    fams = set(tkfont.families())
    for f in preferred:
        if f in fams:
            return f
    return fallback


# ==================== GUI ====================
# Modül import edildiğinde (testler) GUI kurulmaz; yalnızca doğrudan çalıştırılınca kurulur.
if __name__ == "__main__":
    root = tk.Tk()
    compute_layout()
    root.geometry(f"{WIN_W}x{WIN_H}")
    root.configure(bg=BG_COLOR)
    root.resizable(False, False)
    try:
        root.iconbitmap(resource_path(os.path.join("assets", "icon.ico")))
    except tk.TclError:
        pass

    # Yazı tipleri: sistemde yoksa fallback (Bahnschrift yalnızca Win10+)
    _display_family = pick_font(["Bahnschrift SemiBold", "Bahnschrift", "Segoe UI Semibold", "Segoe UI"], "Arial")
    _ui_family = pick_font(["Segoe UI"], "Arial")
    _ui_bold_family = pick_font(["Segoe UI Semibold", "Segoe UI"], "Arial")
    _mono_family = pick_font(["Consolas", "Courier New"], "Courier")
    FONT_DISPLAY = (_display_family, 26, "bold")
    FONT_SECTION = (_display_family, 12, "bold")
    FONT_BTN = (_ui_bold_family, 10)
    FONT_LABEL = (_ui_family, 10)
    FONT_LABEL_BOLD = (_ui_bold_family, 10)
    FONT_SUB = (_ui_family, 9)
    FONT_TINY = (_ui_family, 8)
    FONT_DATA = (_mono_family, 12)
    FONT_DATA_BOLD = (_mono_family, 11, "bold")

    # Durum / ayarlar
    tags = load_json(TAG_FILE, {}) or load_json(_OLD_TAG_FILE, {})
    settings = load_json(SETTINGS_FILE, {}) or load_json(_OLD_SETTINGS_FILE, {})
    all_mods = []
    dependents = {}
    alert_big, alert_old = set(), set()
    silinen_count = 0
    sort_col, sort_reverse = "size", True
    start_dir = default_addons_dir()
    LANG = settings.get("lang") if settings.get("lang") in STRINGS else detect_language()
    root.title(T("win_title", v=APP_VERSION))

    selected_dir = tk.StringVar(value=start_dir)
    search_var = tk.StringVar()
    size_var = tk.StringVar()
    server_filter_var = tk.StringVar(value=T("all"))
    status_var = tk.StringVar(value="")

    style = ttk.Style()
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass
    style.configure("Treeview", background=ROW_ODD, fieldbackground=ROW_ODD, foreground=FG_COLOR,
                    rowheight=32, font=FONT_DATA, borderwidth=0)
    style.configure("Treeview.Heading", background=BTN_COLOR, foreground=HEADER_COLOR,
                    font=FONT_LABEL_BOLD, relief="flat", padding=6)
    style.map("Treeview.Heading", background=[("active", BTN_HOVER)], foreground=[("active", BG_COLOR)])
    style.map("Treeview", background=[("selected", SELECT_BG)], foreground=[("selected", "#ffffff")])
    style.configure("TCombobox", fieldbackground=BTN_COLOR, background=BTN_COLOR, foreground=FG_COLOR,
                    arrowcolor=HEADER_COLOR, borderwidth=0)
    style.map("TCombobox", fieldbackground=[("readonly", BTN_COLOR)], foreground=[("readonly", FG_COLOR)])

    btn = dict(font=FONT_BTN, bg=BTN_COLOR, fg=HEADER_COLOR, activebackground=BTN_HOVER,
               activeforeground=BG_COLOR, bd=0, relief="flat", cursor="hand2")


    def entry(parent, var, w):
        return tk.Entry(parent, textvariable=var, width=w, font=FONT_LABEL, bg=BTN_COLOR,
                        fg=FG_COLOR, bd=0, relief="flat", insertbackground=HEADER_COLOR)


    backdrop_label = tk.Label(root, bg=BG_COLOR, bd=0)
    backdrop_label.place(x=0, y=0, width=WIN_W, height=WIN_H)


    def glass_panel(region):
        """Cam görselli + cyan kenarlıklı panel. (content_frame, image_label) döndürür."""
        x, y, w, h = region
        holder = tk.Frame(root, bg=HEADER_COLOR, highlightbackground=HEADER_COLOR, highlightthickness=1)
        holder.place(x=x, y=y, width=w, height=h)
        img_label = tk.Label(holder, bg=PANEL_BG, bd=0)
        img_label.place(x=0, y=0, relwidth=1, relheight=1)
        content = tk.Frame(img_label, bg=PANEL_BG)
        content.place(x=14, y=12, width=w - 30, height=h - 26)
        return content, img_label


    # ---- Başlık bandı ----
    header_holder = tk.Frame(root, bg=HEADER_COLOR, highlightbackground=HEADER_COLOR, highlightthickness=1)
    header_holder.place(x=R_HEADER[0], y=R_HEADER[1], width=R_HEADER[2], height=R_HEADER[3])
    header_canvas = tk.Canvas(header_holder, bg=PANEL_BG, highlightthickness=0)
    header_canvas.place(x=0, y=0, relwidth=1, relheight=1)
    header_bg_item = header_canvas.create_image(0, 0, anchor="nw")
    header_canvas.create_text(22, R_HEADER[3] // 2 - 8, anchor="w", fill="#04110f",
                              font=FONT_DISPLAY, text="REFORGER MOD CLEANER")
    header_canvas.create_text(20, R_HEADER[3] // 2 - 10, anchor="w", fill=HEADER_COLOR,
                              font=FONT_DISPLAY, text="REFORGER MOD CLEANER")
    header_sub = header_canvas.create_text(22, R_HEADER[3] // 2 + 18, anchor="w", fill=FG_COLOR,
                                           font=FONT_SUB, text=T("subtitle"))
    _i18n.append(lambda: header_canvas.itemconfig(header_sub, text=T("subtitle")))
    header_status = header_canvas.create_text(R_HEADER[2] - 72, R_HEADER[3] // 2, anchor="e",
                                              fill=HEADER_COLOR, font=FONT_DATA_BOLD, text="")
    corner_ticks(header_canvas, R_HEADER[2], R_HEADER[3])
    status_var.trace_add("write", lambda *a: header_canvas.itemconfig(header_status, text=status_var.get()))

    # ---- Araç çubuğu ----
    tb, toolbar_bg = glass_panel(R_TOOLBAR)
    row1 = tk.Frame(tb, bg=PANEL_BG)
    row1.pack(fill="x", pady=(6, 4))
    tr_text(tk.Button(row1, command=on_select_folder, **btn), "b_folder").pack(side="left", ipadx=6, ipady=3)
    tr_text(tk.Button(row1, command=rescan, **btn), "b_refresh").pack(side="left", padx=6, ipadx=6, ipady=3)
    tr_text(tk.Button(row1, command=on_analyze, **btn), "b_analyze").pack(side="left", ipadx=6, ipady=3)
    tr_text(tk.Button(row1, command=open_treemap, **btn), "b_treemap").pack(side="left", padx=6, ipadx=6, ipady=3)
    tr_text(tk.Button(row1, command=choose_background, **btn), "b_bg").pack(side="left", ipadx=6, ipady=3)
    tk.Button(row1, text="↺", command=reset_background, **btn).pack(side="left", padx=6, ipadx=4, ipady=3)
    # sağ taraf: dil seçimi + yerel veriyi sil
    tr_text(tk.Button(row1, command=toggle_language, **btn), "lang_btn").pack(side="right", ipadx=6, ipady=3)
    tr_text(tk.Button(row1, command=wipe_local_data, **btn), "b_wipe").pack(side="right", padx=6, ipadx=6, ipady=3)

    row2 = tk.Frame(tb, bg=PANEL_BG)
    row2.pack(fill="x", pady=(2, 0))
    tr_text(tk.Label(row2, bg=PANEL_BG, fg=FG_COLOR, font=FONT_LABEL), "l_search").pack(side="left")
    entry(row2, search_var, 22).pack(side="left", padx=(4, 12), ipady=3)
    tr_text(tk.Label(row2, bg=PANEL_BG, fg=FG_COLOR, font=FONT_LABEL), "l_minmb").pack(side="left")
    entry(row2, size_var, 6).pack(side="left", padx=(4, 12), ipady=3)
    tr_text(tk.Label(row2, bg=PANEL_BG, fg=FG_COLOR, font=FONT_LABEL), "l_server").pack(side="left")
    server_cb = ttk.Combobox(row2, textvariable=server_filter_var, values=[T("all"), T("untagged")],
                             width=16, state="readonly", font=FONT_LABEL)
    server_cb.pack(side="left", padx=(4, 12))
    tr_text(tk.Button(row2, command=on_clear_filters, **btn), "b_clear").pack(side="left", ipadx=6, ipady=1)
    tr_text(tk.Label(row2, bg=PANEL_BG, fg=DIM, font=FONT_SUB), "l_hint").pack(side="left", padx=12)

    # ---- Sağ panel ----
    # Paketleme sırası = yer önceliği: istatistik, butonlar, açıklamalar; en son sunucu dağılımı
    # (yer kalmazsa kırpılan o olur).
    rp, right_bg = glass_panel(R_RIGHT)
    stats_label = tk.Label(rp, text="", bg=PANEL_BG, fg=HEADER_COLOR, font=FONT_DATA_BOLD, justify="left")
    stats_label.pack(anchor="w", padx=14, pady=(8, 0))
    grow = tk.Frame(rp, bg=PANEL_BG)
    grow.pack(anchor="w", padx=14, pady=(6, 0), fill="x")
    gauge_canvas = tk.Canvas(grow, bg=PANEL_BG, bd=0, highlightthickness=0, width=72, height=72)
    gauge_canvas.pack(side="left")
    gauge_label = tk.Label(grow, text="", bg=PANEL_BG, fg=HEADER_COLOR, font=FONT_LABEL_BOLD,
                           justify="left", wraplength=180)
    gauge_label.pack(side="left", padx=6)

    for key, cmd in [("b_sel_untagged", select_untagged), ("b_open", open_selected),
                     ("b_tag", tag_selected), ("b_autotag", open_auto_tag),
                     ("b_group", auto_group_dependencies),
                     ("b_cfg", choose_server_config_dir),
                     ("b_delete", delete_selected)]:
        tr_text(tk.Button(rp, command=cmd, **btn), key).pack(fill="x", padx=14, pady=1, ipady=2)

    tr_text(tk.Label(rp, bg=PANEL_BG, fg=DIM, font=FONT_TINY, justify="left", wraplength=255),
            "transparency").pack(side="bottom", anchor="w", padx=14, pady=(2, 6))
    tr_text(tk.Label(rp, bg=PANEL_BG, fg=BADGE_COLOR, font=FONT_TINY, justify="left", wraplength=255),
            "legend").pack(side="bottom", anchor="w", padx=14, pady=4)
    tr_text(tk.Label(rp, bg=PANEL_BG, fg=HEADER_COLOR, font=FONT_SECTION),
            "h_dist").pack(anchor="w", padx=14, pady=(8, 2))
    summary_label = tk.Label(rp, text="", bg=PANEL_BG, fg=FG_COLOR, font=FONT_SUB,
                             justify="left", anchor="nw", wraplength=255)
    summary_label.pack(anchor="w", padx=14, fill="x")

    # ---- Tablo ----
    tp, table_bg = glass_panel(R_TABLE)
    tree = ttk.Treeview(tp, columns=[c[0] for c in COLUMNS], show="headings", selectmode="extended")
    vsb = ttk.Scrollbar(tp, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=vsb.set)
    vsb.pack(side="right", fill="y")
    tree.pack(side="left", fill="both", expand=True)
    for key, title, w, anchor in COLUMNS:
        tree.heading(key, text=T(title), command=lambda k=key: on_sort(k))
        tree.column(key, width=w, anchor=anchor, stretch=(key == "name"))
    tree.tag_configure("even", background=ROW_EVEN)
    tree.tag_configure("odd", background=ROW_ODD)
    tree.tag_configure("alert", foreground=BADGE_COLOR)
    tree.tag_configure("orphan", foreground=ORPHAN_COLOR)
    tree.tag_configure("required", foreground=REQUIRED_COLOR)
    tree.bind("<<TreeviewSelect>>", lambda e: update_gauge())


    def on_double_click(e):
        if tree.identify_region(e.x, e.y) != "cell":   # başlığa çift tık = sıralama, etiketleme değil
            return
        edit_tag(mod_by_id(tree.identify_row(e.y)))


    tree.bind("<Double-1>", on_double_click)

    menu = tk.Menu(root, tearoff=0, bg=PANEL_BG, fg=FG_COLOR, activebackground=BTN_HOVER, activeforeground=BG_COLOR)
    menu.add_command(label=T("m_open"), command=open_selected)
    menu.add_command(label=T("m_tag"), command=tag_selected)
    menu.add_separator()
    menu.add_command(label=T("m_delete"), command=delete_selected)
    _i18n.append(lambda: (menu.entryconfig(0, label=T("m_open")), menu.entryconfig(1, label=T("m_tag")),
                          menu.entryconfig(3, label=T("m_delete"))))


    def on_right_click(e):
        iid = tree.identify_row(e.y)
        if iid and iid not in tree.selection():
            tree.selection_set(iid)
        if tree.selection():
            menu.tk_popup(e.x_root, e.y_root)


    tree.bind("<Button-3>", on_right_click)

    _job = None


    def debounced(*_):
        global _job
        if _job:
            root.after_cancel(_job)
        _job = root.after(180, populate)


    search_var.trace_add("write", debounced)
    size_var.trace_add("write", debounced)
    server_filter_var.trace_add("write", lambda *a: populate())

    root.protocol("WM_DELETE_WINDOW", on_close)
    update_headings()
    rebuild_visuals()
    rescan()
    animate_radar()
    log.info("%s %s started (Tk %s, Pillow=%s, send2trash=%s, lang=%s)",
             APP_NAME, APP_VERSION, tk.TkVersion, HAVE_PIL, send2trash is not None, LANG)
    root.mainloop()
