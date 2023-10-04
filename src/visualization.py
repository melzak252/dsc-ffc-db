import pandas as pd
import matplotlib as matplt
import matplotlib.pyplot as plt

MATERIALS = [
    "Plastics",
    "Coatings",
    "Rubber",
    "Silicones",
    "Ion-Exchange Resins",
    "Paper/Board",
    "Cellophane",
    "Textiles",
    "Cork and Wood",
    "Adhesives",
    "Colorants",
    "Printing Inks",
    "Wax",
    "Inorganics",
    "A&I Materials",
    "Other Uses",
]


def plot_hazardous_pie_chart(df: pd.DataFrame):
    plt.figure(figsize=(10, 6))
    plt.style.use("dark_background")

    total_count = df[df["Hazardous auth"]].size
    hsub_in_food = df[df["Hazardous auth"] & (df["food_contact"] | df["SIN food contact"])].size
    hsub_no_food = total_count - hsub_in_food

    chart_data = [hsub_in_food, hsub_no_food]
    labels = ["In contact", "No contact"]
    colors = {"red", "blue"}

    plt.pie(chart_data, labels=labels, colors=colors, autopct="%.2f")
    plt.title("Percentage of Hazardous substances in contact with food")

    plt.savefig("hazardous_pie_chart.png")


def plot_bars(labels: pd.Series, values: pd.Series, color: str="#000099") -> None:
    plt.grid(True, linestyle="--", linewidth=0.5)
    bars = plt.bar(labels, values, color=color, zorder=3)

    plt.xticks(rotation=45, ha="right")

    for i, (bar, count) in enumerate(zip(bars, values)):
        plt.text(
            i,
            bar.get_height() / 2,
            f"{count}",
            ha="center",
            va="bottom",
            color="white",
            fontsize=8,
        )

def plot_hazardous_count(df: pd.DataFrame):
    plt.figure(figsize=(10, 6))
    plt.style.use("dark_background")
    df.sort_values("hazardous_substances_count", inplace=True, ascending=False)
    plot_bars(df["material"], df["hazardous_substances_count"])
    plt.ylabel("Count of Hazardous Substances")
    plt.title("Count of Hazardous Substances in Each Material")
    plt.tight_layout()
    plt.savefig("hazardous_count.png")

def plot_hazardous_percentage(df: pd.DataFrame):
    plt.figure(figsize=(10, 6))
    plt.style.use("dark_background")
    df.sort_values("percentage_hazardous", inplace=True, ascending=False)
    plot_bars(df["material"], df["percentage_hazardous"])
    plt.ylabel("Percentage of Hazardous Substances")
    plt.title("Percentage of Hazardous Substances in Each Material")
    plt.tight_layout()
    plt.savefig("hazardous_percentage.png")


def plot_material_count(df: pd.DataFrame):
    plt.figure(figsize=(10, 6))
    plt.style.use("dark_background")
    df.sort_values("count", inplace=True, ascending=False)
    plot_bars(df["material"], df["count"])
    plt.ylabel("Count of Materials")
    plt.title("Count of Substances in Each Material")
    plt.tight_layout()
    plt.savefig("material_count.png")



def prepare_data_for_material_plots(df: pd.DataFrame) -> pd.DataFrame:
    results = []

    for column in MATERIALS:
        total_substances = df[column].sum()
        hazardous_substances = len(df[df["Hazardous auth"] & df[column]])

        percentage_hazardous = round((hazardous_substances / total_substances) * 100, 1)
        results.append(
            {
                "material": column,
                "percentage_hazardous": percentage_hazardous,
                "count": total_substances,
                "hazardous_substances_count": hazardous_substances,
            }
        )

    return pd.DataFrame(results)
