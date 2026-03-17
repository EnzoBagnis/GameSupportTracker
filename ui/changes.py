import tkinter as tk
from tkinter import ttk
import webbrowser

from config import BG, BG2, BG3, BORDER, TEXT, TEXT_DIM, ACCENT2, YELLOW, STATUS_COLORS
from lang.l18n import t


def _selectable_label(parent, text, bg, fg, font, scroll_cb=None, **kw):
    """
    Read-only Text widget that looks exactly like a Label but allows text
    selection / copy-paste. No border, no editing cursor, no visual diff.
    """
    w = tk.Text(parent, height=1, bg=bg, fg=fg, font=font,
                relief="flat", borderwidth=0, highlightthickness=0,
                wrap="none", cursor="xterm", state="normal",
                padx=0, pady=0, **kw)
    w.insert("1.0", text)
    w.config(state="disabled")
    if scroll_cb:
        w.bind("<MouseWheel>", scroll_cb)
    return w


def build_changes_panel(parent, app):
    """
    Build the left changes panel inside `parent`.
    Returns (canvas, inner_frame, last_check_lbl, hist_inner, hist_canvas).
    The toggle arrow button has been removed.
    """
    lhdr = tk.Frame(parent, bg=BG2, pady=10, padx=14)
    lhdr.pack(fill="x")

    tk.Label(lhdr, text=t("changes_title"), bg=BG2,
             fg=ACCENT2, font=("Courier New", 9, "bold")).pack(anchor="w")

    last_check_lbl = tk.Label(lhdr, text=t("last_check_never"),
                              bg=BG2, fg=TEXT_DIM, font=("Courier New", 8))
    last_check_lbl.pack(anchor="w")

    tk.Frame(parent, bg=BORDER, height=1).pack(fill="x")

    # ── Current changes (scrollable, expands) ────────────────────────────────
    changes_frame = tk.Frame(parent, bg=BG2)
    changes_frame.pack(fill="both", expand=True)

    canvas = tk.Canvas(changes_frame, bg=BG2, highlightthickness=0)
    sb = ttk.Scrollbar(changes_frame, orient="vertical", command=canvas.yview)
    inner = tk.Frame(canvas, bg=BG2)
    inner.bind("<Configure>",
               lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=inner, anchor="nw")
    canvas.configure(yscrollcommand=sb.set)
    canvas.pack(side="left", fill="both", expand=True)
    sb.pack(side="right", fill="y")

    # ── History section (collapsible) ─────────────────────────────────────────
    tk.Frame(parent, bg=BORDER, height=1).pack(fill="x")

    hist_toggle_state = {"open": False}

    hist_hdr = tk.Frame(parent, bg=BG3, pady=6, padx=14, cursor="hand2")
    hist_hdr.pack(fill="x")

    hist_title_row = tk.Frame(hist_hdr, bg=BG3)
    hist_title_row.pack(fill="x")

    hist_lbl = tk.Label(hist_title_row, text=t("changes_history_title"),
                        bg=BG3, fg=TEXT_DIM, font=("Courier New", 8, "bold"),
                        cursor="hand2")
    hist_lbl.pack(side="left")

    hist_arrow = tk.Label(hist_title_row, text="▸", bg=BG3, fg=TEXT_DIM,
                          font=("Courier New", 8), cursor="hand2")
    hist_arrow.pack(side="right")

    hist_body_outer = tk.Frame(parent, bg=BG3)
    # Not packed by default (collapsed)

    hist_canvas = tk.Canvas(hist_body_outer, bg=BG3, highlightthickness=0, height=180)
    hist_sb = ttk.Scrollbar(hist_body_outer, orient="vertical", command=hist_canvas.yview)
    hist_inner = tk.Frame(hist_canvas, bg=BG3)
    hist_inner.bind("<Configure>",
                    lambda e: hist_canvas.configure(scrollregion=hist_canvas.bbox("all")))
    hist_canvas.create_window((0, 0), window=hist_inner, anchor="nw")
    hist_canvas.configure(yscrollcommand=hist_sb.set)
    hist_canvas.pack(side="left", fill="both", expand=True)
    hist_sb.pack(side="right", fill="y")

    def _toggle_hist(*_):
        if hist_toggle_state["open"]:
            hist_body_outer.pack_forget()
            hist_arrow.config(text="▸")
            hist_toggle_state["open"] = False
        else:
            hist_body_outer.pack(fill="x")
            hist_arrow.config(text="▾")
            hist_toggle_state["open"] = True

    for w in (hist_hdr, hist_title_row, hist_lbl, hist_arrow):
        w.bind("<Button-1>", _toggle_hist)

    return canvas, inner, last_check_lbl, hist_inner, hist_canvas


def _build_change_rows(container, entries, register_scroll_fn, scroll_cb, dim=False, app=None):
    """Render a list of change entry tuples into `container`."""
    bg = container["bg"]

    owned_set   = getattr(app, "_manual_owned",   set()) if app else set()
    steam_all   = getattr(app, "_steam_owned",    set()) if app else set()
    steam_bases = getattr(app, "_steam_bases",    None)  if app else None
    play_all    = getattr(app, "_playnite_owned", set()) if app else set()
    play_bases  = getattr(app, "_playnite_bases", None)  if app else None

    def _is_owned(game_name):
        if game_name in owned_set:
            return True
        try:
            from data import is_owned_on_steam, is_owned_on_playnite
            return (is_owned_on_steam(game_name, steam_all, steam_bases)
                    or is_owned_on_playnite(game_name, play_all, play_bases))
        except Exception:
            return False
    for entry in entries:
        icon    = entry[0]
        tab     = entry[1]
        game    = entry[2]
        status  = entry[3]
        desc    = entry[4]
        rel_url = entry[5] if len(entry) > 5 else ""

        row = tk.Frame(container, bg=bg, pady=5, padx=14)
        row.pack(fill="x")
        register_scroll_fn(row, scroll_cb)

        top_row = tk.Frame(row, bg=bg)
        top_row.pack(fill="x")
        register_scroll_fn(top_row, scroll_cb)

        fg_name = TEXT_DIM if dim else (ACCENT2 if _is_owned(game) else TEXT)
        tk.Label(top_row, text=icon, bg=bg,
                 font=("Segoe UI Emoji", 11)).pack(side="left")
        name_w = _selectable_label(top_row, "  " + game, bg=bg, fg=fg_name,
                                   font=("Courier New", 9, "bold"),
                                   scroll_cb=scroll_cb)
        name_w.pack(side="left", fill="x", expand=True)
        register_scroll_fn(name_w, scroll_cb)

        bot_row = tk.Frame(row, bg=bg)
        bot_row.pack(fill="x")
        register_scroll_fn(bot_row, scroll_cb)

        color = YELLOW if icon == "🏷️" else STATUS_COLORS.get(status, TEXT_DIM)
        if dim:
            color = TEXT_DIM
        desc_w = _selectable_label(bot_row, "   " + tab + " — " + desc,
                                   bg=bg, fg=color, font=("Courier New", 8),
                                   scroll_cb=scroll_cb)
        desc_w.pack(side="left", fill="x", expand=True)
        register_scroll_fn(desc_w, scroll_cb)

        if rel_url and not dim:
            lnk = tk.Label(bot_row, text=" ↗", bg=bg, fg=ACCENT2,
                           font=("Courier New", 8, "underline"), cursor="hand2")
            lnk.pack(side="left")
            lnk.bind("<Button-1>", lambda e, u=rel_url: webbrowser.open(u))

        tk.Frame(container, bg=BORDER, height=1).pack(fill="x", padx=14)


def refresh_changes(inner, changes, register_scroll_fn, scroll_cb, app=None):
    """Repopulate the current changes inner frame."""
    for w in inner.winfo_children():
        w.destroy()

    if not changes:
        tk.Label(inner, text=t("changes_none"),
                 bg=BG2, fg=TEXT_DIM, font=("Courier New", 9),
                 padx=14, pady=10).pack(anchor="w")
        return

    _build_change_rows(inner, changes, register_scroll_fn, scroll_cb, app=app)


def _run_summary(entries):
    """Return a short summary string like '➕×2  🔄×1  🏷️×1' for a run's entries."""
    counts = {}
    for e in entries:
        icon = e[0]
        counts[icon] = counts.get(icon, 0) + 1
    if not counts:
        return "—"
    # Canonical order
    order = ["➕", "➖", "🔄", "🏷️"]
    parts = []
    for icon in order:
        if icon in counts:
            parts.append(f"{icon}×{counts[icon]}")
    # Any other icons not in the order
    for icon, n in counts.items():
        if icon not in order:
            parts.append(f"{icon}×{n}")
    return "  ".join(parts)


def refresh_history(hist_inner, hist_canvas, history,
                    register_scroll_fn, scroll_cb):
    """
    Repopulate the history panel with one compact summary row per past run.
    `history` is a list of dicts (newest first):
      {"ts": "2025-01-01 12:00", "changes": [(icon, tab, game, status, desc, url), ...]}
    """
    for w in hist_inner.winfo_children():
        w.destroy()

    if not history:
        tk.Label(hist_inner, text=t("changes_history_empty"),
                 bg=BG3, fg=TEXT_DIM, font=("Courier New", 8),
                 padx=14, pady=8).pack(anchor="w")
        hist_canvas.configure(scrollregion=hist_canvas.bbox("all") or (0, 0, 1, 1))
        return

    for run in history:
        ts      = run.get("ts", "")
        entries = run.get("changes", [])
        summary = _run_summary(entries)

        row = tk.Frame(hist_inner, bg=BG3, padx=14, pady=5)
        row.pack(fill="x")
        register_scroll_fn(row, scroll_cb)

        # Date on the left
        tk.Label(row, text=ts, bg=BG3, fg=TEXT_DIM,
                 font=("Courier New", 8)).pack(side="left")

        # Separator dot
        tk.Label(row, text="  ·  ", bg=BG3, fg=TEXT_DIM,
                 font=("Courier New", 8)).pack(side="left")

        # Counters summary
        summary_lbl = tk.Label(row, text=summary if entries else t("changes_none"),
                               bg=BG3, fg=TEXT_DIM,
                               font=("Courier New", 8))
        summary_lbl.pack(side="left")

        tk.Frame(hist_inner, bg=BORDER, height=1).pack(fill="x", padx=8)

    hist_canvas.configure(scrollregion=hist_canvas.bbox("all") or (0, 0, 1, 1))