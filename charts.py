# charts.py - Professional Charts for Campus Lost & Found
# This file ONLY makes charts. It never touches database.
# app.py calls: plot_category_chart(df) and plot_status_chart(df)

import matplotlib.pyplot as plt
import pandas as pd

# --- Brand Colors - Must match app.py CSS ---
COLORS = {
    "primary": "#FF4B4B",   # Red - main
    "dark": "#111827",      # Dark sidebar
    "blue": "#3B82F6",
    "green": "#22C55E",
    "orange": "#F97316",
    "purple": "#8B5CF6",
    "pink": "#EC4899",
    "teal": "#14B8A6",
    "grey": "#94A3B8",
}

# Professional palette for categories
CATEGORY_COLORS = ["#FF4B4B", "#3B82F6", "#22C55E", "#F97316", "#8B5CF6", "#EC4899", "#14B8A6", "#EAB308"]
STATUS_COLORS = {
    "Lost": "#FF4B4B",
    "Found": "#22C55E",
    "Open": "#3B82F6",
    "Claimed": "#F97316",
    "Returned": "#22C55E",
}

def _style_ax(ax):
    """Make every chart look clean and modern like app.py"""
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color("#E2E8F0")
    ax.spines['bottom'].set_color("#E2E8F0")
    ax.tick_params(colors="#64748B", labelsize=9)
    ax.yaxis.grid(True, color="#F1F5F9", linewidth=0.8)
    ax.set_axisbelow(True)

def plot_category_chart(df):
    """
    Called in app.py as: st.pyplot(plot_category_chart(df))
    Input: DataFrame with column 'category'
    Output: Matplotlib Figure
    """
    fig, ax = plt.subplots(figsize=(6.5, 4.2))
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    # Safety: empty or missing column
    if df is None or len(df) == 0 or "category" not in df.columns:
        ax.text(0.5, 0.5, "No data yet\nReport an item to see chart",
                ha="center", va="center", fontsize=12, color="#64748B", transform=ax.transAxes)
        ax.axis("off")
        plt.tight_layout()
        return fig

    counts = df["category"].value_counts()
    # Keep order, limit to 8
    counts = counts.head(8)

    bars = ax.bar(
        counts.index,
        counts.values,
        color=CATEGORY_COLORS[:len(counts)],
        edgecolor="white",
        linewidth=1.2,
        width=0.6,
        zorder=3
    )

    # Add numbers on top of bars - like in image
    for bar in bars:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height + 0.15,
            f"{int(height)}",
            ha="center", va="bottom",
            fontsize=11, fontweight="bold", color="#0F172A"
        )

    ax.set_title("Items by Category", fontsize=13, fontweight="bold", color="#0F172A", loc="left", pad=14)
    ax.set_xlabel("Category", fontsize=10, color="#64748B")
    ax.set_ylabel("Number of Reports", fontsize=10, color="#64748B")
    ax.set_ylim(0, max(counts.values) + 1.5)
    plt.xticks(rotation=20, ha="right")
    _style_ax(ax)
    plt.tight_layout()
    return fig

def plot_status_chart(df):
    """
    Called in app.py as: st.pyplot(plot_status_chart(df))
    Input: DataFrame with columns 'type' and 'status'
    Output: Matplotlib Figure - Pie / Donut chart
    """
    fig, ax = plt.subplots(figsize=(6.5, 4.2))
    fig.patch.set_facecolor("white")

    # Safety: empty
    if df is None or len(df) == 0 or "type" not in df.columns:
        ax.text(0.5, 0.5, "No data yet",
                ha="center", va="center", fontsize=12, color="#64748B")
        ax.axis("off")
        plt.tight_layout()
        return fig

    # We show: Lost, Found, Claimed
    # Claimed is status == Claimed, rest are type
    lost = len(df[df["type"] == "Lost"])
    found = len(df[df["type"] == "Found"])
    claimed = 0
    if "status" in df.columns:
        claimed = len(df[df["status"] == "Claimed"])
        # Avoid double counting: Found/Lost includes claimed, so adjust
        # For chart we want 3 slices that make sense:
        # Lost Open, Found Open, Claimed
        # Simpler: show total Lost, total Found, total Claimed as 3 groups
        # But to keep total = 100%, we do: Lost, Found, Claimed as separate counts
        # If claimed items are also in Lost/Found, we subtract them
        lost_open = len(df[(df["type"] == "Lost") & (df["status"] != "Claimed")])
        found_open = len(df[(df["type"] == "Found") & (df["status"] != "Claimed")])
        lost, found = lost_open, found_open

    labels = []
    values = []
    colors = []

    if lost > 0:
        labels.append(f"Lost ({lost})")
        values.append(lost)
        colors.append(STATUS_COLORS["Lost"])
    if found > 0:
        labels.append(f"Found ({found})")
        values.append(found)
        colors.append(STATUS_COLORS["Found"])
    if claimed > 0:
        labels.append(f"Claimed ({claimed})")
        values.append(claimed)
        colors.append(STATUS_COLORS["Claimed"])

    if sum(values) == 0:
        ax.text(0.5, 0.5, "No data yet", ha="center", va="center", fontsize=12, color="#64748B")
        ax.axis("off")
        plt.tight_layout()
        return fig

    # Donut chart - looks more professional than normal pie
    wedges, texts, autotexts = ax.pie(
        values,
        labels=labels,
        colors=colors,
        autopct="%1.0f%%",
        startangle=90,
        pctdistance=0.78,
        wedgeprops=dict(width=0.45, edgecolor="white", linewidth=2),
        textprops=dict(fontsize=10, color="#0F172A"),
    )
    for t in autotexts:
        t.set_fontsize(10)
        t.set_fontweight("bold")
        t.set_color("white")

    # Center text
    ax.text(0, 0, f"Total\n{sum(values)}", ha="center", va="center", fontsize=13, fontweight="bold", color="#0F172A")
    ax.set_title("Lost vs Found vs Claimed", fontsize=13, fontweight="bold", color="#0F172A", pad=14)
    plt.tight_layout()
    return fig

# Extra helper - if you want to use in future, not required by app.py
def plot_monthly_chart(df):
    """Optional: Not used in app.py yet, safe to keep"""
    fig, ax = plt.subplots(figsize=(6.5, 3.5))
    fig.patch.set_facecolor("white")
    if df is None or len(df) == 0 or "date" not in df.columns:
        ax.text(0.5, 0.5, "No data yet", ha="center", va="center")
        ax.axis("off")
        return fig
    df_copy = df.copy()
    df_copy["date"] = pd.to_datetime(df_copy["date"], errors="coerce")
    counts = df_copy.groupby(df_copy["date"].dt.date).size()
    ax.plot(counts.index, counts.values, color=COLORS["primary"], marker="o", linewidth=2.5, markersize=6)
    ax.fill_between(counts.index, counts.values, alpha=0.15, color=COLORS["primary"])
    ax.set_title("Reports Over Time", fontsize=13, fontweight="bold", color="#0F172A", loc="left")
    _style_ax(ax)
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    return fig
