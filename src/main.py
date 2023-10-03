import logging

import matplotlib.pyplot as plt
import pandas as pd

from ffc_db import FFC_DB

LOG_FORMAT = "[%(asctime)s - %(levelname)s] %(message)s"
DATE_FORMAT = "%d-%m-%Y %H:%M:%S"

def plot_bars(ax, labels, values, color='#000099'):
    ax.grid(True, linestyle='--', linewidth=0.5)
    bars = ax.bar(labels, values, color=color, zorder=3)
    for i, (bar, count) in enumerate(zip(bars, values)):
        ax.text(i, bar.get_height() / 2, f'{count}', ha='center', va='bottom', color='white', fontsize=8)

def plot_data(df: pd.DataFrame):
    material_columns = [
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

    results = []
 
    for column in material_columns:
        total_substances = df[column].sum()
        hazardous_substances = df[df['Hazardous auth'] & df[column]].shape[0]
        percentage_hazardous = (hazardous_substances / total_substances)
        results.append({
            'material': column, 
            'percentage_hazardous': percentage_hazardous,
            'count': total_substances,
            'hazardous_substances_count': hazardous_substances
        })

    result_df = pd.DataFrame(results)

    fig, (ax, ax1, ax2) = plt.subplots(ncols=3)

    # Counts
    result_df.sort_values("count", inplace=True, ascending=False)    
    plot_bars(ax, result_df['material'], result_df['count'])
    ax.set_ylabel('Count of Materials')
    ax.set_title('Count of Substances in Each Material')
    ax.set_xticklabels(result_df['material'], rotation=45, ha='right')

    # Hazardous substances count
    result_df.sort_values("hazardous_substances_count", inplace=True, ascending=False)    
    plot_bars(ax1, result_df['material'], result_df['hazardous_substances_count'])
    ax1.set_ylabel('Count of Hazardous Substances')
    ax1.set_title('Count of Hazardous Substances in Each Material')
    ax1.set_xticklabels(result_df['material'], rotation=45, ha='right')
   
    # Percentage
    result_df.sort_values("percentage_hazardous", inplace=True, ascending=False)    
    result_df["percentage_hazardous"] = round(result_df["percentage_hazardous"], 2)
    plot_bars(ax2, result_df['material'], result_df["percentage_hazardous"])
    ax2.set_ylabel('Percentage of Hazardous Substances')
    ax2.set_title('Percentage of Hazardous Substances in Each Material')
    ax2.set_xticklabels(result_df['material'], rotation=45, ha='right')
    fig.canvas.manager.window.state('zoomed')
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    plt.style.use('dark_background')
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT, datefmt=DATE_FORMAT)
    logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT, datefmt=DATE_FORMAT)
    db = FFC_DB()
    # if not db.is_downloaded:
    #     db.download_xlsx()

    # db.clean_data()

    df = db.get_clean_data()
    plot_data(df)



