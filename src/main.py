import logging

import matplotlib.pyplot as plt
import pandas as pd

from ffc_db import FFC_DB
from visualization import plot_hazardous_count, hazardous_pie_chart

LOG_FORMAT = "[%(asctime)s - %(levelname)s] %(message)s"
DATE_FORMAT = "%d-%m-%Y %H:%M:%S"





if __name__ == "__main__":
    
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT, datefmt=DATE_FORMAT)
    logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT, datefmt=DATE_FORMAT)
    db = FFC_DB()
    # if not db.is_downloaded:
    #     db.download_xlsx()

    # db.clean_data()

    df = db.get_clean_data()
    # hazardous_pie_chart(df)
    plot_hazardous_count(df)
    plt.show()

