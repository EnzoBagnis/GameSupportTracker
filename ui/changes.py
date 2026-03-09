import tkinter as tk
from tkinter import ttk
import webbrowser

from config import BG, BG2, BG3, BORDER, TEXT, TEXT_DIM, ACCENT2, YELLOW, STATUS_COLORS
from lang.l18n import t


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


def _build_change_rows(container, entries, register_scroll_fn, scroll_cb, dim=False):
    """Render a list of change entry tuples into `container`."""
    bg = container["bg"]
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

        fg_name = TEXT_DIM if dim else TEXT
        tk.Label(top_row, text=icon, bg=bg,
                 font=("Segoe UI Emoji", 11)).pack(side="left")
        tk.Label(top_row, text="  " + game, bg=bg, fg=fg_name,
                 font=("Courier New", 9, "bold"),
                 wraplength=240, justify="left").pack(side="left")

        bot_row = tk.Frame(row, bg=bg)
        bot_row.pack(fill="x")
        register_scroll_fn(bot_row, scroll_cb)

        color = YELLOW if icon == "🏷️" else STATUS_COLORS.get(status, TEXT_DIM)
        if dim:
            color = TEXT_DIM
        tk.Label(bot_row, text="   " + tab + " — " + desc,
                 bg=bg, fg=color, font=("Courier New", 8)).pack(side="left")

        if rel_url and not dim:
            lnk = tk.Label(bot_row, text=" ↗", bg=bg, fg=ACCENT2,
                           font=("Courier New", 8, "underline"), cursor="hand2")
            lnk.pack(side="left")
            lnk.bind("<Button-1>", lambda e, u=rel_url: webbrowser.open(u))

        tk.Frame(container, bg=BORDER, height=1).pack(fill="x", padx=14)


def refresh_changes(inner, changes, register_scroll_fn, scroll_cb):
    """Repopulate the current changes inner frame."""
    for w in inner.winfo_children():
        w.destroy()

    if not changes:
        tk.Label(inner, text=t("changes_none"),
                 bg=BG2, fg=TEXT_DIM, font=("Courier New", 9),
                 padx=14, pady=10).pack(anchor="w")
        return

    _build_change_rows(inner, changes, register_scroll_fn, scroll_cb)


def refresh_history(hist_inner, hist_canvas, history,
                    register_scroll_fn, scroll_cb):
    """
    Repopulate the history panel.
    `history` is a list of dicts (newest first, max 10):
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

        hdr = tk.Frame(hist_inner, bg=BG3, padx=14, pady=4)
        hdr.pack(fill="x")
        register_scroll_fn(hdr, scroll_cb)

        count_txt = t("changes_history_count", n=len(entries)) if entries \
            else t("changes_none")
        tk.Label(hdr, text=f"  {ts}  ·  {count_txt}",
                 bg=BG3, fg=TEXT_DIM, font=("Courier New", 8, "bold")).pack(anchor="w")

        if entries:
            _build_change_rows(hist_inner, entries,
                               register_scroll_fn, scroll_cb, dim=True)
        else:
            tk.Label(hist_inner, text=t("changes_none"),
                     bg=BG3, fg=TEXT_DIM, font=("Courier New", 8),
                     padx=28, pady=2).pack(anchor="w")

        tk.Frame(hist_inner, bg=BORDER, height=1).pack(fill="x")

    hist_canvas.configure(scrollregion=hist_canvas.bbox("all") or (0, 0, 1, 1))