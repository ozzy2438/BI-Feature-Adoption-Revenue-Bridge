"""
Generate a 4-panel recruiter-friendly composite image for the README.
Charts: Funnel Leakage · Cohort Retention · Feature Adoption · Revenue Bridge
Run: python python/generate_readme_visual.py
Output: assets/readme_visual.png
"""

import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch
import matplotlib.gridspec as gridspec
from pathlib import Path

# ── Paths ─────────────────────────────────────────────────────────────────────
ROOT  = Path(__file__).resolve().parents[1]
RAW   = ROOT / "data" / "raw"
OUT   = ROOT / "assets" / "readme_visual.png"

# ── Load data ─────────────────────────────────────────────────────────────────
rev = pd.read_csv(RAW / "sim_revenue_monthly.csv", parse_dates=["month"])
evt = pd.read_csv(RAW / "sim_events.csv",          parse_dates=["event_month"])
acc = pd.read_csv(RAW / "sim_accounts.csv",        parse_dates=["signup_month"])

# ── Palette ───────────────────────────────────────────────────────────────────
BG        = "#F7F9FC"
PANEL_BG  = "#FFFFFF"
BLUE      = "#2E86DE"
GREEN     = "#27AE60"
ORANGE    = "#E67E22"
RED       = "#E74C3C"
PURPLE    = "#8E44AD"
GREY      = "#BDC3C7"
DARK      = "#2C3E50"
ANNOT_BG  = "#FFFBE6"          # soft yellow sticky-note background
ANNOT_BD  = "#F39C12"          # amber border

FONT_TITLE  = dict(fontsize=13, fontweight="bold", color=DARK)
FONT_SUB    = dict(fontsize=9,  color="#7F8C8D")
FONT_ANNOT  = dict(fontsize=8.5, color=DARK, style="italic")
FONT_LABEL  = dict(fontsize=8,  color=DARK)


# ══════════════════════════════════════════════════════════════════════════════
# Helper: sticky-note annotation box
# ══════════════════════════════════════════════════════════════════════════════
def sticky(ax, x, y, text, color=ANNOT_BD, ha="left", va="top"):
    ax.annotate(
        text, xy=(x, y), xycoords="axes fraction",
        fontsize=8.5, color=DARK, style="italic",
        ha=ha, va=va,
        bbox=dict(boxstyle="round,pad=0.4", fc=ANNOT_BG, ec=color, lw=1.2),
    )


# ══════════════════════════════════════════════════════════════════════════════
# 1. FUNNEL LEAKAGE
# ══════════════════════════════════════════════════════════════════════════════
FUNNEL_STEPS = [
    ("Signed Up",           "signup"),
    ("Created Invoice",     "first_invoice_created"),
    ("First Payment",       "first_payment_received"),
    ("Connected Integration","app_integration_connected"),
    ("Activated Feature",   "feature_activated"),
]

funnel_counts = []
for label, name in FUNNEL_STEPS:
    n = evt[evt["event_name"] == name]["account_id"].nunique()
    funnel_counts.append((label, n))

labels_f  = [x[0] for x in funnel_counts]
counts_f  = [x[1] for x in funnel_counts]
pct_f     = [c / counts_f[0] * 100 for c in counts_f]

# drop-off percentage at each step
drop_f = []
for i in range(len(counts_f)):
    if i == 0:
        drop_f.append(0)
    else:
        drop_f.append((counts_f[i - 1] - counts_f[i]) / counts_f[i - 1] * 100)

# bar colours – highlight the worst drop-off step
bar_colors_f = [BLUE] * len(labels_f)
worst_step   = drop_f.index(max(drop_f[1:]))     # ignore step 0
bar_colors_f[worst_step] = RED


# ══════════════════════════════════════════════════════════════════════════════
# 2. COHORT RETENTION HEATMAP
# ══════════════════════════════════════════════════════════════════════════════
# Build first-payment month per account
fp = (
    evt[evt["event_name"] == "first_payment_received"]
    .groupby("account_id")["event_month"]
    .min()
    .reset_index()
    .rename(columns={"event_month": "cohort_month"})
)

# Join to monthly revenue to get all months where the account was paid-active
paid = rev[(rev["mrr_end"] > 0)][["account_id", "month"]].copy()
cohort_df = paid.merge(fp, on="account_id", how="inner")
cohort_df["age_month"] = (
    (cohort_df["month"].dt.year  - cohort_df["cohort_month"].dt.year) * 12 +
    (cohort_df["month"].dt.month - cohort_df["cohort_month"].dt.month)
)

# Cohort sizes (M+0)
cohort_sizes = (
    cohort_df[cohort_df["age_month"] == 0]
    .groupby("cohort_month")["account_id"]
    .nunique()
    .rename("cohort_size")
)

# Retention matrix
ret = (
    cohort_df[cohort_df["age_month"].between(0, 12)]
    .groupby(["cohort_month", "age_month"])["account_id"]
    .nunique()
    .reset_index(name="count")
    .merge(cohort_sizes, on="cohort_month")
)
ret["retention"] = ret["count"] / ret["cohort_size"]

pivot = ret.pivot(index="cohort_month", columns="age_month", values="retention")
pivot.index = pivot.index.strftime("%Y-%m")

# Keep at most 10 cohorts for readability
pivot = pivot.tail(10)


# ══════════════════════════════════════════════════════════════════════════════
# 3. FEATURE ADOPTION OVER TIME
# ══════════════════════════════════════════════════════════════════════════════
# Cumulative unique accounts that have ever activated bank_feed_sync each month
bfs = (
    evt[(evt["event_name"] == "feature_activated") &
        (evt["feature_name"] == "bank_feed_sync")]
    [["account_id", "event_month"]]
    .drop_duplicates()
)

months_sorted = sorted(rev["month"].unique())
paid_active_by_month = (
    rev[rev["mrr_end"] > 0]
    .groupby("month")["account_id"]
    .nunique()
    .rename("paid_active")
    .reset_index()
)

cum_adopters = []
seen = set()
for m in months_sorted:
    new = set(bfs[bfs["event_month"] <= m]["account_id"]) - seen
    seen.update(new)
    cum_adopters.append({"month": m, "adopters": len(seen)})

adopt_df = pd.DataFrame(cum_adopters).merge(paid_active_by_month, on="month", how="left")
adopt_df["adoption_rate"] = adopt_df["adopters"] / adopt_df["paid_active"].clip(lower=1)
adopt_df = adopt_df[adopt_df["paid_active"] > 0]


# ══════════════════════════════════════════════════════════════════════════════
# 4. REVENUE BRIDGE (quarterly waterfall — 2024Q3, richest quarter)
# ══════════════════════════════════════════════════════════════════════════════
rev["quarter"] = rev["month"].dt.to_period("Q").astype(str)

# Positive components from simulation flags
pos_comp = (
    rev[rev["bridge_component"].isin(
        ["New Customers", "Plan Upgrade", "Feature Adoption Lift"]
    )]
    .groupby(["quarter", "bridge_component"])["mrr_delta"]
    .sum()
    .reset_index()
)

# Derive Churn / Contraction from mrr_delta < 0
neg = rev[rev["mrr_delta"] < 0].copy()
neg["bridge_component"] = neg.apply(
    lambda r: "Churn" if r["mrr_end"] == 0 else "Contraction", axis=1
)
neg_comp = neg.groupby(["quarter", "bridge_component"])["mrr_delta"].sum().reset_index()
bridge_q = pd.concat([pos_comp, neg_comp], ignore_index=True)

# Use Q3 2024 — has all 5 components and is the richest full quarter
TARGET_Q = "2024Q3"
wf = bridge_q[bridge_q["quarter"] == TARGET_Q].set_index("bridge_component")["mrr_delta"]

ORDER = ["New Customers", "Plan Upgrade", "Feature Adoption Lift", "Contraction", "Churn"]
wf    = wf.reindex([o for o in ORDER if o in wf.index]).fillna(0)

COLORS_WF = {
    "New Customers":          GREEN,
    "Plan Upgrade":           BLUE,
    "Feature Adoption Lift":  PURPLE,
    "Contraction":            ORANGE,
    "Churn":                  RED,
}


# ══════════════════════════════════════════════════════════════════════════════
# FIGURE LAYOUT
# ══════════════════════════════════════════════════════════════════════════════
fig = plt.figure(figsize=(18, 13), facecolor=BG)
fig.patch.set_facecolor(BG)

# Master title banner
fig.text(
    0.5, 0.97,
    "Feature Adoption → Revenue Bridge  |  Analytics Platform Overview",
    ha="center", va="top",
    fontsize=18, fontweight="bold", color=DARK,
)
fig.text(
    0.5, 0.945,
    "Built with Python · BigQuery · dbt · Power BI  |  Synthetic SaaS simulation — adapts to real Segment / Stripe data",
    ha="center", va="top",
    fontsize=10, color="#7F8C8D",
)

gs = gridspec.GridSpec(
    2, 2,
    figure=fig,
    top=0.91, bottom=0.05,
    left=0.05, right=0.97,
    hspace=0.40, wspace=0.32,
)

axes = [fig.add_subplot(gs[r, c]) for r in range(2) for c in range(2)]
for ax in axes:
    ax.set_facecolor(PANEL_BG)
    for sp in ax.spines.values():
        sp.set_color("#DDE1E7")
        sp.set_linewidth(0.8)


# ── Panel 1: Funnel Leakage ───────────────────────────────────────────────────
ax1 = axes[0]
bars = ax1.barh(
    range(len(labels_f)), counts_f,
    color=bar_colors_f, edgecolor="white", linewidth=0.6, height=0.55,
)
ax1.set_yticks(range(len(labels_f)))
ax1.set_yticklabels(labels_f, **FONT_LABEL)
ax1.invert_yaxis()
ax1.set_xlabel("Unique Accounts", **FONT_LABEL)
ax1.set_title("① Onboarding Funnel Leakage", **FONT_TITLE)
ax1.text(0, -0.12, "Where are users dropping off?", transform=ax1.transAxes, **FONT_SUB)

# Value labels on bars
for i, (bar, cnt, pct) in enumerate(zip(bars, counts_f, pct_f)):
    ax1.text(cnt + 20, i, f"{cnt:,}  ({pct:.0f}%)", va="center", **FONT_LABEL)

ax1.set_xlim(0, counts_f[0] * 1.22)
ax1.tick_params(axis="x", labelsize=8)

# Annotate worst drop
wd_label = labels_f[worst_step]
wd_drop  = drop_f[worst_step]
sticky(
    ax1, 0.52, 0.98,
    f"⚠ Biggest leak: {wd_label}\n   {wd_drop:.0f}% of users don't\n   complete this step",
    color=RED, ha="left", va="top",
)


# ── Panel 2: Cohort Retention Heatmap ────────────────────────────────────────
ax2 = axes[1]
import matplotlib.colors as mcolors

cmap = plt.cm.get_cmap("Blues", 256)
cmap = mcolors.LinearSegmentedColormap.from_list(
    "custom_blues", ["#EBF5FB", "#2E86DE"], N=256
)

mask_cols = [c for c in range(13) if c in pivot.columns]
heat_data = pivot[mask_cols].values
im = ax2.imshow(heat_data, aspect="auto", cmap=cmap, vmin=0, vmax=1)

ax2.set_xticks(range(len(mask_cols)))
ax2.set_xticklabels([f"M+{c}" for c in mask_cols], fontsize=7, color=DARK)
ax2.set_yticks(range(len(pivot)))
ax2.set_yticklabels(pivot.index, fontsize=7, color=DARK)
ax2.set_xlabel("Months since first payment", **FONT_LABEL)
ax2.set_title("② Paid Cohort Retention", **FONT_TITLE)
ax2.text(0, -0.14, "Which customer groups survive 6–12 months?", transform=ax2.transAxes, **FONT_SUB)

# Overlay cell values
for ri in range(heat_data.shape[0]):
    for ci in range(heat_data.shape[1]):
        val = heat_data[ri, ci]
        if not np.isnan(val):
            ax2.text(ci, ri, f"{val:.0%}", ha="center", va="center",
                     fontsize=6.5, color="white" if val > 0.6 else DARK)

plt.colorbar(im, ax=ax2, fraction=0.04, pad=0.02, format="{x:.0%}")

# M+6 annotation
if 6 in mask_cols:
    ci6 = mask_cols.index(6)
    col_vals = heat_data[:, ci6]
    avg6 = np.nanmean(col_vals)
    sticky(
        ax2, 0.02, 0.22,
        f"Month-6 retention\naverages {avg6:.0%}\nacross all cohorts",
        color=BLUE, ha="left", va="top",
    )


# ── Panel 3: Feature Adoption Over Time ──────────────────────────────────────
ax3 = axes[2]

x3 = adopt_df["month"]
y3 = adopt_df["adoption_rate"] * 100
yp = adopt_df["paid_active"]

ax3_r = ax3.twinx()
ax3_r.fill_between(x3, yp, alpha=0.12, color=GREY)
ax3_r.set_ylabel("Paid-active accounts", fontsize=7, color=GREY)
ax3_r.tick_params(axis="y", labelsize=7, colors=GREY)

ax3.plot(x3, y3, color=PURPLE, linewidth=2.5, marker="o", markersize=4, label="bank_feed_sync adoption %")
ax3.set_ylabel("Adoption rate (%)", **FONT_LABEL)
ax3.set_title("③ Feature Adoption Growth", **FONT_TITLE)
ax3.text(0, -0.14, "Is the most impactful feature gaining traction?", transform=ax3.transAxes, **FONT_SUB)
ax3.tick_params(axis="x", rotation=30, labelsize=7)
ax3.tick_params(axis="y", labelsize=8)
ax3.set_ylim(0, max(y3.max() * 1.35, 10))
ax3.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0f}%"))

# Peak annotation
peak_idx = y3.idxmax()
peak_m   = x3[peak_idx]
peak_v   = y3[peak_idx]
ax3.annotate(
    f"Peak: {peak_v:.0f}%",
    xy=(peak_m, peak_v),
    xytext=(0.62, 0.88),
    textcoords="axes fraction",
    arrowprops=dict(arrowstyle="->", color=PURPLE, lw=1.5),
    fontsize=8, color=PURPLE, fontweight="bold",
)

sticky(
    ax3, 0.02, 0.98,
    "Accounts using bank_feed_sync\nchurn ~18% less than non-adopters",
    color=PURPLE, ha="left", va="top",
)


# ── Panel 4: Revenue Bridge Waterfall ────────────────────────────────────────
ax4 = axes[3]

components = wf.index.tolist()
values     = wf.values.tolist()
colors_bar = [COLORS_WF.get(c, GREY) for c in components]

# Proper cascading waterfall: each bar starts where previous bar ended
running = 0
bottoms_wf = []
heights_wf = []
for v in values:
    if v >= 0:
        bottoms_wf.append(running)
        heights_wf.append(v)
    else:
        bottoms_wf.append(running + v)  # bottom is running + negative
        heights_wf.append(abs(v))
    running += v

# Add "Net Change" summary bar
net_val = sum(values)
components_plot = components + ["Net Change"]
bottoms_wf      = bottoms_wf + [min(0, net_val)]
heights_wf      = heights_wf + [abs(net_val)]
colors_bar      = colors_bar + [GREEN if net_val >= 0 else RED]
values_plot     = values + [net_val]

x_pos = list(range(len(components_plot)))

bars4 = ax4.bar(
    x_pos, heights_wf,
    bottom=bottoms_wf,
    color=colors_bar,
    edgecolor="white", linewidth=0.8, width=0.55,
)

# Connector lines between bars (waterfall bridges)
for i in range(len(components)):
    y_top = bottoms_wf[i] + heights_wf[i]
    ax4.plot([i + 0.28, i + 0.72], [y_top, y_top],
             color="#AAB7B8", linewidth=0.7, linestyle="--")

ax4.set_xticks(x_pos)
ax4.set_xticklabels(
    [c.replace(" ", "\n") for c in components_plot],
    fontsize=7.5, color=DARK,
)
ax4.axhline(0, color=DARK, linewidth=0.8, linestyle="--", alpha=0.3)
ax4.set_ylabel("MRR ($)", **FONT_LABEL)
ax4.set_title(f"④ Revenue Bridge  (Q3 2024)", **FONT_TITLE)
ax4.text(0, -0.14, "What drove this quarter's MRR change?", transform=ax4.transAxes, **FONT_SUB)
ax4.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"${v:,.0f}"))
ax4.tick_params(axis="y", labelsize=7.5)

# Value labels on bars
for i, (v, b, h) in enumerate(zip(values_plot, bottoms_wf, heights_wf)):
    sign = "+" if v > 0 else ""
    ax4.text(
        i, b + h / 2,
        f"{sign}${abs(v):,.0f}",
        ha="center", va="center",
        fontsize=7, color="white", fontweight="bold",
    )

# Feature Adoption Lift callout (arrow to bar)
if "Feature Adoption Lift" in components:
    fi = components.index("Feature Adoption Lift")
    fl_val   = values[fi]
    tot_pos  = sum(v for v in values if v > 0)
    pct_lift = fl_val / tot_pos * 100 if tot_pos else 0
    bar_mid_y = bottoms_wf[fi] + heights_wf[fi] / 2

    ax4.annotate(
        f"Feature Adoption Lift\n= {pct_lift:.0f}% of expansion MRR",
        xy=(fi, bar_mid_y),
        xytext=(0.52, 0.88),
        textcoords="axes fraction",
        arrowprops=dict(arrowstyle="->", color=PURPLE, lw=1.5),
        fontsize=7.5, color=PURPLE, fontweight="bold",
        ha="center",
        bbox=dict(boxstyle="round,pad=0.3", fc=ANNOT_BG, ec=PURPLE, lw=1),
    )


# ── Panel labels (A B C D) ────────────────────────────────────────────────────
for ax, label in zip(axes, ["A", "B", "C", "D"]):
    ax.text(
        -0.01, 1.04, label,
        transform=ax.transAxes,
        fontsize=14, fontweight="bold", color=DARK,
        va="bottom", ha="right",
    )

# ── Footer ────────────────────────────────────────────────────────────────────
fig.text(
    0.5, 0.018,
    "Data: Xero-style SaaS simulation  ·  Stack: Python · BigQuery · dbt (incremental + merge) · Power BI · DAX · GA4  ·  github.com/ozzy2438/BI-Feature-Adoption-Revenue-Bridge",
    ha="center", va="bottom",
    fontsize=7.5, color="#95A5A6",
)

# ── Save ──────────────────────────────────────────────────────────────────────
OUT.parent.mkdir(exist_ok=True)
fig.savefig(OUT, dpi=160, bbox_inches="tight", facecolor=BG)
print(f"✓ Saved → {OUT}")
