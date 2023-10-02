import logging

import altair as alt
import pandas as pd
import streamlit as st

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

    # Calculate the percentage of hazardous substances for each material
    for column in material_columns:
        total_substances = df[column].sum()
        hazardous_substances = df[df['Hazardous auth'] & df[column]].shape[0]
        percentage_hazardous = (hazardous_substances / total_substances)
        results.append({'material': column, 'percentage_hazardous': percentage_hazardous})

    # Convert results to a DataFrame
    result_df = pd.DataFrame(results)

    # Create an Altair chart
    chart = alt.Chart(result_df).mark_bar().encode(
        x=alt.X('material', sort='-y'),
        y='percentage_hazardous',
        tooltip=['material', 'percentage_hazardous']
    ).properties(
        title="Percentage of Hazardous Substances in Each Material"
    )

    st.altair_chart(chart, use_container_width=True)
