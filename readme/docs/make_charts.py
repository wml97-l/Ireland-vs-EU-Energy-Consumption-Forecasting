"""
Build the README insight charts and print the headline figures.

    pip install pandas numpy matplotlib statsmodels vaderSentiment scikit-learn
    python docs/make_charts.py

Writes light and dark PNGs to docs/charts/.
"""
import re
import warnings
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mt
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
from statsmodels.tsa.arima.model import ARIMA
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "charts"
OUT.mkdir(parents=True, exist_ok=True)

THEMES = {
    "light": dict(bg="#ffffff", ink="#1f2328", ink2="#59636e", grid="#d8dee4",
                  main="#2a78d6", accent="#eb6834", muted="#b7c0ca", band="#2a78d6"),
    "dark": dict(bg="#0d1117", ink="#f0f6fc", ink2="#9198a1", grid="#30363d",
                 main="#3987e5", accent="#d95926", muted="#4a535e", band="#3987e5"),
}


def style(ax, t, grid_axis="y"):
    ax.set_facecolor(t["bg"])
    for s in ["top", "right", "left"]:
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(t["grid"])
    ax.tick_params(colors=t["ink2"], length=0, labelsize=10.5)
    ax.grid(axis=grid_axis, color=t["grid"], linewidth=0.8)
    ax.set_axisbelow(True)


def heading(fig, t, head, sub):
    fig.text(0.02, 0.965, head, fontsize=15, fontweight="bold", color=t["ink"], va="top")
    fig.text(0.02, 0.885, sub, fontsize=11, color=t["ink2"], va="top")


def endlabel(ax, t, x, y, text, color, dy=0):
    ax.annotate(text, (x, y), xytext=(8, dy), textcoords="offset points", va="center",
                fontsize=10.5, fontweight="bold", color=color)


def save(fig, name, mode):
    fig.savefig(OUT / f"{name}-{mode}.png", dpi=200, facecolor=fig.get_facecolor())
    plt.close(fig)


def load():
    d = pd.read_csv(ROOT / "eu_merged (1).csv").dropna()
    ie = d[d["Country Name"] == "Ireland"].set_index("Year").sort_index()
    eu = (d[(d["Country Name"] != "Ireland") & (d.Year >= 1990)]
          .groupby("Year")[["Energy use", "Electric Power Consumption"]].mean())
    return d, ie, eu


def chart_trends(ie, eu, t, mode):
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.2), facecolor=t["bg"])
    fig.subplots_adjust(left=0.07, right=0.9, top=0.72, bottom=0.1, wspace=0.42)
    ie90 = ie[ie.index >= 1990]
    for ax, col, title, unit in [
        (axes[0], "Energy use", "Energy use", "kg of oil equivalent per person"),
        (axes[1], "Electric Power Consumption", "Electricity use", "kWh per person"),
    ]:
        ax.plot(eu.index, eu[col], color=t["muted"], linewidth=2)
        ax.plot(ie90.index, ie90[col], color=t["main"], linewidth=2)
        a, b = ie90[col].iloc[-1], eu[col].iloc[-1]
        endlabel(ax, t, ie90.index[-1], a, "Ireland", t["main"], dy=-9 if a < b else 9)
        endlabel(ax, t, eu.index[-1], b, "EU avg", t["ink2"], dy=9 if a < b else -9)
        pk = ie90[col].idxmax()
        ax.plot([pk], [ie90[col].max()], "o", ms=8, color=t["main"], mec=t["bg"], mew=2, zorder=5)
        below = col == "Electric Power Consumption"
        if below:
            ax.annotate(f"Ireland peak {pk}", (pk, ie90[col].max()), xytext=(14, -62), textcoords="offset points",
                        ha="left", fontsize=10, color=t["ink"],
                        arrowprops=dict(arrowstyle="-", color=t["ink2"], linewidth=0.8, shrinkA=2, shrinkB=5))
        else:
            ax.annotate(f"Ireland peak {pk}", (pk, ie90[col].max()), xytext=(0, 10), textcoords="offset points",
                        ha="center", fontsize=10, color=t["ink"])
        ax.set_title(f"{title} ({unit})", loc="left", color=t["ink"], fontsize=11.5, fontweight="bold", pad=10)
        ax.yaxis.set_major_formatter(mt.FuncFormatter(lambda v, _: f"{v:,.0f}"))
        lo = min(ie90[col].min(), eu[col].min())
        ax.set_ylim(lo * 0.85, max(ie90[col].max(), eu[col].max()) * 1.12)
        style(ax, t)
    drop = ie["Energy use"].iloc[-1] / ie["Energy use"].max() - 1
    heading(fig, t, f"Ireland's energy use peaked in {ie['Energy use'].idxmax()} and has fallen {abs(drop):.0%} since",
            "Per-capita energy and electricity use, Ireland vs average of the other 26 EU countries, 1990 to 2022")
    save(fig, "ireland-vs-eu-trends", mode)
    return drop


def chart_relationship(d, ie, t, mode):
    fig, ax = plt.subplots(figsize=(10, 4.6), facecolor=t["bg"])
    fig.subplots_adjust(left=0.09, right=0.97, top=0.78, bottom=0.13)
    other = d[d["Country Name"] != "Ireland"]
    ax.scatter(other["Energy use"], other["Electric Power Consumption"], s=10, color=t["muted"], alpha=0.7,
               linewidths=0, label="Other EU countries (each dot = one country-year)")
    ax.scatter(ie["Energy use"], ie["Electric Power Consumption"], s=26, color=t["main"],
               edgecolors=t["bg"], linewidths=0.8, label="Ireland, 1960 to 2022", zorder=4)
    r_all = d["Energy use"].corr(d["Electric Power Consumption"])
    r_ie = ie["Energy use"].corr(ie["Electric Power Consumption"])
    ax.set_xlabel("Energy use (kg of oil equivalent per person)", color=t["ink2"], fontsize=10.5)
    ax.set_ylabel("Electricity use (kWh per person)", color=t["ink2"], fontsize=10.5)
    for axis in (ax.xaxis, ax.yaxis):
        axis.set_major_formatter(mt.FuncFormatter(lambda v, _: f"{v:,.0f}"))
    leg = ax.legend(frameon=False, loc="upper left", fontsize=10)
    for txt in leg.get_texts():
        txt.set_color(t["ink"])
    style(ax, t, grid_axis="both")
    heading(fig, t, f"More energy use goes with more electricity use (r = {r_all:.2f} across the EU, {r_ie:.2f} in Ireland)",
            "Per-capita energy use vs electricity use, 27 EU countries, 1960 to 2022")
    save(fig, "energy-vs-electricity", mode)
    return r_all, r_ie


def chart_forecast(ie, t, mode):
    ts = ie["Energy use"].copy()
    ts.index = pd.to_datetime(ts.index.astype(str))
    res = ARIMA(ts, order=(1, 1, 1)).fit()
    fc = res.get_forecast(5)
    mean, ci = fc.predicted_mean, fc.conf_int()
    years = mean.index.year

    fig, ax = plt.subplots(figsize=(10, 4.3), facecolor=t["bg"])
    fig.subplots_adjust(left=0.08, right=0.9, top=0.77, bottom=0.1)
    ax.plot(ie.index, ie["Energy use"], color=t["main"], linewidth=2)
    xs = [ie.index[-1]] + list(years)
    ys = [ie["Energy use"].iloc[-1]] + list(mean.values)
    ax.fill_between(years, ci.iloc[:, 0], ci.iloc[:, 1], color=t["band"], alpha=0.18, linewidth=0)
    ax.plot(xs, ys, color=t["accent"], linewidth=2, linestyle=(0, (4, 3)))
    endlabel(ax, t, ie.index[-1], ie["Energy use"].iloc[-1], "", t["main"])
    ax.annotate(f"Forecast {years[-1]}: {mean.iloc[-1]:,.0f}", (years[-1], mean.iloc[-1]), xytext=(8, 0),
                textcoords="offset points", va="center", fontsize=10.5, fontweight="bold", color=t["accent"])
    ax.annotate("95% interval", (years[-1], ci.iloc[-1, 1]), xytext=(8, 0), textcoords="offset points",
                va="center", fontsize=10, color=t["ink2"])
    ax.annotate(f"Actual (peak {ie['Energy use'].max():,.0f} in {ie['Energy use'].idxmax()})",
                (ie["Energy use"].idxmax(), ie["Energy use"].max()), xytext=(-10, 10), textcoords="offset points",
                ha="right", fontsize=10.5, fontweight="bold", color=t["main"])
    ax.yaxis.set_major_formatter(mt.FuncFormatter(lambda v, _: f"{v:,.0f}"))
    ax.set_ylim(1000, 4100)
    ax.set_xlim(1958, 2033)
    style(ax, t)
    heading(fig, t, f"ARIMA(1,1,1) expects Ireland's energy use to keep edging down, to about {mean.iloc[-1]:,.0f} by {years[-1]}",
            "Ireland energy use per person (kg of oil equivalent), actual 1960 to 2022 and 5-year forecast")
    save(fig, "arima-forecast", mode)
    return mean, ci


def chart_sentiment(t, mode, shares):
    order = ["Positive", "Neutral", "Negative"]
    vals = [shares[k] for k in order]
    cols = [t["main"], t["muted"], t["accent"]]
    fig, ax = plt.subplots(figsize=(10, 3.2), facecolor=t["bg"])
    fig.subplots_adjust(left=0.12, right=0.95, top=0.66, bottom=0.12)
    ax.barh(order[::-1], [v * 100 for v in vals[::-1]], color=cols[::-1], height=0.56)
    for i, v in enumerate(vals[::-1]):
        ax.annotate(f"{v:.0%}", (v * 100, i), xytext=(6, 0), textcoords="offset points", va="center",
                    fontsize=11, fontweight="bold", color=t["ink"])
    ax.set_xlim(0, 100)
    ax.xaxis.set_major_formatter(mt.PercentFormatter())
    ax.tick_params(axis="y", colors=t["ink"], labelsize=11)
    style(ax, t, grid_axis="x")
    heading(fig, t, f"About two-thirds of Reddit energy headlines read as positive",
            "VADER sentiment of 412 energy-related Reddit post titles, March to May 2025")
    save(fig, "reddit-sentiment", mode)


def sentiment():
    p = pd.read_csv(ROOT / "energy_posts.csv")
    clean = (p["Post Title"].astype(str).apply(lambda x: re.sub(r"[^\w\s']", "", x)).str.lower()
             .apply(lambda x: " ".join(w for w in x.split() if w not in ENGLISH_STOP_WORDS)))
    a = SentimentIntensityAnalyzer()
    comp = clean.apply(lambda x: a.polarity_scores(x)["compound"])
    lab = np.where(comp >= 0.05, "Positive", np.where(comp <= -0.05, "Negative", "Neutral"))
    return pd.Series(lab).value_counts(normalize=True).to_dict(), comp.mean(), len(p)


if __name__ == "__main__":
    d, ie, eu = load()
    shares, mean_comp, n_posts = sentiment()
    for mode, t in THEMES.items():
        drop = chart_trends(ie, eu, t, mode)
        r_all, r_ie = chart_relationship(d, ie, t, mode)
        mean, ci = chart_forecast(ie, t, mode)
        chart_sentiment(t, mode, shares)
    print(f"Ireland energy use: peak {ie['Energy use'].idxmax()} {ie['Energy use'].max():,.0f}, 2022 {ie['Energy use'].iloc[-1]:,.0f} ({drop:.1%})")
    print(f"Ireland electricity: peak {ie['Electric Power Consumption'].idxmax()} {ie['Electric Power Consumption'].max():,.0f}, 2022 {ie['Electric Power Consumption'].iloc[-1]:,.0f}")
    print(f"EU avg 2022: energy {eu['Energy use'].iloc[-1]:,.0f}, electricity {eu['Electric Power Consumption'].iloc[-1]:,.0f}")
    print(f"correlation EU {r_all:.3f}, Ireland {r_ie:.3f}")
    print("ARIMA forecast", mean.round(0).tolist(), ci.round(0).values.tolist())
    print(f"sentiment {n_posts} posts", {k: round(v, 3) for k, v in shares.items()}, f"mean compound {mean_comp:.3f}")
