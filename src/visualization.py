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


def hazardous_pie_chart(df: pd.DataFrame):
    plt.style.use("dark_background")

    total_count = df[df["Hazardous auth"]].size
    hsub_in_food = df[df["Hazardous auth"] & df["food_contact"]].size
    hsub_no_food = total_count - hsub_in_food

    chart_data = [hsub_in_food, hsub_no_food]
    labels = ["In contact", "No contact"]
    colors = {"red", "blue"}

    plt.pie(chart_data, labels=labels, colors=colors, autopct="%.2f")
    plt.title("Percentage of Hazardous substances in contact with food")


def plot_bars(ax: plt.Axes, labels: pd.Series, values: pd.Series, color: str="#000099") -> None:
    ax.grid(True, linestyle="--", linewidth=0.5)
    bars = ax.bar(labels, values, color=color, zorder=3)
    ax.set_xticks(labels)
    ax.set_xticklabels(labels, rotation=45, ha="right")

    for i, (bar, count) in enumerate(zip(bars, values)):
        ax.text(
            i,
            bar.get_height() / 2,
            f"{count}",
            ha="center",
            va="bottom",
            color="white",
            fontsize=8,
        )



def plot_hazardous_count(df: pd.DataFrame):
    plt.style.use("dark_background")
    fig, (ax, ax1, ax2) = plt.subplots(ncols=3)
    fig.canvas.manager.window.state("zoomed")

    results = []

    for column in MATERIALS:
        total_substances = df[column].sum()
        hazardous_substances = len(df[df["Hazardous auth"] & df[column]])

        percentage_hazardous = (hazardous_substances / total_substances) * 100
        results.append(
            {
                "material": column,
                "percentage_hazardous": percentage_hazardous,
                "count": total_substances,
                "hazardous_substances_count": hazardous_substances,
            }
        )

    result_df = pd.DataFrame(results)
     
    # Counts
    result_df.sort_values("count", inplace=True, ascending=False)
    plot_bars(ax, result_df["material"], result_df["count"])
    ax.set_ylabel("Count of Materials")
    ax.set_title("Count of Substances in Each Material")

    # Hazardous substances count
    result_df.sort_values("hazardous_substances_count", inplace=True, ascending=False)
    plot_bars(ax1, result_df["material"], result_df["hazardous_substances_count"])
    ax1.set_ylabel("Count of Hazardous Substances")
    ax1.set_title("Count of Hazardous Substances in Each Material")

    # Percentage
    result_df.sort_values("percentage_hazardous", inplace=True, ascending=False)
    result_df["percentage_hazardous"] = round(result_df["percentage_hazardous"], 1)
    plot_bars(ax2, result_df["material"], result_df["percentage_hazardous"])
    ax2.set_ylabel("Percentage of Hazardous Substances")
    ax2.set_title("Percentage of Hazardous Substances in Each Material")

    plt.tight_layout()
