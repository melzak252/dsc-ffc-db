import logging
import os
import re

import pandas as pd
import requests

DATA_FILE_NAME = "data/FFCdb.xlsx"
CLEANDED_DATA = "data/FFCdb_clean.csv"
SHEET_NAME = "FCCdb_FINAL_LIST"
API_RECORD_URL = "https://zenodo.org/api/records/4296944"
API_XL_DATA_URL = "https://zenodo.org/api/files/9b157c7a-93cc-4812-aeff-3c1fe71dbafd/FCCdb_201130_v5_Zenodo.xlsx"
COLS_TO_DROP = [
    """Synonyms, 
as used by other sources""",
    """ECHA 
C&L: Pictograms""",
    """GHS-J: 
Pictograms""",
    """Use in specific FCMs or other type of fc application: Defined (from at least one source) or Undefined use"""
]

class FFC_DB:
    @property
    def is_downloaded(self) -> bool:
        return os.path.exists(DATA_FILE_NAME)

    def download_xlsx(self) -> None:
        logging.info("Downloading data from API")
        headers = {"Content-Type": "application/json"}
        resp = requests.get(API_XL_DATA_URL, headers=headers)

        if not resp.status_code == 200:
            logging.info(
                f"Request status code is not OK. Status code: {resp.status_code}"
            )
            return

        logging.info(f"Writing data to file {DATA_FILE_NAME}")
        with open(DATA_FILE_NAME, "wb") as xl_file:
            xl_file.write(resp.content)

    def clean_data(self) -> None:
        if not self.is_downloaded:
            return

        df = pd.read_excel(DATA_FILE_NAME, engine="openpyxl", sheet_name=SHEET_NAME)
        new_df = pd.DataFrame()

        self._fill_CAS_numbers(df, new_df)

        new_df["Hazardous auth"] = df["Priority hazardous substance prioritized based on selected authoritative sources? + why"].str.split(";").str.get(0) == "yes"
        new_df["Potential concern non-auth"] = df["Substance of potential concern identified based on selected non-authoritative sources? + why"].str.split(";").str.get(0) == "yes"
        new_df["ECHA: HH"] = pd.to_numeric(df["ECHA \nC&L: \nSUM HH"], errors="coerce")
        new_df["ECHA: ENVH"] = pd.to_numeric(df["ECHA \nC&L: SUM ENVH"], errors="coerce")
        new_df["ECHA: Signal Word"] = df["ECHA \nC&L: Signal Word"].where(df["ECHA \nC&L: Signal Word"] != "not listed")
        new_df["GHS-J: HH"] = pd.to_numeric(df["GHS-J: \nSUM HH"], errors="coerce")
        new_df["GHS-J: ENVH"] = pd.to_numeric(df["GHS-J: \nSUM ENVH"], errors="coerce")
        new_df["GHS-J: Signal Word"] = df["GHS-J: \nSignal Word"].where(df["GHS-J: \nSignal Word"] != "not listed")

        self._replace_material_info(df, new_df)

        # new_df.to_excel("data/cleaned.xlsx", engine="openpyxl")
        new_df.to_csv(CLEANDED_DATA)

    def _fill_CAS_numbers(self, df: pd.DataFrame, new_df: pd.DataFrame):
        name = "CAS \nvalidity"
        new_df["CAS validity"] = df[name].str.split(" ").str.get(0) == "valid"
        new_df["CAS/CFSAN number"] = df["CAS \nnumber or CFSAN id"]

    def _replace_material_info(self, df: pd.DataFrame, new_df: pd.DataFrame):
        for col_name in list(df.columns):
            if match := re.match(r"^Global \nInventory: (.+)$", col_name):
                material = match.group(1)

                new_df[material] = df[col_name] != 0
                
        new_df["Usage count"] = df["N global \nFCM inventories where included"].astype(int)

    def get_clean_data(self) -> pd.DataFrame:
        return pd.read_csv(CLEANDED_DATA)