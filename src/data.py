import logging
import os

import pandas as pd
import requests

DATA_FILE_NAME = "data.xlsx"
SHEET_NAME = "FCCdb_FINAL_LIST"
API_RECORD_URL = "https://zenodo.org/api/records/4296944"
API_XL_DATA_URL = "https://zenodo.org/api/files/9b157c7a-93cc-4812-aeff-3c1fe71dbafd/FCCdb_201130_v5_Zenodo.xlsx"


def get_data(force_download: bool = False) -> pd.DataFrame:
    is_downloaded = os.path.exists(DATA_FILE_NAME)

    if is_downloaded and not force_download:
        logging.info(f"Reading data from local file {DATA_FILE_NAME}")
        return pd.read_excel(DATA_FILE_NAME, engine="openpyxl", sheet_name=SHEET_NAME)

    logging.info("Downloading data from site")
    headers = {"Content-Type": "application/json"}
    resp = requests.get(API_XL_DATA_URL, headers=headers)

    if not resp.status_code == 200:
        logging.info(f"Request status code is not OK. Status code: {resp.status_code}")
        return None

    logging.info(f"Writing data to file {DATA_FILE_NAME}")
    with open(DATA_FILE_NAME, "wb") as xl_file:
        xl_file.write(resp.content)

    logging.info("Reading downloaded data to DataFrame")
    return pd.read_excel(DATA_FILE_NAME, engine="openpyxl", sheet_name=SHEET_NAME)
