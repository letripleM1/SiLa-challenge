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

PALETTE      = {"setosa": "#E63946", "versicolor": "#457B9D", "virginica": "#2A9D8F"}
BG_DARK      = "#0D1117"
BG_PANEL     = "#161B22"
BG_WIDGET    = "#21262D"
BG_BTN       = "#1F2937"
BG_BTN_HOV   = "#2D3748"
BG_BTN_ACT   = "#E63946"
BORDER       = "#30363D"
FG_DIM       = "#8B949E"
FG_MAIN      = "#C9D1D9"
YELLOW       = "#F1FA8C"
WHITE        = "#FFFFFF"
ACCENT       = "#58A6FF"

NUMERIC_COLS = ["sepal_length", "sepal_width", "petal_length", "petal_width"]
COL_LABELS   = ["S. Length", "S. Width", "P. Length", "P. Width"]

_active_ani = None


def load_data(path="iris.csv"):
    if not os.path.exists(path):
        messagebox.showerror("Erreur", f"Fichier introuvable :\n{path}")
        sys.exit(1)
    return pd.read_csv(path)


def style_ax(ax):
    ax.set_facecolor(BG_PANEL)
    for spine in ax.spines.values():
        spine.set_edgecolor(BORDER)
    ax.tick_params(colors=FG_DIM)
    ax.xaxis.label.set_color(FG_DIM)
    ax.yaxis.label.set_color(FG_DIM)
    ax.title.set_color(WHITE)


def build_histogramme(ax, df):
    for sp in df["species"].unique():
        data = df[df["species"] == sp]["sepal_length"]
        ax.hist(data, bins=15, alpha=0.72, label=sp.capitalize(),
                color=PALETTE[sp], edgecolor=WHITE, linewidth=0.35)
        mean_val = data.mean()
        ax.axvline(mean_val, color=PALETTE[sp], linestyle="--", linewidth=1.6, alpha=0.9)
        ax.text(mean_val + 0.06, ax.get_ylim()[1] * 0.88,
                f"u={mean_val:.1f}", color=PALETTE[sp], fontsize=8,
                bbox=dict(facecolor=BG_WIDGET, edgecolor="none", alpha=0.6, pad=1.5))
    ax.set_title("Distribution  Longueur des Sepales", fontsize=13, pad=10)
    ax.set_xlabel("Longueur (cm)")
    ax.set_ylabel("Frequence")
    ax.legend(facecolor=BG_WIDGET, edgecolor=BORDER, labelcolor=WHITE, fontsize=9)
    ax.grid(axis="y", color=BORDER, linewidth=0.5, alpha=0.6)
    style_ax(ax)


def build_scatter(ax, df):
    for sp in df["species"].unique():
        sub = df[df["species"] == sp]
        ax.scatter(sub["sepal_length"], sub["petal_length"],
                   c=PALETTE[sp], label=sp.capitalize(),
                   alpha=0.82, s=58, edgecolors=WHITE, linewidths=0.3)
    x_all = df["sepal_length"].values
    y_all = df["petal_length"].values
    slope, intercept, r, p, _ = stats.linregress(x_all, y_all)
    x_line = np.linspace(x_all.min(), x_all.max(), 300)
    y_line = slope * x_line + intercept
    ax.plot(x_line, y_line, color=YELLOW, linewidth=2,
            label=f"Regression (R2={r**2:.3f})")
    ax.fill_between(x_line, y_line - 0.5, y_line + 0.5, color=YELLOW, alpha=0.07)
    ax.annotate(f"y = {slope:.2f}x + {intercept:.2f}\np = {p:.2e}",
                xy=(0.05, 0.87), xycoords="axes fraction", fontsize=9, color=YELLOW,
                bbox=dict(boxstyle="round,pad=0.35", facecolor=BG_WIDGET,
                          edgecolor=YELLOW, alpha=0.85))
    ax.set_title("Scatter Plot + Regression\nLongueur Petale vs Longueur Sepale",
                 fontsize=13, pad=10)
    ax.set_xlabel("Longueur Sepale (cm)")
    ax.set_ylabel("Longueur Petale (cm)")
    ax.legend(facecolor=BG_WIDGET, edgecolor=BORDER, labelcolor=WHITE, fontsize=9)
    ax.grid(color=BORDER, linewidth=0.5, alpha=0.6)
    style_ax(ax)


def build_heatmap(ax, df):
    corr = df[NUMERIC_COLS].corr()
    sns.heatmap(corr, ax=ax, annot=True, fmt=".2f", cmap="coolwarm",
                linewidths=1, linecolor=BG_DARK,
                xticklabels=COL_LABELS, yticklabels=COL_LABELS,
                annot_kws={"size": 11, "weight": "bold"},
                vmin=-1, vmax=1, cbar_kws={"shrink": 0.82})
    ax.set_title("Heatmap de Correlation", fontsize=13, pad=10, color=WHITE)
    ax.tick_params(colors=FG_DIM, labelsize=9)
    ax.xaxis.label.set_color(FG_DIM)
    ax.yaxis.label.set_color(FG_DIM)
    cbar = ax.collections[0].colorbar
    cbar.ax.tick_params(colors=FG_DIM)
    cbar.outline.set_edgecolor(BORDER)
    ax.set_facecolor(BG_PANEL)


def build_courbe_statique(ax, df):
    for sp in df["species"].unique():
        data = df[df["species"] == sp]["petal_length"].values
        ax.plot(np.arange(len(data)), data, color=PALETTE[sp],
                linewidth=2, label=sp.capitalize(),
                marker="o", markersize=3, alpha=0.85)
    ax.set_title("Evolution  Longueur Petale par Espece", fontsize=13, pad=10)
    ax.set_xlabel("Echantillon (index)")
    ax.set_ylabel("Longueur Petale (cm)")
    ax.legend(facecolor=BG_WIDGET, edgecolor=BORDER, labelcolor=WHITE, fontsize=9)
    ax.grid(color=BORDER, linewidth=0.5, alpha=0.6)
    style_ax(ax)


def stats_text(df):
    lines = []
    lines.append("=" * 60)
    lines.append("     STATISTIQUES DESCRIPTIVES  IRIS DATASET")
    lines.append("=" * 60)
    for col in NUMERIC_COLS:
        q1, q3 = df[col].quantile([0.25, 0.75]).values
        lines.append(f"\n  {col.replace('_', ' ').upper()}")
        lines.append(f"    Moyenne    : {df[col].mean():.4f}")
        lines.append(f"    Mediane    : {df[col].median():.4f}")
        lines.append(f"    Ecart-type : {df[col].std():.4f}")
        lines.append(f"    Min        : {df[col].min():.4f}")
        lines.append(f"    Max        : {df[col].max():.4f}")
        lines.append(f"    Q1  (25%)  : {q1:.4f}")
        lines.append(f"    Q3  (75%)  : {q3:.4f}")
        lines.append(f"    IQR        : {q3 - q1:.4f}")
    lines.append("\n" + "=" * 60)
    lines.append("  RESUME PAR ESPECE")
    lines.append("=" * 60)
    for sp in df["species"].unique():
        sub = df[df["species"] == sp][NUMERIC_COLS]
        lines.append(f"\n  [{sp.upper()}]")
        desc = sub.describe().round(4)
        header = "           " + "  ".join(f"{c:>12}" for c in NUMERIC_COLS)
        lines.append(header)
        for stat_row in desc.index:
            vals = "  ".join(f"{v:12.4f}" for v in desc.loc[stat_row].values)
            lines.append(f"    {stat_row:<8} {vals}")
    lines.append("\n" + "=" * 60)
    return "\n".join(lines)


class IrisDashboard(tk.Tk):
    def __init__(self, df):
        super().__init__()
        self.df = df
        self.title("Iris Dashboard  |  Visualisation Multi-Graphiques")
        self.configure(bg=BG_DARK)
        self.geometry("1280x820")
        self.minsize(1100, 700)
        self._current_btn = None
        self._ani_ref = None
        self._build_ui()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _on_close(self):
        self._ani_ref = None
        self.destroy()

    def _build_ui(self):
        self._build_sidebar()
        self._build_main_area()
        self._build_statusbar()
        self._show_accueil()

    def _build_sidebar(self):
        sidebar = tk.Frame(self, bg=BG_PANEL, width=230)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        logo_frame = tk.Frame(sidebar, bg=BG_PANEL, pady=18)
        logo_frame.pack(fill="x")
        tk.Label(logo_frame, text="IRIS", font=("DejaVu Sans", 26, "bold"),
                 fg=ACCENT, bg=BG_PANEL).pack()
        tk.Label(logo_frame, text="Dashboard", font=("DejaVu Sans", 11),
                 fg=FG_DIM, bg=BG_PANEL).pack()

        sep = tk.Frame(sidebar, bg=BORDER, height=1)
        sep.pack(fill="x", padx=14, pady=4)

        tk.Label(sidebar, text="NAVIGATION", font=("DejaVu Sans", 8, "bold"),
                 fg=FG_DIM, bg=BG_PANEL, anchor="w", padx=18, pady=8).pack(fill="x")

        nav_items = [
            ("Accueil",              "\u2302",  self._show_accueil),
            ("Dashboard complet",    "\u229e",  self._show_dashboard),
            ("Histogramme",          "\u2261",  self._show_histogramme),
            ("Scatter + Regression", "\u25C6",  self._show_scatter),
            ("Heatmap Correlation",  "\u25A6",  self._show_heatmap),
            ("Animation courbes",    "\u25B6",  self._show_animation),
            ("Statistiques",         "\u03A3",  self._show_stats),
        ]

        self._nav_btns = []
        for label, icon, cmd in nav_items:
            btn = self._nav_btn(sidebar, icon, label, cmd)
            self._nav_btns.append(btn)

        sep2 = tk.Frame(sidebar, bg=BORDER, height=1)
        sep2.pack(fill="x", padx=14, pady=10)

        tk.Label(sidebar, text="DATASET", font=("DejaVu Sans", 8, "bold"),
                 fg=FG_DIM, bg=BG_PANEL, anchor="w", padx=18, pady=4).pack(fill="x")

        info_lines = [
            ("Observations", "150"),
            ("Variables",    "4"),
            ("Especes",      "3"),
        ]
        for lbl, val in info_lines:
            row = tk.Frame(sidebar, bg=BG_PANEL)
            row.pack(fill="x", padx=18, pady=2)
            tk.Label(row, text=lbl, font=("DejaVu Sans", 9), fg=FG_DIM,
                     bg=BG_PANEL, anchor="w").pack(side="left")
            tk.Label(row, text=val, font=("DejaVu Sans", 9, "bold"), fg=ACCENT,
                     bg=BG_PANEL, anchor="e").pack(side="right")

        legend_frame = tk.Frame(sidebar, bg=BG_PANEL)
        legend_frame.pack(fill="x", padx=18, pady=(14, 4))
        tk.Label(legend_frame, text="ESPECES", font=("DejaVu Sans", 8, "bold"),
                 fg=FG_DIM, bg=BG_PANEL, anchor="w").pack(fill="x")
        for sp, color in PALETTE.items():
            row = tk.Frame(legend_frame, bg=BG_PANEL)
            row.pack(fill="x", pady=2)
            dot = tk.Canvas(row, width=12, height=12, bg=BG_PANEL,
                            highlightthickness=0)
            dot.pack(side="left", padx=(0, 6))
            dot.create_oval(1, 1, 11, 11, fill=color, outline="")
            tk.Label(row, text=sp.capitalize(), font=("DejaVu Sans", 9),
                     fg=FG_MAIN, bg=BG_PANEL).pack(side="left")

        save_btn = tk.Button(sidebar, text="Exporter PNG",
                             font=("DejaVu Sans", 9, "bold"),
                             fg=WHITE, bg="#1A4480", activebackground="#2563EB",
                             activeforeground=WHITE, bd=0, pady=7, cursor="hand2",
                             command=self._export_png)
        save_btn.pack(side="bottom", fill="x", padx=14, pady=(8, 16))

    def _nav_btn(self, parent, icon, label, cmd):
        frame = tk.Frame(parent, bg=BG_PANEL, cursor="hand2")
        frame.pack(fill="x", padx=10, pady=2)

        icon_lbl = tk.Label(frame, text=icon, font=("DejaVu Sans", 13),
                            fg=FG_DIM, bg=BG_PANEL, width=3, anchor="center")
        icon_lbl.pack(side="left", padx=(6, 2), pady=6)

        text_lbl = tk.Label(frame, text=label, font=("DejaVu Sans", 10),
                            fg=FG_MAIN, bg=BG_PANEL, anchor="w")
        text_lbl.pack(side="left", fill="x", expand=True)

        def on_enter(e):
            if frame != self._current_btn:
                frame.configure(bg=BG_BTN_HOV)
                icon_lbl.configure(bg=BG_BTN_HOV)
                text_lbl.configure(bg=BG_BTN_HOV)

        def on_leave(e):
            if frame != self._current_btn:
                frame.configure(bg=BG_PANEL)
                icon_lbl.configure(bg=BG_PANEL)
                text_lbl.configure(bg=BG_PANEL)

        def on_click(e):
            self._set_active_btn(frame, icon_lbl, text_lbl)
            cmd()

        for widget in (frame, icon_lbl, text_lbl):
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
            widget.bind("<Button-1>", on_click)

        frame._icon_lbl = icon_lbl
        frame._text_lbl = text_lbl
        return frame

    def _set_active_btn(self, frame, icon_lbl, text_lbl):
        if self._current_btn:
            prev = self._current_btn
            prev.configure(bg=BG_PANEL)
            prev._icon_lbl.configure(bg=BG_PANEL, fg=FG_DIM)
            prev._text_lbl.configure(bg=BG_PANEL, fg=FG_MAIN)
        self._current_btn = frame
        frame.configure(bg=BG_BTN_ACT)
        icon_lbl.configure(bg=BG_BTN_ACT, fg=WHITE)
        text_lbl.configure(bg=BG_BTN_ACT, fg=WHITE)

    def _build_main_area(self):
        self.main_frame = tk.Frame(self, bg=BG_DARK)
        self.main_frame.pack(side="left", fill="both", expand=True)

        self.header_frame = tk.Frame(self.main_frame, bg=BG_PANEL, height=52)
        self.header_frame.pack(fill="x")
        self.header_frame.pack_propagate(False)

        self.page_title = tk.Label(self.header_frame, text="Accueil",
                                   font=("DejaVu Sans", 15, "bold"),
                                   fg=WHITE, bg=BG_PANEL, padx=22)
        self.page_title.pack(side="left", fill="y")

        self.page_subtitle = tk.Label(self.header_frame, text="",
                                      font=("DejaVu Sans", 9),
                                      fg=FG_DIM, bg=BG_PANEL, padx=6)
        self.page_subtitle.pack(side="left", fill="y")

        self.content_frame = tk.Frame(self.main_frame, bg=BG_DARK)
        self.content_frame.pack(fill="both", expand=True)

    def _build_statusbar(self):
        bar = tk.Frame(self.main_frame, bg=BG_PANEL, height=26)
        bar.pack(side="bottom", fill="x")
        bar.pack_propagate(False)
        self.status_var = tk.StringVar(value="Pret.")
        tk.Label(bar, textvariable=self.status_var, font=("DejaVu Sans", 8),
                 fg=FG_DIM, bg=BG_PANEL, padx=14, anchor="w").pack(side="left", fill="y")
        tk.Label(bar, text="Iris Dataset  Fisher 1936",
                 font=("DejaVu Sans", 8), fg=BORDER, bg=BG_PANEL,
                 padx=14, anchor="e").pack(side="right", fill="y")

    def _clear_content(self):
        self._ani_ref = None
        for w in self.content_frame.winfo_children():
            w.destroy()

    def _set_header(self, title, subtitle=""):
        self.page_title.configure(text=title)
        self.page_subtitle.configure(text=subtitle)

    def _embed_figure(self, fig, toolbar=True):
        canvas = FigureCanvasTkAgg(fig, master=self.content_frame)
        canvas.draw()
        if toolbar:
            tb_frame = tk.Frame(self.content_frame, bg=BG_DARK)
            tb_frame.pack(fill="x", padx=4)
            tb = NavigationToolbar2Tk(canvas, tb_frame)
            tb.configure(background=BG_DARK)
            for child in tb.winfo_children():
                try:
                    child.configure(background=BG_DARK)
                except Exception:
                    pass
            tb.update()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        return canvas

    def _show_accueil(self):
        self._clear_content()
        self._set_header("Accueil", "Bienvenue dans Iris Dashboard")
        self.status_var.set("Page : Accueil")

        center = tk.Frame(self.content_frame, bg=BG_DARK)
        center.pack(expand=True)

        tk.Label(center, text="Iris Dashboard", font=("DejaVu Sans", 30, "bold"),
                 fg=ACCENT, bg=BG_DARK).pack(pady=(40, 6))
        tk.Label(center, text="Visualisation Multi-Graphiques  |  Dataset Fisher 1936",
                 font=("DejaVu Sans", 13), fg=FG_DIM, bg=BG_DARK).pack(pady=(0, 32))

        cards = [
            ("150", "Observations"),
            ("4",   "Variables numeriques"),
            ("3",   "Especes"),
            ("5",   "Graphiques disponibles"),
        ]
        card_row = tk.Frame(center, bg=BG_DARK)
        card_row.pack(pady=10)
        for val, lbl in cards:
            card = tk.Frame(card_row, bg=BG_PANEL, padx=28, pady=18,
                            highlightbackground=BORDER, highlightthickness=1)
            card.pack(side="left", padx=10)
            tk.Label(card, text=val, font=("DejaVu Sans", 28, "bold"),
                     fg=ACCENT, bg=BG_PANEL).pack()
            tk.Label(card, text=lbl, font=("DejaVu Sans", 9),
                     fg=FG_DIM, bg=BG_PANEL).pack()

        tk.Label(center, text="Utilisez le menu lateral pour naviguer entre les visualisations.",
                 font=("DejaVu Sans", 10), fg=FG_DIM, bg=BG_DARK).pack(pady=30)

        species_row = tk.Frame(center, bg=BG_DARK)
        species_row.pack()
        for sp, color in PALETTE.items():
            sp_frame = tk.Frame(species_row, bg=BG_PANEL, padx=18, pady=10,
                                highlightbackground=color, highlightthickness=2)
            sp_frame.pack(side="left", padx=8)
            dot = tk.Canvas(sp_frame, width=14, height=14, bg=BG_PANEL,
                            highlightthickness=0)
            dot.pack()
            dot.create_oval(1, 1, 13, 13, fill=color, outline="")
            tk.Label(sp_frame, text=sp.capitalize(), font=("DejaVu Sans", 10, "bold"),
                     fg=WHITE, bg=BG_PANEL).pack()
            n = len(self.df[self.df["species"] == sp])
            tk.Label(sp_frame, text=f"{n} obs.", font=("DejaVu Sans", 8),
                     fg=FG_DIM, bg=BG_PANEL).pack()

    def _show_dashboard(self):
        self._clear_content()
        self._set_header("Dashboard complet", "4 graphiques en un seul affichage")
        self.status_var.set("Rendu en cours...")
        self.update_idletasks()

        fig = plt.Figure(figsize=(15, 10), facecolor=BG_DARK)
        fig.suptitle("Tableau de Bord  Iris Dataset",
                     fontsize=20, fontweight="bold", color=WHITE, y=0.99)
        gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.48, wspace=0.38)

        build_histogramme(fig.add_subplot(gs[0, 0]), self.df)
        build_scatter(fig.add_subplot(gs[0, 1]), self.df)
        build_heatmap(fig.add_subplot(gs[1, 0]), self.df)
        build_courbe_statique(fig.add_subplot(gs[1, 1]), self.df)

        self._embed_figure(fig)
        self.status_var.set("Dashboard complet affiche. Utilisez la barre d'outils pour zoomer/exporter.")

    def _show_histogramme(self):
        self._clear_content()
        self._set_header("Histogramme", "Distribution de la longueur des sepales par espece")
        self.status_var.set("Rendu histogramme...")
        self.update_idletasks()

        fig = plt.Figure(figsize=(11, 6), facecolor=BG_DARK)
        ax = fig.add_subplot(111)
        build_histogramme(ax, self.df)
        fig.tight_layout(pad=2)
        self._embed_figure(fig)
        self.status_var.set("Histogramme affiche.")

    def _show_scatter(self):
        self._clear_content()
        self._set_header("Scatter Plot + Regression", "Longueur Petale vs Longueur Sepale")
        self.status_var.set("Rendu scatter plot...")
        self.update_idletasks()

        fig = plt.Figure(figsize=(11, 6), facecolor=BG_DARK)
        ax = fig.add_subplot(111)
        build_scatter(ax, self.df)
        fig.tight_layout(pad=2)
        self._embed_figure(fig)
        self.status_var.set("Scatter plot affiche. R2 et p-value calcules sur l'ensemble des donnees.")

    def _show_heatmap(self):
        self._clear_content()
        self._set_header("Heatmap de Correlation", "Matrice de correlation de Pearson (4 variables)")
        self.status_var.set("Rendu heatmap...")
        self.update_idletasks()

        fig = plt.Figure(figsize=(8, 6), facecolor=BG_DARK)
        ax = fig.add_subplot(111)
        build_heatmap(ax, self.df)
        fig.tight_layout(pad=2)
        self._embed_figure(fig)
        self.status_var.set("Heatmap de correlation affichee.")

    def _show_animation(self):
        self._clear_content()
        self._set_header("Animation  Courbes Petales", "Trace progressif par espece  |  Export GIF disponible")
        self.status_var.set("Preparation de l'animation...")
        self.update_idletasks()

        ctrl_bar = tk.Frame(self.content_frame, bg=BG_PANEL, height=44)
        ctrl_bar.pack(fill="x")
        ctrl_bar.pack_propagate(False)

        self._anim_running = True
        self._anim_obj = None

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

            def do_export():
                fig2 = plt.Figure(figsize=(10, 5), facecolor=BG_DARK)
                ax2 = fig2.add_subplot(111)
                style_ax(ax2)
                ax2.set_title("Animation  Longueur Petale par Espece",
                              fontsize=13, pad=10, color=WHITE)
                ax2.set_xlabel("Echantillon (index)", color=FG_DIM)
                ax2.set_ylabel("Longueur Petale (cm)", color=FG_DIM)
                ax2.grid(color=BORDER, linewidth=0.5, alpha=0.6)

                sp_data = {sp: self.df[self.df["species"] == sp]["petal_length"].values
                           for sp in self.df["species"].unique()}
                max_l = max(len(v) for v in sp_data.values())
                ax2.set_xlim(0, max_l)
                ax2.set_ylim(min(v.min() for v in sp_data.values()) - 0.3,
                             max(v.max() for v in sp_data.values()) + 0.3)

                ln = {}
                for sp in sp_data:
                    (l,) = ax2.plot([], [], color=PALETTE[sp], linewidth=2,
                                    label=sp.capitalize(), marker="o", markersize=3)
                    ln[sp] = l
                ax2.legend(facecolor=BG_WIDGET, edgecolor=BORDER,
                           labelcolor=WHITE, fontsize=9)

                def init2():
                    for l in ln.values():
                        l.set_data([], [])
                    return list(ln.values())

                def anim2(frame):
                    for sp, l in ln.items():
                        d = sp_data[sp]
                        n = min(frame + 1, len(d))
                        l.set_data(np.arange(n), d[:n])
                    return list(ln.values())

                a = animation.FuncAnimation(fig2, anim2, init_func=init2,
                                            frames=max_l, interval=80, blit=True)
                a.save("iris_animated.gif", writer="pillow", fps=18, dpi=90)
                plt.close(fig2)
                self.after(0, lambda: self.status_var.set(
                    "GIF exporte : iris_animated.gif"))

            threading.Thread(target=do_export, daemon=True).start()

        pause_btn = tk.Button(ctrl_bar, text="  Pause",
                              font=("DejaVu Sans", 9, "bold"),
                              fg=WHITE, bg=BG_BTN, activebackground=BG_BTN_HOV,
                              activeforeground=WHITE, bd=0, padx=14, cursor="hand2",
                              command=toggle)
        pause_btn.pack(side="left", padx=10, pady=6)

        gif_btn = tk.Button(ctrl_bar, text="  Exporter GIF",
                            font=("DejaVu Sans", 9, "bold"),
                            fg=WHITE, bg="#1A4480", activebackground="#2563EB",
                            activeforeground=WHITE, bd=0, padx=14, cursor="hand2",
                            command=export_gif)
        gif_btn.pack(side="left", padx=4, pady=6)

        fig = plt.Figure(figsize=(13, 6), facecolor=BG_DARK)
        ax = fig.add_subplot(111)
        style_ax(ax)
        ax.set_title("Animation  Longueur Petale par Espece",
                     fontsize=13, pad=10, color=WHITE)
        ax.set_xlabel("Echantillon (index)", color=FG_DIM)
        ax.set_ylabel("Longueur Petale (cm)", color=FG_DIM)
        ax.grid(color=BORDER, linewidth=0.5, alpha=0.6)

        sp_data = {sp: self.df[self.df["species"] == sp]["petal_length"].values
                   for sp in self.df["species"].unique()}
        max_len = max(len(v) for v in sp_data.values())
        all_min = min(v.min() for v in sp_data.values())
        all_max = max(v.max() for v in sp_data.values())
        ax.set_xlim(0, max_len)
        ax.set_ylim(all_min - 0.3, all_max + 0.3)

        lines = {}
        for sp in sp_data:
            (line,) = ax.plot([], [], color=PALETTE[sp], linewidth=2,
                              label=sp.capitalize(), marker="o", markersize=3)
            lines[sp] = line

        prog_txt = ax.text(0.02, 0.05, "", transform=ax.transAxes,
                           color=FG_DIM, fontsize=9)
        ax.legend(facecolor=BG_WIDGET, edgecolor=BORDER, labelcolor=WHITE, fontsize=10)

        def init():
            for l in lines.values():
                l.set_data([], [])
            prog_txt.set_text("")
            return list(lines.values()) + [prog_txt]

        def animate(frame):
            for sp, l in lines.items():
                d = sp_data[sp]
                n = min(frame + 1, len(d))
                l.set_data(np.arange(n), d[:n])
            pct = int((frame + 1) / max_len * 100)
            prog_txt.set_text(f"Progression : {pct}%")
            return list(lines.values()) + [prog_txt]

        canvas = self._embed_figure(fig, toolbar=False)
        ani = animation.FuncAnimation(fig, animate, init_func=init,
                                      frames=max_len, interval=80,
                                      blit=True, repeat=True)
        self._ani_ref = ani
        self._anim_obj = ani
        canvas.draw()
        self.status_var.set("Animation en cours. Utilisez Pause pour stopper.")

    def _show_stats(self):
        self._clear_content()
        self._set_header("Statistiques Descriptives",
                         "Moyenne, Mediane, Ecart-type, Quartiles, IQR")
        self.status_var.set("Affichage des statistiques.")

        tabs = ttk.Notebook(self.content_frame)
        tabs.pack(fill="both", expand=True, padx=10, pady=10)

        style = ttk.Style()
        style.theme_use("default")
        style.configure("TNotebook", background=BG_DARK, borderwidth=0)
        style.configure("TNotebook.Tab", background=BG_PANEL, foreground=FG_MAIN,
                        padding=(14, 6), font=("DejaVu Sans", 9))
        style.map("TNotebook.Tab", background=[("selected", ACCENT)],
                  foreground=[("selected", WHITE)])

        tab_global = tk.Frame(tabs, bg=BG_DARK)
        tab_especes = tk.Frame(tabs, bg=BG_DARK)
        tab_tableau = tk.Frame(tabs, bg=BG_DARK)
        tabs.add(tab_global,  text="  Global  ")
        tabs.add(tab_especes, text="  Par espece  ")
        tabs.add(tab_tableau, text="  Tableau recapitulatif  ")

        text_global = tk.Text(tab_global, bg=BG_PANEL, fg=FG_MAIN,
                              font=("Courier", 10), bd=0, padx=16, pady=12,
                              insertbackground=WHITE)
        sb1 = ttk.Scrollbar(tab_global, command=text_global.yview)
        text_global.configure(yscrollcommand=sb1.set)
        sb1.pack(side="right", fill="y")
        text_global.pack(fill="both", expand=True)

        content_global = []
        content_global.append("=" * 58)
        content_global.append("     STATISTIQUES GLOBALES — IRIS DATASET")
        content_global.append("=" * 58)
        for col in NUMERIC_COLS:
            q1, q3 = self.df[col].quantile([0.25, 0.75]).values
            content_global.append(f"\n  {col.replace('_', ' ').upper()}")
            content_global.append(f"    Moyenne     : {self.df[col].mean():.4f}")
            content_global.append(f"    Mediane     : {self.df[col].median():.4f}")
            content_global.append(f"    Ecart-type  : {self.df[col].std():.4f}")
            content_global.append(f"    Min         : {self.df[col].min():.4f}")
            content_global.append(f"    Max         : {self.df[col].max():.4f}")
            content_global.append(f"    Q1  (25%)   : {q1:.4f}")
            content_global.append(f"    Q3  (75%)   : {q3:.4f}")
            content_global.append(f"    IQR         : {q3 - q1:.4f}")
        content_global.append("\n" + "=" * 58)
        text_global.insert("end", "\n".join(content_global))
        text_global.configure(state="disabled")

        text_esp = tk.Text(tab_especes, bg=BG_PANEL, fg=FG_MAIN,
                           font=("Courier", 10), bd=0, padx=16, pady=12,
                           insertbackground=WHITE)
        sb2 = ttk.Scrollbar(tab_especes, command=text_esp.yview)
        text_esp.configure(yscrollcommand=sb2.set)
        sb2.pack(side="right", fill="y")
        text_esp.pack(fill="both", expand=True)

        content_esp = []
        for sp in self.df["species"].unique():
            sub = self.df[self.df["species"] == sp][NUMERIC_COLS]
            content_esp.append(f"\n  [{sp.upper()}]  ({len(sub)} observations)")
            content_esp.append("  " + "-" * 54)
            desc = sub.describe().round(4)
            header = f"  {'Stat':<10}" + "".join(f"{c:>14}" for c in NUMERIC_COLS)
            content_esp.append(header)
            content_esp.append("  " + "-" * 54)
            for row in desc.index:
                vals = "".join(f"{v:14.4f}" for v in desc.loc[row].values)
                content_esp.append(f"  {row:<10}{vals}")
        text_esp.insert("end", "\n".join(content_esp))
        text_esp.configure(state="disabled")

        tree_frame = tk.Frame(tab_tableau, bg=BG_DARK)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

        cols = ("Espece", "Variable", "Moyenne", "Mediane", "Ecart-type",
                "Min", "Max", "Q1", "Q3", "IQR")
        tree = ttk.Treeview(tree_frame, columns=cols, show="headings", height=20)

        style.configure("Treeview", background=BG_PANEL, foreground=FG_MAIN,
                        fieldbackground=BG_PANEL, rowheight=26,
                        font=("DejaVu Sans", 9))
        style.configure("Treeview.Heading", background=BG_WIDGET, foreground=ACCENT,
                        font=("DejaVu Sans", 9, "bold"), relief="flat")
        style.map("Treeview", background=[("selected", "#1A4480")])

        for col in cols:
            w = 100 if col not in ("Espece", "Variable") else 90
            tree.heading(col, text=col)
            tree.column(col, width=w, anchor="center")

        row_colors = {
            "setosa": "#1A1F2E",
            "versicolor": "#1A2430",
            "virginica": "#1A2820",
        }
        for sp in self.df["species"].unique():
            sub = self.df[self.df["species"] == sp]
            for var in NUMERIC_COLS:
                q1, q3 = sub[var].quantile([0.25, 0.75]).values
                tree.insert("", "end", values=(
                    sp.capitalize(),
                    var.replace("_", " "),
                    f"{sub[var].mean():.4f}",
                    f"{sub[var].median():.4f}",
                    f"{sub[var].std():.4f}",
                    f"{sub[var].min():.4f}",
                    f"{sub[var].max():.4f}",
                    f"{q1:.4f}",
                    f"{q3:.4f}",
                    f"{q3 - q1:.4f}",
                ), tags=(sp,))
            tree.tag_configure(sp, background=row_colors.get(sp, BG_PANEL))

        sb_tree = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sb_tree.set)
        sb_tree.pack(side="right", fill="y")
        tree.pack(fill="both", expand=True)

    def _export_png(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("Tous", "*.*")],
            initialfile="iris_dashboard.png",
            title="Exporter le dashboard en PNG",
        )
        if not path:
            return
        self.status_var.set("Export en cours...")
        self.update_idletasks()

        fig = plt.Figure(figsize=(18, 12), facecolor=BG_DARK)
        fig.suptitle("Tableau de Bord  Iris Dataset",
                     fontsize=20, fontweight="bold", color=WHITE, y=0.99)
        gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.48, wspace=0.38)
        build_histogramme(fig.add_subplot(gs[0, 0]), self.df)
        build_scatter(fig.add_subplot(gs[0, 1]), self.df)
        build_heatmap(fig.add_subplot(gs[1, 0]), self.df)
        build_courbe_statique(fig.add_subplot(gs[1, 1]), self.df)
        fig.savefig(path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
        plt.close(fig)
        self.status_var.set(f"Export PNG : {os.path.basename(path)}")
        messagebox.showinfo("Export reussi", f"Fichier sauvegarde :\n{path}")


if __name__ == "__main__":
    df = load_data("iris.csv")
    app = IrisDashboard(df)
    app.mainloop()
