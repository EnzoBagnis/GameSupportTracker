import re
import csv
import io
import unicodedata

import requests

from config import (
    SHEET_ID, TABS, POPTRACKER_API, GITHUB_REPO_RE, SKIP_NAMES
)

URL_PATTERN = re.compile(r'https?://\S+')


# ── Sheet ──────────────────────────────────────────────────────────────────────

def fetch_tab(tab_name, gid):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={gid}"
    r = requests.get(url, timeout=15)
    if r.status_code != 200:
        return []
    return list(csv.reader(io.StringIO(r.content.decode("utf-8"))))


def rows_to_dict(rows, tab_name=""):
    """Parse raw CSV rows into {name: {status, notes, apworld}} dict."""
    if not rows:
        return {}

    # Playable Worlds : A=Game(0)  B=Status(1)  C=APWorld(2)  D=Notes(3)
    # Core Verified   : A=Game(0)  B=Notes(1)   (no APWorld column)
    if tab_name == "Core Verified":
        idx_name, idx_status, idx_apworld, idx_notes = 0, -1, -1, 1
    else:
        idx_name, idx_status, idx_apworld, idx_notes = 0, 1, 2, 3

    result = {}
    for row in rows:
        if len(row) <= idx_name:
            continue
        name = row[idx_name].strip()
        if not name or name in SKIP_NAMES or len(name) > 80:
            continue

        def _get(i):
            return row[i].strip() if i != -1 and i < len(row) else ""

        status  = _get(idx_status)
        apworld = _get(idx_apworld)
        notes   = _get(idx_notes)

        if status.lower() in ("status", "game", "do not sort"):
            continue

        result[name] = {"status": status, "notes": notes, "apworld": apworld}
    return result


# ── URL helpers ────────────────────────────────────────────────────────────────

def extract_urls(text):
    return URL_PATTERN.findall(text)


def extract_github_repo(notes, apworld=""):
    """Return (owner, repo) from the first valid GitHub URL found, or None."""
    for text in (apworld, notes):
        if not text:
            continue
        for url in extract_urls(text):
            m = GITHUB_REPO_RE.search(url)
            if m:
                owner = m.group(1)
                repo  = m.group(2)
                if repo.endswith(".git"):
                    repo = repo[:-4]
                if "/pull/" in url:
                    continue
                return owner, repo
    return None


# ── GitHub ─────────────────────────────────────────────────────────────────────

def fetch_github_release(owner, repo, token=""):
    """Return {tag, date, url}, None on error, or 'rate_limited' on 403/429."""
    try:
        api_url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"
        headers = {
            "User-Agent": "GameSupportTracker/1.0",
            "Accept":     "application/vnd.github+json",
        }
        if token:
            headers["Authorization"] = "Bearer " + token

        r = requests.get(api_url, timeout=10, headers=headers)
        if r.status_code in (403, 429):
            return "rate_limited"
        if r.status_code == 404:
            r2 = requests.get(
                f"https://api.github.com/repos/{owner}/{repo}/tags",
                timeout=10, headers=headers)
            if r2.status_code in (403, 429):
                return "rate_limited"
            if r2.status_code == 200:
                tags = r2.json()
                if tags:
                    return {"tag": tags[0].get("name", ""), "date": "", "url": ""}
            return None
        if r.status_code != 200:
            return None

        data     = r.json()
        raw_date = data.get("published_at", "")
        return {
            "tag":  data.get("tag_name", ""),
            "date": raw_date[:10] if raw_date else "",
            "url":  data.get("html_url", ""),
        }
    except Exception:
        return None


# ── PopTracker ─────────────────────────────────────────────────────────────────

def _normalize(name):
    n = name.lower()
    for prefix in ["category:", "game:"]:
        if n.startswith(prefix):
            n = n[len(prefix):]
    n = re.sub(r"[:\-_'\"!.,&()]", " ", n)
    n = re.sub(r"\s+", " ", n).strip()
    return n


def fetch_poptracker_games():
    try:
        headers = {"User-Agent": "GameSupportTracker/1.0"}
        r = requests.get(POPTRACKER_API, timeout=15, headers=headers)
        if r.status_code != 200:
            return set()
        data    = r.json()
        members = data.get("query", {}).get("categorymembers", [])
        return {_normalize(m.get("title", "")) for m in members}
    except Exception:
        return set()


def match_poptracker(game_name, poptracker_set):
    norm = _normalize(game_name)
    if norm in poptracker_set:
        return True
    for pt in poptracker_set:
        if norm in pt or pt in norm:
            if len(norm) > 4 and len(pt) > 4:
                return True
    return False


# ── Steam ──────────────────────────────────────────────────────────────────────

def _extract_acronym(name: str) -> str | None:
    """'Totally Accurate Battle Simulator (TABS)' -> 'tabs'"""
    match = re.search(r'\(([A-Z]{2,})\)', name)
    return match.group(1).lower() if match else None

def _build_acronym(name: str) -> str:
    """'Totally Accurate Battle Simulator' -> 'tabs'"""
    STOP = {"a", "an", "the", "of", "vs", "vs.", "and", "&", "in", "on", "at", "to", "for"}
    clean = re.sub(r"[^a-zA-Z0-9 ]", " ", name)
    words = clean.split()
    return "".join(w[0] for w in words if w.lower() not in STOP).lower()

def _normalize_steam(name: str) -> set[str]:
    """Retourne un set de variantes normalisées."""
    # Nom de base sans parenthèses
    clean = re.sub(r'\s*\(.*?\)', '', name).strip()
    base = re.sub(r"[^a-z0-9 ]", "", clean.lower())

    variants = {base}

    # Acronyme explicite: "Foo Bar (FB)" -> "fb"
    # Toujours fiable car écrit explicitement par Steam
    explicit = _extract_acronym(name)
    if explicit:
        variants.add(explicit)

    # Acronyme généré: "Totally Accurate Battle Simulator" -> "tabs"
    # Seulement si 3+ mots significatifs ET acronyme de 3+ caractères
    # → évite les faux positifs ("Hades" -> "h", "Hollow Knight" -> "hk")
    STOP = {"a", "an", "the", "of", "vs", "vs.", "and", "&", "in", "on", "at", "to", "for"}
    words = [w for w in re.sub(r"[^a-zA-Z0-9 ]", " ", clean).split()
             if w.lower() not in STOP and w[0].isalpha()]  # exclut les mots commençant par un chiffre
    if len(words) >= 3:
        acronym = "".join(w[0] for w in words).lower()
        if len(acronym) >= 3:
            variants.add(acronym)

    return variants


def fetch_steam_owned(api_key, steam_ids):
    """Return dict of {frozenset_of_variants: original_name} owned across all given Steam IDs."""
    owned = {}
    headers = {"User-Agent": "GameSupportTracker/1.0"}
    for sid in steam_ids:
        sid = sid.strip()
        if not sid:
            continue
        try:
            r = requests.get(
                "https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/",
                params={"key": api_key, "steamid": sid, "include_appinfo": True},
                timeout=15, headers=headers)
            if r.status_code != 200:
                continue
            for game in r.json().get("response", {}).get("games", []):
                appid = game["appid"]
                if appid not in owned:
                    owned[appid] = game.get("name", "")
        except Exception:
            continue

    # Construit un set "à plat" de toutes les variantes -> pour lookup rapide
    all_variants: set[str] = set()
    for name in owned.values():
        if name:
            for v in _normalize_steam(name):
                all_variants.add(v)

    return all_variants, len(owned)


def is_owned_on_steam(sheet_name: str, steam_variants: set[str]) -> bool:
    """Vérifie si un jeu du sheet est dans les variantes Steam."""
    return bool(_normalize_steam(sheet_name) & steam_variants)


# ── Playnite ───────────────────────────────────────────────────────────────────
# Reads the games.db file from a Playnite backup ZIP.
# Playnite stores its library in a LiteDB binary format. We parse it directly
# by locating BSON "Favorite" boolean fields (present exactly once per game
# document) and scanning backwards for the game's Name field.
#
# How the user creates the backup:
#   Playnite main menu (☰) → Library → Save library data
#   → saves a .zip file the user can select in GST settings.

def _parse_games_db(db_bytes: bytes) -> list[str]:
    """
    Extract game names from a Playnite games.db (LiteDB/BSON) binary blob.
    Returns a list of unique game name strings.

    Strategy:
      - Use \\x08Favorite\\x00 as the anchor: this boolean field appears exactly
        once per game document, even for games without a store ID.
      - Walk backwards (up to 80 KB) from each anchor to find the last
        \\x02Name\\x00 field that belongs to the game doc, skipping:
          * Link sub-document names (Name immediately followed by Url)
          * CompletionStatus names (Name immediately followed by RecentActivity)
      - Also check 50 KB forward for edge cases where the Name segment lands
        after the Favorite in the file (heavily fragmented docs).
    """
    import struct

    fav_needle    = b'\x08Favorite\x00'
    name_needle   = b'\x02Name\x00'
    url_needle    = b'\x02Url\x00'
    recent_needle = b'RecentActivity'
    LOOK_BACK     = 80_000
    LOOK_FWD      = 50_000

    def _read_bson_string(data, pos):
        if pos + 4 > len(data):
            return None
        n = struct.unpack_from('<I', data, pos)[0]
        if not (1 <= n <= 512):
            return None
        end = pos + 4 + n - 1
        if end > len(data):
            return None
        v = data[pos + 4:end].decode('utf-8', errors='replace')
        return None if ('\x00' in v or v.count('\ufffd') > 1) else v

    def _find_game_name(data, anchor):
        """Search backwards then forwards from anchor for the game Name."""
        # ── backwards pass ────────────────────────────────────────────────
        window_start = max(0, anchor - LOOK_BACK)
        window = data[window_start:anchor]
        ni = len(window)
        while True:
            ni = window.rfind(name_needle, 0, ni)
            if ni == -1:
                break
            abs_ni  = window_start + ni
            candidate = _read_bson_string(data, abs_ni + len(name_needle))
            if not candidate:
                continue
            val_end = abs_ni + len(name_needle) + 4 + len(candidate)
            after   = data[val_end:val_end + 20]
            if url_needle in after or recent_needle in after:
                continue
            return candidate

        # ── forward pass (fragmented docs) ───────────────────────────────
        fwd_end = min(len(data), anchor + LOOK_FWD)
        ni = anchor
        while True:
            ni = data.find(name_needle, ni + 1, fwd_end)
            if ni == -1:
                break
            candidate = _read_bson_string(data, ni + len(name_needle))
            if not candidate:
                continue
            val_end = ni + len(name_needle) + 4 + len(candidate)
            after   = data[val_end:val_end + 20]
            if url_needle in after or recent_needle in after:
                continue
            return candidate

        return None

    games = []
    seen  = set()
    pos   = 0

    while True:
        fi = db_bytes.find(fav_needle, pos)
        if fi == -1:
            break
        pos = fi + 1

        name = _find_game_name(db_bytes, fi)
        if name and name not in seen:
            seen.add(name)
            games.append(name)

    return games


def load_playnite_library(path: str) -> tuple[set[str], int]:
    """
    Load a Playnite library from a backup ZIP (produced by
    Library → Save library data) and return (variants_set, total_count).
    Returns (set(), 0) on any error.
    """
    import zipfile

    try:
        with zipfile.ZipFile(path, 'r') as z:
            # The games database is always at library/games.db inside the ZIP
            with z.open('library/games.db') as f:
                db_bytes = f.read()
    except Exception:
        return set(), 0

    names = _parse_games_db(db_bytes)

    all_variants: set[str] = set()
    for name in names:
        all_variants.update(_normalize_steam(name))

    return all_variants, len(names)


def is_owned_on_playnite(sheet_name: str, playnite_variants: set[str]) -> bool:
    return bool(_normalize_steam(sheet_name) & playnite_variants)