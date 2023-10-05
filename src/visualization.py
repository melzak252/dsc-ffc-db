from typing import Tuple

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
import seaborn as sns
from sklearn.metrics import confusion_matrix, roc_curve, auc
from sklearn.linear_model import LogisticRegression

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

def _plot_bars(labels: pd.Series, values: pd.Series, color: str="#000080", is_perc: bool = False) -> None:
    plt.grid(True, linestyle="--", linewidth=0.5)
    bars = plt.bar(labels, values, color=color, zorder=3)

    plt.xticks(rotation=45, ha="right")

    for i, (bar, count) in enumerate(zip(bars, values)):
        plt.text(
            i,
            bar.get_height() / 2,
            f"{count}{'%' if is_perc else ''}",
            ha="center",
            va="bottom",
            color="white",
            fontsize=8,
        )

def plot_hazardous_pie_chart(df: pd.DataFrame, save: bool = False, fig_size: Tuple[float, float] = (12, 8)):
    plt.style.use("dark_background")

    fig = plt.figure(figsize=fig_size)
    gs = gridspec.GridSpec(2, 2, width_ratios=[2, 1], height_ratios=[1, 1])

    total_count = len(df)
    potential_concern_count = len(df[df["Potential concern non-auth"] & (~df["Hazardous auth"])])
    hazardous_count = len(df[df["Hazardous auth"]])
    hsub_in_food = len(df[df["Hazardous auth"] & df["food_contact"]])
    hsub_no_food = hazardous_count - hsub_in_food

    chart_data = [hsub_in_food, hsub_no_food]
    labels = ["In contact", "No contact"]
    colors = ["red", "blue"]

    def _absolute_value(val):
        a  = np.round(val/100. * total_count, 0).astype(int)
        return a

    ax0 = fig.add_subplot(gs[:, 0])
    ax0.pie(chart_data, labels=labels, colors=colors, autopct="%.2f%%")
    ax0.set_title("Percentage of Hazardous substances that can be in contact with food")


    chart_data = [hazardous_count, potential_concern_count, total_count - hazardous_count - potential_concern_count]
    labels = ["Hazardous", "Potential con.", "Safe"]   
    colors = ["red", "green", "blue"]

    ax1 = fig.add_subplot(gs[0, 1])
    ax1.pie(chart_data, labels=labels, colors=colors, autopct=_absolute_value)
    ax1.set_title("Count of classificated substances")
    
    ax2 = fig.add_subplot(gs[1, 1])
    ax2.pie(chart_data, labels=labels, colors=colors, autopct="%.2f%%")
    ax2.set_title("Percentage of classificated substances")

    plt.tight_layout()
    if save:
        plt.savefig("pie_chart_of_percentage_of_hazardous_substances_in_contact_with_food.png")
        return

    plt.show(block=False)
    plt.pause(0.2)


def plot_hazardous_count(df: pd.DataFrame, save: bool = False, fig_size: Tuple[float, float] = (11, 6)) -> bool:
    plt.style.use("dark_background")
    plt.figure(figsize=fig_size)

    df.sort_values("hazardous_substances_count", inplace=True, ascending=False)
    
    _plot_bars(df["material"], df["hazardous_substances_count"])
    
    plt.title("Count of Hazardous Substances that can be found in Material")
    plt.tight_layout()

    if save:
        plt.savefig("hazardous_substances_count_in_materials.png")
        return

    plt.show(block=False)
    plt.pause(0.2)

def plot_hazardous_percentage(df: pd.DataFrame, save: bool = False, fig_size: Tuple[float, float] = (11, 6)) -> None:
    plt.style.use("dark_background")
    plt.figure(figsize=fig_size)

    df.sort_values("percentage_hazardous", inplace=True, ascending=False)

    _plot_bars(df["material"], df["percentage_hazardous"], is_perc=True)
    
    plt.title("Percentage of Hazardous Substances that can be found in Material")
    plt.tight_layout()
    
    if save:
        plt.savefig("percentage_of_hazardous_substances_in_materials.png")
        return

    plt.show(block=False)
    plt.pause(0.2)


def plot_material_count(df: pd.DataFrame, save: bool = False, fig_size: Tuple[float, float] = (11, 6)) -> None:
    plt.style.use("dark_background")
    plt.figure(figsize=fig_size)

    df.sort_values("count", inplace=True, ascending=False)
    
    _plot_bars(df["material"], df["count"])
    
    plt.title("Count of Substances that can be found in Material")
    plt.tight_layout()

    if save:
        plt.savefig("substances_count_in_materials.png")
        return

    plt.show(block=False)
    plt.pause(0.2)



