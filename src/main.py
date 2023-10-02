import logging

import matplotlib.pyplot as plt
import pandas as pd

from ffc_db import FFC_DB

LOG_FORMAT = "[%(asctime)s - %(levelname)s] %(message)s"
DATE_FORMAT = "%d-%m-%Y %H:%M:%S"


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT, datefmt=DATE_FORMAT)
    logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT, datefmt=DATE_FORMAT)
    db = FFC_DB()
    if not db.is_downloaded:
        db.download_xlsx()
    # db.clean_data()
    df = db.get_clean_data()
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
        percentage_hazardous = (hazardous_substances / total_substances) * 100
        results.append({
            'material': column, 
            'percentage_hazardous': percentage_hazardous,
            'count': total_substances
        })

    result_df = pd.DataFrame(results)

    materials = result_df['material'].tolist()
    counts = result_df['count'].tolist()
    percentages = result_df['percentage_hazardous'].tolist()

    bars = plt.bar(materials, percentages, color='blue')

    for i, bar in enumerate(bars):
        plt.text(i, bar.get_height() / 2, f'{round(percentages[i], 2)}%', ha='center', va='bottom', color='white', fontsize=8)

    plt.ylabel('Count of Substances')
    plt.title('Count of Substances in Each Material (Colored by Hazardous Percentage)')
    plt.xticks(rotation=45, ha='right')

    # Display the plot in Streamlit
    plt.show()


