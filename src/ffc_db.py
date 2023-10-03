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


class FFC_DB:
    @property
    def is_downloaded(self) -> bool:
        return os.path.exists(DATA_FILE_NAME)
    
    @property
    def is_cleaned(self) -> bool:
        return os.path.exists(CLEANDED_DATA)

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

        self._clean_edc_lists(df, new_df)
        self._replace_material_info(df, new_df)
        self.food_contact_clean(df,new_df)

        # new_df.to_excel("data/cleaned.xlsx", engine="openpyxl")
        new_df.to_csv(CLEANDED_DATA)

    def _replace_material_info(self, df: pd.DataFrame, new_df: pd.DataFrame) -> None:
        for col_name in df.columns:
            if match := re.match(r"^Global \nInventory: (.+)$", col_name):
                material = match.group(1)
                new_df[material] = df[col_name] != 0

        new_df["Usage count"] = df["N global \nFCM inventories where included"].astype(int)


    def _clean_edc_lists(self, df: pd.DataFrame, new_df: pd.DataFrame) -> None:
        new_df["CAS validity"] = df["CAS \nvalidity"].str.startswith("valid")
        new_df["CAS/CFSAN number"] = df["CAS \nnumber or CFSAN id"]
        
        new_df["Hazardous auth"] = self._yes_no_column(df["Priority hazardous substance prioritized based on selected authoritative sources? + why"])
        new_df["Potential concern non-auth"] = self._yes_no_column(df["Substance of potential concern identified based on selected non-authoritative sources? + why"])
        new_df["ref_count"] = df["N sources \nthat mention this chemical"].astype(int)
        new_df["ECHA: HH"] = pd.to_numeric(df["ECHA \nC&L: \nSUM HH"], errors="coerce")
        new_df["ECHA: ENVH"] = pd.to_numeric(df["ECHA \nC&L: SUM ENVH"], errors="coerce")
        new_df["ECHA: Signal Word"] = df["ECHA \nC&L: Signal Word"].where(df["ECHA \nC&L: Signal Word"] != "not listed")
        new_df["ECHA: Classification"] = df["ECHA \nC&L: \nClassification"].where(df["ECHA \nC&L: \nClassification"] != "not listed")
        new_df["GHS-J: HH"] = pd.to_numeric(df["GHS-J: \nSUM HH"], errors="coerce")
        new_df["GHS-J: ENVH"] = pd.to_numeric(df["GHS-J: \nSUM ENVH"], errors="coerce")
        new_df["GHS-J: Signal Word"] = df["GHS-J: \nSignal Word"].where(df["GHS-J: \nSignal Word"] != "not listed")
        new_df["GHS-J: Classification"] = df["GHS-J: \nClassification"].where(df["GHS-J: \nClassification"] != "not listed")

        new_df["GHS-aligned classifications"] = df["Danish \nEPA's predicted GHS-aligned classifications for HH or ENVH"].where(df["Danish \nEPA's predicted GHS-aligned classifications for HH or ENVH"] != 'not listed')
        new_df["GHS-aligned HH priority"] = df["predicted priority HH: potential CMR substance based on the Danish EPA's predicted GHS-aligned classifications? + which classifications decisive"].where(df["predicted priority HH: potential CMR substance based on the Danish EPA's predicted GHS-aligned classifications? + which classifications decisive"] != 'not listed')
        new_df["GHS-aligned ENVH priority"] = df["predicted priority ENVH: Class 1 Aq. Chronic with or without Aq. Acute 1 toxicant based on the Danish EPA's predicted GHS-aligned classifications? + which classifications decisive"].where(df["predicted priority ENVH: Class 1 Aq. Chronic with or without Aq. Acute 1 toxicant based on the Danish EPA's predicted GHS-aligned classifications? + which classifications decisive"] != 'not listed')
    
    def food_contact_clean(self,df: pd.DataFrame, new_df: pd.DataFrame) -> None:
        new_df["food_contact"] = [self.has_fc(x) for x in df["included in the CPPdb?\n + List A or B status and if considered fc (assessed for ListA only)"]]

    def has_fc(self,val: str):
       if val.endswith("no"):
           return False
       
       fc_check = val.split(';')
       
       if len(fc_check) < 3:
           return False
       
       return True
       
 
    def _yes_no_column(self, series: pd.Series) -> pd.Series:
        return series.str.startswith("yes")

    def get_clean_data(self) -> pd.DataFrame:
        return pd.read_csv(CLEANDED_DATA)
