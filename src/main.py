import logging

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from ffc_db import FFC_DB
from visualization import plot_hazardous_count, plot_material_count, plot_hazardous_percentage, plot_hazardous_pie_chart, prepare_data_for_material_plots

if __name__ == "__main__":
    db = FFC_DB()
    
    if not db.is_downloaded:
        db.download_xlsx()

    db.clean_data()

    df = db.get_clean_data()
    
    db.save_strong_correlations(df)

    db.save_strong_correlations(df, 'kendall')

    db.save_strong_correlations(df, 'spearman')

    material_df = prepare_data_for_material_plots(df)
    plot_hazardous_pie_chart(df)
    plot_material_count(material_df)
    plot_hazardous_count(material_df)
    plot_hazardous_percentage(material_df)

