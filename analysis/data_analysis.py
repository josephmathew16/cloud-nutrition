# analysis/data_analysis.py
from __future__ import annotations

from pathlib import Path
from datetime import datetime
import pandas as pd

# --- Headless plotting so CI (GitHub Actions) can generate figures without a display
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns


# ---------- Robust paths (works no matter where you run from)
BASE = Path(__file__).resolve().parent.parent
DATA_PATH = BASE / "data" / "All_Diets.csv"
OUT_DIR = BASE / "analysis" / "outputs"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def log(msg: str):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}")


def main():
    log("START Task 1")
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Missing dataset: {DATA_PATH}")

    # 1) Load
    df = pd.read_csv(DATA_PATH)
    log(f"Loaded data: {df.shape[0]} rows, {df.shape[1]} cols")

    # 2) Normalize column names to match the brief (handles minor variants)
    rename_map: dict[str, str] = {}
    wanted = {
        "diet_type": "Diet_type",
        "recipe_name": "Recipe_name",
        "cuisine_type": "Cuisine_type",
        "protein(g)": "Protein(g)",
        "carbs(g)": "Carbs(g)",
        "fat(g)": "Fat(g)",
        "extraction_day": "Extraction_day",
        "extraction_time": "Extraction_time",
    }
    lower_to_actual = {c.lower().replace(" ", "_"): c for c in df.columns}
    for key, canonical in wanted.items():
        if canonical in df.columns:
            continue
        if key in lower_to_actual:
            rename_map[lower_to_actual[key]] = canonical
    if rename_map:
        df.rename(columns=rename_map, inplace=True)

    # 3) Clean: coerce numerics & fill nulls with column means (brief allows mean-fill)
    for col in ["Protein(g)", "Carbs(g)", "Fat(g)"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
            df[col].fillna(df[col].mean(skipna=True), inplace=True)

    # 4) New metrics
    df["Protein_to_Carbs_ratio"] = df["Protein(g)"] / df["Carbs(g)"].replace(0, pd.NA)
    df["Carbs_to_Fat_ratio"] = df["Carbs(g)"] / df["Fat(g)"].replace(0, pd.NA)
    df[["Protein_to_Carbs_ratio", "Carbs_to_Fat_ratio"]] = df[
        ["Protein_to_Carbs_ratio", "Carbs_to_Fat_ratio"]
    ].fillna(0)

    # 5) Required summaries
    avg_by_diet = (
        df.groupby("Diet_type")[["Protein(g)", "Carbs(g)", "Fat(g)"]]
        .mean()
        .reset_index()
    )
    avg_by_cuisine = (
        df.groupby("Cuisine_type")[["Protein(g)", "Carbs(g)", "Fat(g)"]]
        .mean()
        .reset_index()
    )
    top5_per_diet = (
        df.sort_values("Protein(g)", ascending=False)
        .groupby("Diet_type")
        .head(5)[["Diet_type", "Recipe_name", "Cuisine_type", "Protein(g)"]]
        .reset_index(drop=True)
    )
    most_common = (
        df.groupby(["Diet_type", "Cuisine_type"])
        .size()
        .reset_index(name="count")
        .sort_values(["Diet_type", "count"], ascending=[True, False])
        .groupby("Diet_type")
        .head(1)
        .reset_index(drop=True)
    )
    highest_protein_diet = avg_by_diet.loc[
        avg_by_diet["Protein(g)"].idxmax(), "Diet_type"
    ]

    # 6) Write CSV outputs (exact filenames)
    def write_csv(d: pd.DataFrame, name: str):
        p = OUT_DIR / name
        d.to_csv(p, index=False)
        log(f"WRITE {p}")

    write_csv(avg_by_diet, "avg_by_diet.csv")
    write_csv(avg_by_cuisine, "avg_by_cuisine.csv")
    write_csv(top5_per_diet, "top5_protein_per_diet.csv")
    write_csv(most_common, "most_common_cuisine_per_diet.csv")
    write_csv(
        df[
            [
                "Diet_type",
                "Recipe_name",
                "Cuisine_type",
                "Protein(g)",
                "Carbs(g)",
                "Fat(g)",
                "Protein_to_Carbs_ratio",
                "Carbs_to_Fat_ratio",
            ]
        ],
        "macro_ratios.csv",
    )

    # 7) Visuals (3 required)
    sns.set_theme()

    # A) Grouped bar: avg Protein/Carbs/Fat by Diet_type
    m = avg_by_diet.melt(
        id_vars="Diet_type",
        value_vars=["Protein(g)", "Carbs(g)", "Fat(g)"],
        var_name="Macro",
        value_name="grams",
    )
    plt.figure(figsize=(11, 6))
    sns.barplot(data=m, x="Diet_type", y="grams", hue="Macro")
    plt.title("Average Macros by Diet Type")
    plt.xlabel("Diet Type")
    plt.ylabel("grams")
    plt.tight_layout()
    fp = OUT_DIR / "avg_macros_by_diet.png"
    plt.savefig(fp, dpi=150)
    plt.close()
    log(f"PLOT {fp}")

    # B) Heatmap: mean Protein by Diet × Cuisine
    pivot = df.pivot_table(
        index="Diet_type",
        columns="Cuisine_type",
        values="Protein(g)",
        aggfunc="mean",
        fill_value=0,
    )
    plt.figure(figsize=(12, 7))
    sns.heatmap(pivot, cmap="viridis")
    plt.title("Mean Protein (g) by Diet × Cuisine")
    plt.tight_layout()
    fp = OUT_DIR / "diet_cuisine_heatmap.png"
    plt.savefig(fp, dpi=150)
    plt.close()
    log(f"PLOT {fp}")

    # C) Stripplot: Top-5 protein items per diet, across cuisines
    plt.figure(figsize=(12, 6))
    sns.stripplot(
        data=top5_per_diet,
        x="Cuisine_type",
        y="Protein(g)",
        hue="Diet_type",
        dodge=True,
    )
    plt.xticks(rotation=45)
    plt.title("Top-5 Protein-Rich Recipes per Diet (by Cuisine)")
    plt.tight_layout()
    fp = OUT_DIR / "top5_per_diet_by_cuisine.png"
    plt.savefig(fp, dpi=150)
    plt.close()
    log(f"PLOT {fp}")

    # 8) Console summary (for screenshot)
    log(f"Highest average protein diet: {highest_protein_diet}")
    log(f"DONE -> outputs in {OUT_DIR}")


if __name__ == "__main__":
    main()
