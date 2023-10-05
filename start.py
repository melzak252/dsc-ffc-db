import argparse
import os

import matplotlib.pyplot as plt

from src.ffc_db import FFC_DB
from src.visualization import prepare_data_for_material_plots, plot_hazardous_count, plot_hazardous_percentage, plot_hazardous_pie_chart, plot_material_count

def main() -> None:
    parser = argparse.ArgumentParser(description="Script to manage FFCdb data.")

    parser.add_argument("-cm", "--corr-method", default="pearson", help="Checks pandas correlation between all numeric columns in cleaned data('pearson', 'kendall', 'spearman').")
    parser.add_argument("-corr", "--correlation", action="store_true", help="Saves pandas correlation between all numeric columns in cleaned data to csv file.")
    parser.add_argument("-c", "--config", default="constants.toml", help="Saves pandas correlation between all numeric columns in cleaned data to csv file.")
    parser.add_argument("-fd", "--force-download", action="store_true", help="Force redownload of raw data")
    parser.add_argument("-fc", "--force-cleanup", action="store_true", help="Force recleanup of raw data")
    parser.add_argument("-v", "--visualisation", action="store_true", help="Shows graphs from presentations")
    parser.add_argument("-sv", "--save-visualisation", action="store_true", help="Saves graphs from presentations to png files")
    
    parser.add_argument("-r", "--regression", action="store_true", help="Runs logistic regression.")
    parser.add_argument("-sr", "--save-regression", action="store_true", help="Runs logistic regression and saves model and graphs of model.")


    args = parser.parse_args()
    
    if args.corr_method not in ('pearson', 'kendall', 'spearman'):
        raise Exception("Correlation method should be one of these values: ('pearson', 'kendall', 'spearman').")
    
    if args.config and not os.path.exists(args.config):
        print(args.config)
        raise Exception("Custom config file doesn't exist.")
    
    db = FFC_DB(config=args.config)

    if not db.is_downloaded or args.force_download:
        db.download_xlsx()
    
    if not db.is_cleaned or args.force_cleanup:
        db.clean_data()
    
    df = db.get_clean_data()

    if args.correlation:
       db.save_correlations(df, method=args.corr_method) 

    material_data = prepare_data_for_material_plots(df)

    if args.save_visualisation:
        plot_material_count(material_data, save=True)    
        plot_hazardous_count(material_data, save=True)    
        plot_hazardous_percentage(material_data, save=True)    
        plot_hazardous_pie_chart(df, save=True)

    if args.visualisation:
        plot_material_count(material_data)    
        plot_hazardous_count(material_data)    
        plot_hazardous_percentage(material_data)    
        plot_hazardous_pie_chart(df)
    
    if args.regression or args.save_regression:
        db.run_regression(df, args.save_regression)

        
    input("Press enter to close script.")
if __name__ == "__main__":
    main()

