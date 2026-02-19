import sys
import os
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.animation as animation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import seaborn as sns
from scipy import stats

matplotlib.rcParams["font.family"] = "DejaVu Sans"

BG_DARK    = "#0D1117"
BG_PANEL   = "#161B22"
BG_WIDGET  = "#21262D"
BG_BTN     = "#1F2937"
BG_BTN_HOV = "#2D3748"
BG_BTN_ACT = "#E63946"
BORDER     = "#30363D"
FG_DIM     = "#8B949E"
FG_MAIN    = "#C9D1D9"
YELLOW     = "#F1FA8C"
WHITE      = "#FFFFFF"
ACCENT     = "#58A6FF"
GREEN      = "#3FB950"
RED        = "#F85149"

AUTO_PALETTE = [
    "#E63946", "#457B9D", "#2A9D8F", "#F4A261", "#A8DADC",
    "#E9C46A", "#264653", "#8338EC", "#FB5607", "#3A86FF",
]


def detect_columns(df):
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    cat_cols = df.select_dtypes(include=["object", "category", "string"]).columns.tolist()
    return num_cols, cat_cols


def make_palette(categories):
    pal = {}
    for i, cat in enumerate(categories):
        pal[cat] = AUTO_PALETTE[i % len(AUTO_PALETTE)]
    return pal


def style_ax(ax):
    ax.set_facecolor(BG_PANEL)
    for spine in ax.spines.values():
        spine.set_edgecolor(BORDER)
    ax.tick_params(colors=FG_DIM)
    ax.xaxis.label.set_color(FG_DIM)
    ax.yaxis.label.set_color(FG_DIM)
    ax.title.set_color(WHITE)


def build_histogramme(ax, df, col, cat_col=None, palette=None):
    if cat_col and cat_col in df.columns and palette:
        for cat in df[cat_col].unique():
            data = df[df[cat_col] == cat][col].dropna()
            ax.hist(data, bins=20, alpha=0.68, label=str(cat),
                    color=palette.get(str(cat), ACCENT),
                    edgecolor=WHITE, linewidth=0.3)
            m = data.mean()
            ax.axvline(m, color=palette.get(str(cat), ACCENT),
                       linestyle="--", linewidth=1.4, alpha=0.9)
            ax.text(m + (df[col].max() - df[col].min()) * 0.01,
                    ax.get_ylim()[1] * 0.85, f"u={m:.2f}",
                    color=palette.get(str(cat), ACCENT), fontsize=7,
                    bbox=dict(facecolor=BG_WIDGET, edgecolor="none", alpha=0.6, pad=1))
        ax.legend(facecolor=BG_WIDGET, edgecolor=BORDER, labelcolor=WHITE, fontsize=8)
    else:
        data = df[col].dropna()
        ax.hist(data, bins=20, alpha=0.78, color=ACCENT,
                edgecolor=WHITE, linewidth=0.3)
        m = data.mean()
        ax.axvline(m, color=YELLOW, linestyle="--", linewidth=1.6)
        ax.text(m, ax.get_ylim()[1] * 0.9, f" u={m:.2f}",
                color=YELLOW, fontsize=8)

    ax.set_title(f"Distribution  {col}", fontsize=12, pad=8)
    ax.set_xlabel(col)
    ax.set_ylabel("Frequence")
    ax.grid(axis="y", color=BORDER, linewidth=0.5, alpha=0.6)
    style_ax(ax)


def build_scatter(ax, df, xcol, ycol, cat_col=None, palette=None):
    if cat_col and cat_col in df.columns and palette:
        for cat in df[cat_col].unique():
            sub = df[df[cat_col] == cat][[xcol, ycol]].dropna()
            ax.scatter(sub[xcol], sub[ycol],
                       c=palette.get(str(cat), ACCENT), label=str(cat),
                       alpha=0.80, s=55, edgecolors=WHITE, linewidths=0.25)
        ax.legend(facecolor=BG_WIDGET, edgecolor=BORDER, labelcolor=WHITE, fontsize=8)
    else:
        clean = df[[xcol, ycol]].dropna()
        ax.scatter(clean[xcol], clean[ycol], c=ACCENT,
                   alpha=0.75, s=50, edgecolors=WHITE, linewidths=0.25)

    clean = df[[xcol, ycol]].dropna()
    if len(clean) >= 2:
        slope, intercept, r, p, _ = stats.linregress(clean[xcol], clean[ycol])
        xl = np.linspace(clean[xcol].min(), clean[xcol].max(), 300)
        yl = slope * xl + intercept
        ax.plot(xl, yl, color=YELLOW, linewidth=2,
                label=f"Regression (R2={r**2:.3f})")
        ax.fill_between(xl, yl - yl.std() * 0.3, yl + yl.std() * 0.3,
                        color=YELLOW, alpha=0.06)
        ax.annotate(f"y={slope:.2f}x+{intercept:.2f}\np={p:.2e}",
                    xy=(0.04, 0.86), xycoords="axes fraction", fontsize=8,
                    color=YELLOW,
                    bbox=dict(boxstyle="round,pad=0.3", facecolor=BG_WIDGET,
                              edgecolor=YELLOW, alpha=0.85))

    ax.set_title(f"Scatter  {xcol}  vs  {ycol}", fontsize=12, pad=8)
    ax.set_xlabel(xcol)
    ax.set_ylabel(ycol)
    ax.grid(color=BORDER, linewidth=0.5, alpha=0.6)
    style_ax(ax)


def build_heatmap(ax, df, num_cols):
    cols = num_cols[:10]
    corr = df[cols].corr()
    labels = [c[:10] for c in cols]
    sns.heatmap(corr, ax=ax, annot=True, fmt=".2f", cmap="coolwarm",
                linewidths=0.8, linecolor=BG_DARK,
                xticklabels=labels, yticklabels=labels,
                annot_kws={"size": max(7, 11 - len(cols))},
                vmin=-1, vmax=1, cbar_kws={"shrink": 0.82})
    ax.set_title("Heatmap de Correlation", fontsize=12, pad=8, color=WHITE)
    ax.tick_params(colors=FG_DIM, labelsize=8)
    ax.xaxis.label.set_color(FG_DIM)
    ax.yaxis.label.set_color(FG_DIM)
    cbar = ax.collections[0].colorbar
    cbar.ax.tick_params(colors=FG_DIM)
    cbar.outline.set_edgecolor(BORDER)
    ax.set_facecolor(BG_PANEL)


def build_courbe(ax, df, col, cat_col=None, palette=None):
    if cat_col and cat_col in df.columns and palette:
        for cat in df[cat_col].unique():
            data = df[df[cat_col] == cat][col].dropna().values
            ax.plot(np.arange(len(data)), data,
                    color=palette.get(str(cat), ACCENT),
                    linewidth=1.8, label=str(cat),
                    marker="o", markersize=2.5, alpha=0.85)
        ax.legend(facecolor=BG_WIDGET, edgecolor=BORDER, labelcolor=WHITE, fontsize=8)
    else:
        data = df[col].dropna().values
        ax.plot(np.arange(len(data)), data, color=ACCENT,
                linewidth=1.8, marker="o", markersize=2.5, alpha=0.85)

    ax.set_title(f"Evolution  {col}", fontsize=12, pad=8)
    ax.set_xlabel("Index")
    ax.set_ylabel(col)
    ax.grid(color=BORDER, linewidth=0.5, alpha=0.6)
    style_ax(ax)


class CSVAnalyser(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("CSV Analyser  |  Visualisation Universelle")
        self.configure(bg=BG_DARK)
        self.geometry("1300x840")
        self.minsize(1000, 660)
        self.df        = None
        self.filepath  = None
        self.num_cols  = []
        self.cat_cols  = []
        self.palette   = {}
        self._ani_ref  = None
        self._current_btn = None
        self._build_ui()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _on_close(self):
        self._ani_ref = None
        self.destroy()

    def _build_ui(self):
        self._build_sidebar()
        self._build_main()
        self._build_status()
        self._show_accueil()

    def _build_sidebar(self):
        self.sidebar = tk.Frame(self, bg=BG_PANEL, width=240)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        logo = tk.Frame(self.sidebar, bg=BG_PANEL, pady=16)
        logo.pack(fill="x")
        tk.Label(logo, text="CSV", font=("DejaVu Sans", 28, "bold"),
                 fg=ACCENT, bg=BG_PANEL).pack()
        tk.Label(logo, text="Analyser", font=("DejaVu Sans", 11),
                 fg=FG_DIM, bg=BG_PANEL).pack()

        self._sep(self.sidebar)

        load_btn = tk.Button(
            self.sidebar, text="  Charger un CSV",
            font=("DejaVu Sans", 10, "bold"),
            fg=WHITE, bg=GREEN, activebackground="#2EA043",
            activeforeground=WHITE, bd=0, pady=10, cursor="hand2",
            command=self._charger_csv
        )
        load_btn.pack(fill="x", padx=12, pady=(10, 4))

        self.file_lbl = tk.Label(
            self.sidebar, text="Aucun fichier charge",
            font=("DejaVu Sans", 8), fg=FG_DIM, bg=BG_PANEL,
            wraplength=200, justify="center"
        )
        self.file_lbl.pack(padx=10, pady=(0, 8))

        self._sep(self.sidebar)

        tk.Label(self.sidebar, text="NAVIGATION",
                 font=("DejaVu Sans", 8, "bold"),
                 fg=FG_DIM, bg=BG_PANEL, anchor="w",
                 padx=18, pady=6).pack(fill="x")

        self._nav_items_def = [
            ("\u2302", "Accueil",              self._show_accueil),
            ("\u229e", "Dashboard complet",    self._show_dashboard),
            ("\u2261", "Histogramme",          self._show_histogramme),
            ("\u25C6", "Scatter + Regression", self._show_scatter),
            ("\u25A6", "Heatmap Correlation",  self._show_heatmap),
            ("\u25B6", "Animation courbes",    self._show_animation),
            ("\u03A3", "Statistiques",         self._show_stats),
            ("\u2630", "Apercu donnees",       self._show_apercu),
        ]
        self._nav_btns = []
        for icon, label, cmd in self._nav_items_def:
            btn = self._nav_btn(self.sidebar, icon, label, cmd)
            self._nav_btns.append(btn)

        self._sep(self.sidebar)

        tk.Label(self.sidebar, text="DATASET",
                 font=("DejaVu Sans", 8, "bold"),
                 fg=FG_DIM, bg=BG_PANEL, anchor="w",
                 padx=18, pady=4).pack(fill="x")

        self.info_frame = tk.Frame(self.sidebar, bg=BG_PANEL)
        self.info_frame.pack(fill="x", padx=18)
        self._info_rows = {}
        for key in ("Lignes", "Colonnes", "Numeriques", "Categorielles"):
            row = tk.Frame(self.info_frame, bg=BG_PANEL)
            row.pack(fill="x", pady=2)
            tk.Label(row, text=key, font=("DejaVu Sans", 9),
                     fg=FG_DIM, bg=BG_PANEL, anchor="w").pack(side="left")
            val = tk.Label(row, text="—", font=("DejaVu Sans", 9, "bold"),
                           fg=ACCENT, bg=BG_PANEL, anchor="e")
            val.pack(side="right")
            self._info_rows[key] = val

        self._sep(self.sidebar)

        self.legend_frame = tk.Frame(self.sidebar, bg=BG_PANEL)
        self.legend_frame.pack(fill="x", padx=14, pady=4)

        self._sep(self.sidebar)

        export_btn = tk.Button(
            self.sidebar, text="Exporter Dashboard PNG",
            font=("DejaVu Sans", 9, "bold"),
            fg=WHITE, bg="#1A4480", activebackground="#2563EB",
            activeforeground=WHITE, bd=0, pady=8, cursor="hand2",
            command=self._export_png
        )
        export_btn.pack(side="bottom", fill="x", padx=12, pady=(4, 14))

    def _sep(self, parent):
        tk.Frame(parent, bg=BORDER, height=1).pack(fill="x", padx=12, pady=6)

    def _nav_btn(self, parent, icon, label, cmd):
        frame = tk.Frame(parent, bg=BG_PANEL, cursor="hand2")
        frame.pack(fill="x", padx=10, pady=2)

        icon_lbl = tk.Label(frame, text=icon, font=("DejaVu Sans", 13),
                            fg=FG_DIM, bg=BG_PANEL, width=3)
        icon_lbl.pack(side="left", padx=(6, 2), pady=5)

        text_lbl = tk.Label(frame, text=label, font=("DejaVu Sans", 10),
                            fg=FG_MAIN, bg=BG_PANEL, anchor="w")
        text_lbl.pack(side="left", fill="x", expand=True)

        def on_enter(e):
            if frame != self._current_btn:
                for w in (frame, icon_lbl, text_lbl):
                    w.configure(bg=BG_BTN_HOV)

        def on_leave(e):
            if frame != self._current_btn:
                for w in (frame, icon_lbl, text_lbl):
                    w.configure(bg=BG_PANEL)

        def on_click(e):
            self._set_active(frame, icon_lbl, text_lbl)
            cmd()

        for w in (frame, icon_lbl, text_lbl):
            w.bind("<Enter>", on_enter)
            w.bind("<Leave>", on_leave)
            w.bind("<Button-1>", on_click)

        frame._icon = icon_lbl
        frame._text = text_lbl
        return frame

    def _set_active(self, frame, icon_lbl, text_lbl):
        if self._current_btn:
            prev = self._current_btn
            for w in (prev, prev._icon, prev._text):
                w.configure(bg=BG_PANEL)
            prev._icon.configure(fg=FG_DIM)
            prev._text.configure(fg=FG_MAIN)
        self._current_btn = frame
        for w in (frame, icon_lbl, text_lbl):
            w.configure(bg=BG_BTN_ACT)
        icon_lbl.configure(fg=WHITE)
        text_lbl.configure(fg=WHITE)

    def _build_main(self):
        self.main_frame = tk.Frame(self, bg=BG_DARK)
        self.main_frame.pack(side="left", fill="both", expand=True)

        self.header = tk.Frame(self.main_frame, bg=BG_PANEL, height=52)
        self.header.pack(fill="x")
        self.header.pack_propagate(False)

        self.page_title = tk.Label(self.header, text="Accueil",
                                   font=("DejaVu Sans", 15, "bold"),
                                   fg=WHITE, bg=BG_PANEL, padx=20)
        self.page_title.pack(side="left", fill="y")

        self.page_sub = tk.Label(self.header, text="",
                                 font=("DejaVu Sans", 9),
                                 fg=FG_DIM, bg=BG_PANEL, padx=6)
        self.page_sub.pack(side="left", fill="y")

        self.content = tk.Frame(self.main_frame, bg=BG_DARK)
        self.content.pack(fill="both", expand=True)

    def _build_status(self):
        bar = tk.Frame(self.main_frame, bg=BG_PANEL, height=26)
        bar.pack(side="bottom", fill="x")
        bar.pack_propagate(False)
        self.status_var = tk.StringVar(value="Aucun fichier charge. Cliquez sur 'Charger un CSV'.")
        tk.Label(bar, textvariable=self.status_var,
                 font=("DejaVu Sans", 8), fg=FG_DIM, bg=BG_PANEL,
                 padx=14, anchor="w").pack(side="left", fill="y")
        tk.Label(bar, text="CSV Analyser",
                 font=("DejaVu Sans", 8), fg=BORDER, bg=BG_PANEL,
                 padx=14, anchor="e").pack(side="right", fill="y")

    def _clear(self):
        self._ani_ref = None
        for w in self.content.winfo_children():
            w.destroy()

    def _set_header(self, title, sub=""):
        self.page_title.configure(text=title)
        self.page_sub.configure(text=sub)

    def _embed(self, fig, toolbar=True):
        canvas = FigureCanvasTkAgg(fig, master=self.content)
        canvas.draw()
        if toolbar:
            tf = tk.Frame(self.content, bg=BG_DARK)
            tf.pack(fill="x", padx=4)
            tb = NavigationToolbar2Tk(canvas, tf)
            tb.configure(background=BG_DARK)
            for child in tb.winfo_children():
                try:
                    child.configure(background=BG_DARK)
                except Exception:
                    pass
            tb.update()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        return canvas

    def _need_data(self):
        if self.df is None:
            messagebox.showwarning(
                "Aucun fichier",
                "Veuillez d'abord charger un fichier CSV\nvia le bouton 'Charger un CSV'."
            )
            return False
        return True

    def _charger_csv(self):
        path = filedialog.askopenfilename(
            title="Selectionner un fichier CSV",
            filetypes=[("Fichiers CSV", "*.csv"), ("Tous", "*.*")]
        )
        if not path:
            return

        try:
            df_raw = pd.read_csv(path)
        except Exception as e:
            messagebox.showerror("Erreur de lecture", f"Impossible de lire le fichier :\n{e}")
            return

        if df_raw.empty:
            messagebox.showerror("Fichier vide", "Le fichier CSV ne contient aucune donnee.")
            return

        num_cols, cat_cols = detect_columns(df_raw)

        if not num_cols:
            messagebox.showerror(
                "Donnees incompatibles",
                "Le fichier ne contient aucune colonne numerique.\n"
                "Au moins une colonne numerique est requise."
            )
            return

        self.df       = df_raw
        self.filepath = path
        self.num_cols = num_cols
        self.cat_cols = cat_cols

        if cat_cols:
            first_cat = cat_cols[0]
            cats = [str(c) for c in self.df[first_cat].unique()]
            self.palette = make_palette(cats)
        else:
            self.palette = {}

        fname = os.path.basename(path)
        self.file_lbl.configure(text=fname, fg=GREEN)
        self._info_rows["Lignes"].configure(text=str(len(self.df)))
        self._info_rows["Colonnes"].configure(text=str(len(self.df.columns)))
        self._info_rows["Numeriques"].configure(text=str(len(num_cols)))
        self._info_rows["Categorielles"].configure(text=str(len(cat_cols)))

        for w in self.legend_frame.winfo_children():
            w.destroy()
        if cat_cols:
            first_cat = cat_cols[0]
            tk.Label(self.legend_frame,
                     text=f"Categorie : {first_cat}",
                     font=("DejaVu Sans", 8, "bold"),
                     fg=FG_DIM, bg=BG_PANEL, anchor="w").pack(fill="x", pady=(4, 2))
            for cat, color in self.palette.items():
                row = tk.Frame(self.legend_frame, bg=BG_PANEL)
                row.pack(fill="x", pady=1)
                dot = tk.Canvas(row, width=12, height=12, bg=BG_PANEL,
                                highlightthickness=0)
                dot.pack(side="left", padx=(0, 5))
                dot.create_oval(1, 1, 11, 11, fill=color, outline="")
                tk.Label(row, text=str(cat), font=("DejaVu Sans", 9),
                         fg=FG_MAIN, bg=BG_PANEL, anchor="w").pack(side="left")

        self.status_var.set(
            f"Fichier charge : {fname}  |  "
            f"{len(self.df)} lignes  {len(num_cols)} variables numeriques  "
            f"{len(cat_cols)} categories"
        )
        self._show_accueil()

    def _col_selector(self, parent, label, choices, default=0, width=22):
        row = tk.Frame(parent, bg=BG_PANEL)
        row.pack(side="left", padx=8, pady=4)
        tk.Label(row, text=label, font=("DejaVu Sans", 9),
                 fg=FG_DIM, bg=BG_PANEL).pack(anchor="w")
        var = tk.StringVar(value=choices[default] if choices else "")
        cb = ttk.Combobox(row, textvariable=var, values=choices,
                          state="readonly", width=width,
                          font=("DejaVu Sans", 9))
        cb.pack()
        return var

    def _ctrl_bar(self, widgets_fn):
        bar = tk.Frame(self.content, bg=BG_PANEL, height=50)
        bar.pack(fill="x")
        bar.pack_propagate(False)
        widgets_fn(bar)
        return bar

    def _show_accueil(self):
        self._clear()
        self._set_header("Accueil", "Bienvenue dans CSV Analyser")
        self.status_var.set(
            "Chargez un fichier CSV pour commencer."
            if self.df is None else
            f"Fichier actif : {os.path.basename(self.filepath)}"
        )

        center = tk.Frame(self.content, bg=BG_DARK)
        center.pack(expand=True)

        tk.Label(center, text="CSV Analyser",
                 font=("DejaVu Sans", 32, "bold"),
                 fg=ACCENT, bg=BG_DARK).pack(pady=(40, 6))
        tk.Label(center,
                 text="Chargez n'importe quel fichier CSV et explorez vos donnees.",
                 font=("DejaVu Sans", 12), fg=FG_DIM, bg=BG_DARK).pack(pady=(0, 30))

        if self.df is None:
            cta = tk.Button(center, text="  Charger un fichier CSV",
                            font=("DejaVu Sans", 12, "bold"),
                            fg=WHITE, bg=GREEN, activebackground="#2EA043",
                            activeforeground=WHITE, bd=0, padx=26, pady=12,
                            cursor="hand2", command=self._charger_csv)
            cta.pack(pady=10)
            tk.Label(center,
                     text="Formats acceptes : .csv  (separateur virgule ou point-virgule)",
                     font=("DejaVu Sans", 9), fg=FG_DIM, bg=BG_DARK).pack(pady=(16, 0))
        else:
            cards_data = [
                (str(len(self.df)),       "Lignes"),
                (str(len(self.df.columns)), "Colonnes"),
                (str(len(self.num_cols)), "Num. variables"),
                (str(len(self.cat_cols)), "Cat. variables"),
            ]
            card_row = tk.Frame(center, bg=BG_DARK)
            card_row.pack(pady=10)
            for val, lbl in cards_data:
                card = tk.Frame(card_row, bg=BG_PANEL, padx=26, pady=16,
                                highlightbackground=BORDER, highlightthickness=1)
                card.pack(side="left", padx=10)
                tk.Label(card, text=val, font=("DejaVu Sans", 26, "bold"),
                         fg=ACCENT, bg=BG_PANEL).pack()
                tk.Label(card, text=lbl, font=("DejaVu Sans", 9),
                         fg=FG_DIM, bg=BG_PANEL).pack()

            tk.Label(center, text=f"Fichier : {os.path.basename(self.filepath)}",
                     font=("DejaVu Sans", 10, "bold"),
                     fg=GREEN, bg=BG_DARK).pack(pady=(18, 4))

            cols_text = "  ".join(self.df.columns.tolist()[:12])
            if len(self.df.columns) > 12:
                cols_text += f"  ... (+{len(self.df.columns)-12})"
            tk.Label(center, text=f"Colonnes : {cols_text}",
                     font=("DejaVu Sans", 8), fg=FG_DIM, bg=BG_DARK,
                     wraplength=800, justify="center").pack()

            change_btn = tk.Button(center, text="Changer de fichier",
                                   font=("DejaVu Sans", 9),
                                   fg=WHITE, bg=BG_BTN, activebackground=BG_BTN_HOV,
                                   activeforeground=WHITE, bd=0, padx=14, pady=6,
                                   cursor="hand2", command=self._charger_csv)
            change_btn.pack(pady=14)

    def _show_dashboard(self):
        if not self._need_data():
            return
        self._clear()
        self._set_header("Dashboard complet", "4 graphiques en un seul affichage")
        self.status_var.set("Rendu en cours...")
        self.update_idletasks()

        n = self.num_cols
        cat = self.cat_cols[0] if self.cat_cols else None

        col_hist = n[0]
        col_x    = n[0]
        col_y    = n[1] if len(n) > 1 else n[0]
        col_crb  = n[0]

        fig = plt.Figure(figsize=(15, 10), facecolor=BG_DARK)
        fig.suptitle(f"Dashboard  |  {os.path.basename(self.filepath)}",
                     fontsize=18, fontweight="bold", color=WHITE, y=0.99)
        gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.48, wspace=0.40)

        build_histogramme(fig.add_subplot(gs[0, 0]), self.df, col_hist, cat, self.palette)
        build_scatter(fig.add_subplot(gs[0, 1]), self.df, col_x, col_y, cat, self.palette)
        build_heatmap(fig.add_subplot(gs[1, 0]), self.df, n)
        build_courbe(fig.add_subplot(gs[1, 1]), self.df, col_crb, cat, self.palette)

        self._embed(fig)
        self.status_var.set("Dashboard affiche.")

    def _show_histogramme(self):
        if not self._need_data():
            return
        self._clear()
        self._set_header("Histogramme", "Distribution d'une variable numerique")

        sel_col = tk.StringVar(value=self.num_cols[0])
        sel_cat = tk.StringVar(
            value=self.cat_cols[0] if self.cat_cols else "Aucune")

        def draw():
            for w in self.content.winfo_children():
                if isinstance(w, FigureCanvasTkAgg.__class__) or hasattr(w, "get_tk_widget"):
                    pass
            for w in list(self.content.winfo_children()):
                if not isinstance(w, tk.Frame) or w.winfo_height() > 50:
                    w.destroy()

            col = sel_col.get()
            cat = sel_cat.get() if sel_cat.get() != "Aucune" else None
            pal = self.palette if cat else None

            fig = plt.Figure(figsize=(12, 6), facecolor=BG_DARK)
            ax = fig.add_subplot(111)
            build_histogramme(ax, self.df, col, cat, pal)
            fig.tight_layout(pad=2)
            self._embed(fig)
            self.status_var.set(f"Histogramme : {col}")

        def ctrl(bar):
            self._col_selector_widget(bar, "Variable", self.num_cols, sel_col)
            cats_opts = ["Aucune"] + self.cat_cols
            self._col_selector_widget(bar, "Couleur par", cats_opts, sel_cat)
            tk.Button(bar, text="Afficher",
                      font=("DejaVu Sans", 9, "bold"),
                      fg=WHITE, bg=ACCENT, activebackground="#388BFD",
                      activeforeground=WHITE, bd=0, padx=16, pady=4,
                      cursor="hand2", command=draw).pack(side="left", padx=8, pady=10)

        self._ctrl_bar(ctrl)
        draw()

    def _show_scatter(self):
        if not self._need_data():
            return
        self._clear()
        self._set_header("Scatter Plot + Regression", "Relation entre deux variables")

        sel_x   = tk.StringVar(value=self.num_cols[0])
        sel_y   = tk.StringVar(value=self.num_cols[1] if len(self.num_cols) > 1 else self.num_cols[0])
        sel_cat = tk.StringVar(value=self.cat_cols[0] if self.cat_cols else "Aucune")

        def draw():
            for w in list(self.content.winfo_children()):
                if not isinstance(w, tk.Frame) or w.winfo_height() > 50:
                    w.destroy()
            col_x = sel_x.get()
            col_y = sel_y.get()
            cat   = sel_cat.get() if sel_cat.get() != "Aucune" else None
            fig = plt.Figure(figsize=(12, 6.5), facecolor=BG_DARK)
            ax = fig.add_subplot(111)
            build_scatter(ax, self.df, col_x, col_y, cat, self.palette if cat else None)
            fig.tight_layout(pad=2)
            self._embed(fig)
            self.status_var.set(f"Scatter : {col_x} vs {col_y}")

        def ctrl(bar):
            self._col_selector_widget(bar, "Axe X", self.num_cols, sel_x)
            self._col_selector_widget(bar, "Axe Y", self.num_cols, sel_y,
                                      default=1 if len(self.num_cols) > 1 else 0)
            cats_opts = ["Aucune"] + self.cat_cols
            self._col_selector_widget(bar, "Couleur par", cats_opts, sel_cat)
            tk.Button(bar, text="Afficher",
                      font=("DejaVu Sans", 9, "bold"),
                      fg=WHITE, bg=ACCENT, activebackground="#388BFD",
                      activeforeground=WHITE, bd=0, padx=16, pady=4,
                      cursor="hand2", command=draw).pack(side="left", padx=8, pady=10)

        self._ctrl_bar(ctrl)
        draw()

    def _show_heatmap(self):
        if not self._need_data():
            return
        self._clear()
        self._set_header("Heatmap de Correlation",
                         f"Variables numeriques ({min(len(self.num_cols),10)} max affichees)")
        self.update_idletasks()

        fig = plt.Figure(figsize=(9, 7), facecolor=BG_DARK)
        ax = fig.add_subplot(111)
        build_heatmap(ax, self.df, self.num_cols)
        fig.tight_layout(pad=2)
        self._embed(fig)
        self.status_var.set("Heatmap de correlation affichee.")

    def _show_animation(self):
        if not self._need_data():
            return
        self._clear()
        self._set_header("Animation  Courbes", "Trace progressif  |  Export GIF disponible")

        sel_col = tk.StringVar(value=self.num_cols[0])
        sel_cat = tk.StringVar(value=self.cat_cols[0] if self.cat_cols else "Aucune")

        self._anim_obj    = None
        self._anim_running = True
        canvas_holder     = [None]

        def do_draw():
            for w in list(self.content.winfo_children()):
                if not isinstance(w, tk.Frame) or w.winfo_height() > 55:
                    w.destroy()

            col = sel_col.get()
            cat = sel_cat.get() if sel_cat.get() != "Aucune" else None
            pal = self.palette if cat else {}

            fig = plt.Figure(figsize=(13, 6), facecolor=BG_DARK)
            ax  = fig.add_subplot(111)
            style_ax(ax)
            ax.set_title(f"Animation  {col}", fontsize=13, pad=10, color=WHITE)
            ax.set_xlabel("Index", color=FG_DIM)
            ax.set_ylabel(col, color=FG_DIM)
            ax.grid(color=BORDER, linewidth=0.5, alpha=0.6)

            if cat:
                sp_data = {str(c): self.df[self.df[cat] == c][col].dropna().values
                           for c in self.df[cat].unique()}
            else:
                sp_data = {"all": self.df[col].dropna().values}

            max_len = max(len(v) for v in sp_data.values())
            ax.set_xlim(0, max_len)
            all_vals = np.concatenate(list(sp_data.values()))
            ax.set_ylim(all_vals.min() - all_vals.std() * 0.1,
                        all_vals.max() + all_vals.std() * 0.1)

            lns = {}
            for k, v in sp_data.items():
                color = pal.get(k, ACCENT)
                (ln,) = ax.plot([], [], color=color, linewidth=2,
                                label=k if cat else col,
                                marker="o", markersize=2.5)
                lns[k] = ln
            if cat:
                ax.legend(facecolor=BG_WIDGET, edgecolor=BORDER,
                          labelcolor=WHITE, fontsize=9)

            prog = ax.text(0.02, 0.05, "", transform=ax.transAxes,
                           color=FG_DIM, fontsize=9)

            def init():
                for l in lns.values():
                    l.set_data([], [])
                prog.set_text("")
                return list(lns.values()) + [prog]

            def anim_fn(frame):
                for k, l in lns.items():
                    d = sp_data[k]
                    n = min(frame + 1, len(d))
                    l.set_data(np.arange(n), d[:n])
                pct = int((frame + 1) / max_len * 100)
                prog.set_text(f"Progression : {pct}%")
                return list(lns.values()) + [prog]

            ani = animation.FuncAnimation(
                fig, anim_fn, init_func=init,
                frames=max_len, interval=80, blit=True, repeat=True
            )
            self._ani_ref  = ani
            self._anim_obj = ani
            self._anim_running = True
            canvas_holder[0] = self._embed(fig, toolbar=False)
            self.status_var.set(f"Animation : {col}" + (f" par {cat}" if cat else ""))

        def toggle():
            if self._anim_obj is None:
                return
            if self._anim_running:
                self._anim_obj.pause()
                self._anim_running = False
                pause_btn.configure(text="  Reprendre")
            else:
                self._anim_obj.resume()
                self._anim_running = True
                pause_btn.configure(text="  Pause")

        def export_gif():
            self.status_var.set("Export GIF en cours...")
            self.update_idletasks()
            col = sel_col.get()
            cat = sel_cat.get() if sel_cat.get() != "Aucune" else None
            pal = self.palette if cat else {}

            def do_export():
                fig2 = plt.Figure(figsize=(10, 5), facecolor=BG_DARK)
                ax2  = fig2.add_subplot(111)
                style_ax(ax2)
                ax2.set_title(f"Animation  {col}", fontsize=12, color=WHITE)
                ax2.set_xlabel("Index", color=FG_DIM)
                ax2.set_ylabel(col, color=FG_DIM)
                ax2.grid(color=BORDER, linewidth=0.5, alpha=0.6)

                sp_data2 = (
                    {str(c): self.df[self.df[cat] == c][col].dropna().values
                     for c in self.df[cat].unique()}
                    if cat else {"all": self.df[col].dropna().values}
                )
                max_l = max(len(v) for v in sp_data2.values())
                all_v = np.concatenate(list(sp_data2.values()))
                ax2.set_xlim(0, max_l)
                ax2.set_ylim(all_v.min() - all_v.std() * 0.1,
                             all_v.max() + all_v.std() * 0.1)

                lns2 = {}
                for k, v in sp_data2.items():
                    color = pal.get(k, ACCENT)
                    (l,) = ax2.plot([], [], color=color, linewidth=2,
                                    label=k, marker="o", markersize=2)
                    lns2[k] = l
                if cat:
                    ax2.legend(facecolor=BG_WIDGET, edgecolor=BORDER,
                               labelcolor=WHITE, fontsize=9)

                def init2():
                    for l in lns2.values():
                        l.set_data([], [])
                    return list(lns2.values())

                def anim2(frame):
                    for k, l in lns2.items():
                        d = sp_data2[k]
                        n = min(frame + 1, len(d))
                        l.set_data(np.arange(n), d[:n])
                    return list(lns2.values())

                ani2 = animation.FuncAnimation(
                    fig2, anim2, init_func=init2,
                    frames=max_l, interval=80, blit=True
                )
                ani2.save("export_animated.gif", writer="pillow", fps=18, dpi=90)
                plt.close(fig2)
                self.after(0, lambda: self.status_var.set(
                    "GIF exporte : export_animated.gif"))

            threading.Thread(target=do_export, daemon=True).start()

        def ctrl(bar):
            self._col_selector_widget(bar, "Variable", self.num_cols, sel_col)
            cats_opts = ["Aucune"] + self.cat_cols
            self._col_selector_widget(bar, "Grouper par", cats_opts, sel_cat)
            tk.Button(bar, text="Animer",
                      font=("DejaVu Sans", 9, "bold"),
                      fg=WHITE, bg=ACCENT, activebackground="#388BFD",
                      activeforeground=WHITE, bd=0, padx=14, pady=4,
                      cursor="hand2", command=do_draw).pack(side="left", padx=8, pady=10)

        self._ctrl_bar(ctrl)

        ctrl2 = tk.Frame(self.content, bg=BG_PANEL, height=42)
        ctrl2.pack(fill="x")
        ctrl2.pack_propagate(False)

        pause_btn = tk.Button(ctrl2, text="  Pause",
                              font=("DejaVu Sans", 9, "bold"),
                              fg=WHITE, bg=BG_BTN, activebackground=BG_BTN_HOV,
                              activeforeground=WHITE, bd=0, padx=14, pady=4,
                              cursor="hand2", command=toggle)
        pause_btn.pack(side="left", padx=10, pady=5)

        tk.Button(ctrl2, text="  Exporter GIF",
                  font=("DejaVu Sans", 9, "bold"),
                  fg=WHITE, bg="#1A4480", activebackground="#2563EB",
                  activeforeground=WHITE, bd=0, padx=14, pady=4,
                  cursor="hand2", command=export_gif).pack(side="left", padx=4, pady=5)

        do_draw()

    def _show_stats(self):
        if not self._need_data():
            return
        self._clear()
        self._set_header("Statistiques Descriptives",
                         "Moyenne, Mediane, Ecart-type, Quartiles, IQR")

        tabs = ttk.Notebook(self.content)
        tabs.pack(fill="both", expand=True, padx=10, pady=10)

        style = ttk.Style()
        style.theme_use("default")
        style.configure("TNotebook", background=BG_DARK, borderwidth=0)
        style.configure("TNotebook.Tab", background=BG_PANEL, foreground=FG_MAIN,
                        padding=(14, 6), font=("DejaVu Sans", 9))
        style.map("TNotebook.Tab",
                  background=[("selected", ACCENT)],
                  foreground=[("selected", WHITE)])

        tab_global  = tk.Frame(tabs, bg=BG_DARK)
        tab_tableau = tk.Frame(tabs, bg=BG_DARK)
        tab_cats    = tk.Frame(tabs, bg=BG_DARK)
        tabs.add(tab_global,  text="  Global  ")
        tabs.add(tab_tableau, text="  Tableau interactif  ")
        tabs.add(tab_cats,    text="  Par categorie  ")

        txt1 = self._make_text(tab_global)
        lines = ["=" * 60,
                 f"  STATISTIQUES GLOBALES  {os.path.basename(self.filepath)}",
                 "=" * 60]
        for col in self.num_cols:
            s = self.df[col].dropna()
            q1, q3 = s.quantile([0.25, 0.75]).values
            lines += [
                f"\n  {col.replace('_',' ').upper()}  ({len(s)} valeurs non-nulles)",
                f"    Moyenne     : {s.mean():.4f}",
                f"    Mediane     : {s.median():.4f}",
                f"    Ecart-type  : {s.std():.4f}",
                f"    Min         : {s.min():.4f}",
                f"    Max         : {s.max():.4f}",
                f"    Q1  (25%)   : {q1:.4f}",
                f"    Q3  (75%)   : {q3:.4f}",
                f"    IQR         : {q3 - q1:.4f}",
                f"    Nulls       : {self.df[col].isna().sum()}",
            ]
        lines.append("\n" + "=" * 60)
        txt1.insert("end", "\n".join(lines))
        txt1.configure(state="disabled")

        style.configure("Treeview", background=BG_PANEL, foreground=FG_MAIN,
                        fieldbackground=BG_PANEL, rowheight=26,
                        font=("DejaVu Sans", 9))
        style.configure("Treeview.Heading", background=BG_WIDGET, foreground=ACCENT,
                        font=("DejaVu Sans", 9, "bold"), relief="flat")
        style.map("Treeview", background=[("selected", "#1A4480")])

        tcols = ("Variable", "N", "Moyenne", "Mediane", "Ecart-type",
                 "Min", "Max", "Q1", "Q3", "IQR", "Nulls")
        tree = ttk.Treeview(tab_tableau, columns=tcols, show="headings", height=24)
        widths = {"Variable": 130, "N": 60}
        for c in tcols:
            tree.heading(c, text=c)
            tree.column(c, width=widths.get(c, 90), anchor="center")
        for col in self.num_cols:
            s = self.df[col].dropna()
            q1, q3 = s.quantile([0.25, 0.75]).values
            tree.insert("", "end", values=(
                col, len(s),
                f"{s.mean():.4f}", f"{s.median():.4f}", f"{s.std():.4f}",
                f"{s.min():.4f}", f"{s.max():.4f}",
                f"{q1:.4f}", f"{q3:.4f}", f"{q3-q1:.4f}",
                self.df[col].isna().sum()
            ))
        sb = ttk.Scrollbar(tab_tableau, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        tree.pack(fill="both", expand=True)

        txt2 = self._make_text(tab_cats)
        if self.cat_cols:
            lines2 = []
            for cat in self.cat_cols:
                lines2.append(f"\n{'='*60}")
                lines2.append(f"  CATEGORIE : {cat.upper()}")
                lines2.append(f"  Valeurs uniques : {self.df[cat].nunique()}")
                lines2.append("=" * 60)
                for grp in self.df[cat].unique():
                    sub = self.df[self.df[cat] == grp][self.num_cols]
                    lines2.append(f"\n  [{str(grp).upper()}]  ({len(sub)} obs.)")
                    desc = sub.describe().round(4)
                    header = f"  {'Stat':<10}" + "".join(
                        f"{c[:11]:>13}" for c in self.num_cols[:6])
                    lines2.append(header)
                    lines2.append("  " + "-" * max(50, 10 + 13 * min(6, len(self.num_cols))))
                    for row in desc.index:
                        vals = "".join(f"{v:13.4f}" for v in
                                       list(desc.loc[row].values)[:6])
                        lines2.append(f"  {row:<10}{vals}")
            txt2.insert("end", "\n".join(lines2))
        else:
            txt2.insert("end", "\n  Aucune colonne categorielle detectee dans ce fichier.")
        txt2.configure(state="disabled")

        self.status_var.set("Statistiques descriptives affichees.")

    def _show_apercu(self):
        if not self._need_data():
            return
        self._clear()
        self._set_header("Apercu des donnees",
                         f"{len(self.df)} lignes x {len(self.df.columns)} colonnes")

        style = ttk.Style()
        style.configure("Treeview", background=BG_PANEL, foreground=FG_MAIN,
                        fieldbackground=BG_PANEL, rowheight=24,
                        font=("DejaVu Sans", 9))
        style.configure("Treeview.Heading", background=BG_WIDGET, foreground=ACCENT,
                        font=("DejaVu Sans", 9, "bold"), relief="flat")
        style.map("Treeview", background=[("selected", "#1A4480")])

        info_bar = tk.Frame(self.content, bg=BG_PANEL, height=38)
        info_bar.pack(fill="x")
        info_bar.pack_propagate(False)
        info_text = (
            f"  {len(self.df)} lignes  |  "
            f"{len(self.num_cols)} variables numeriques : {', '.join(self.num_cols[:5])}"
            + (" ..." if len(self.num_cols) > 5 else "") +
            (f"  |  Categories : {', '.join(self.cat_cols)}" if self.cat_cols else "")
        )
        tk.Label(info_bar, text=info_text, font=("DejaVu Sans", 9),
                 fg=FG_DIM, bg=BG_PANEL, anchor="w", padx=10).pack(fill="both")

        cols = list(self.df.columns)
        tree = ttk.Treeview(self.content, columns=cols, show="headings",
                            height=30)
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, width=max(80, min(160, len(col) * 11)),
                        anchor="center")

        display = self.df.head(200)
        alt = False
        for _, row in display.iterrows():
            vals = [str(v) if pd.notna(v) else "" for v in row]
            tree.insert("", "end", values=vals,
                        tags=("odd" if alt else "even",))
            alt = not alt

        tree.tag_configure("odd",  background=BG_PANEL)
        tree.tag_configure("even", background=BG_WIDGET)

        sb_y = ttk.Scrollbar(self.content, orient="vertical",   command=tree.yview)
        sb_x = ttk.Scrollbar(self.content, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=sb_y.set, xscrollcommand=sb_x.set)
        sb_y.pack(side="right", fill="y")
        sb_x.pack(side="bottom", fill="x")
        tree.pack(fill="both", expand=True)

        n_shown = min(200, len(self.df))
        self.status_var.set(
            f"Apercu : {n_shown} premieres lignes affichees"
            + (f" sur {len(self.df)}" if len(self.df) > 200 else "") + ".")

    def _make_text(self, parent):
        frame = tk.Frame(parent, bg=BG_DARK)
        frame.pack(fill="both", expand=True)
        txt = tk.Text(frame, bg=BG_PANEL, fg=FG_MAIN,
                      font=("Courier", 10), bd=0, padx=16, pady=12,
                      insertbackground=WHITE)
        sb = ttk.Scrollbar(frame, command=txt.yview)
        txt.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        txt.pack(fill="both", expand=True)
        return txt

    def _col_selector_widget(self, bar, label, choices, var, default=0):
        frame = tk.Frame(bar, bg=BG_PANEL)
        frame.pack(side="left", padx=8, pady=6)
        tk.Label(frame, text=label, font=("DejaVu Sans", 8),
                 fg=FG_DIM, bg=BG_PANEL).pack(anchor="w")
        if not var.get() or var.get() not in choices:
            var.set(choices[min(default, len(choices)-1)] if choices else "")
        cb = ttk.Combobox(frame, textvariable=var, values=choices,
                          state="readonly", width=20,
                          font=("DejaVu Sans", 9))
        cb.pack()

    def _export_png(self):
        if not self._need_data():
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("Tous", "*.*")],
            initialfile="dashboard_export.png",
            title="Exporter le dashboard en PNG"
        )
        if not path:
            return
        self.status_var.set("Export en cours...")
        self.update_idletasks()

        n   = self.num_cols
        cat = self.cat_cols[0] if self.cat_cols else None
        fig = plt.Figure(figsize=(18, 12), facecolor=BG_DARK)
        fig.suptitle(f"Dashboard  {os.path.basename(self.filepath)}",
                     fontsize=18, fontweight="bold", color=WHITE, y=0.99)
        gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.48, wspace=0.40)

        build_histogramme(fig.add_subplot(gs[0, 0]), self.df, n[0], cat, self.palette)
        build_scatter(fig.add_subplot(gs[0, 1]), self.df,
                      n[0], n[1] if len(n) > 1 else n[0], cat, self.palette)
        build_heatmap(fig.add_subplot(gs[1, 0]), self.df, n)
        build_courbe(fig.add_subplot(gs[1, 1]), self.df, n[0], cat, self.palette)

        fig.savefig(path, dpi=150, bbox_inches="tight",
                    facecolor=fig.get_facecolor())
        plt.close(fig)
        self.status_var.set(f"PNG exporte : {os.path.basename(path)}")
        messagebox.showinfo("Export reussi", f"Fichier sauvegarde :\n{path}")


if __name__ == "__main__":
    app = CSVAnalyser()
    app.mainloop()
