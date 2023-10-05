import logging
import os
import re
import tomllib
import warnings

import joblib
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, roc_curve, auc
from sklearn.linear_model import LogisticRegression
import numpy as np
import pandas as pd
import requests

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

class FFC_DB:
    YES = "yes"
    NO = "no"
    NOT_LISTED = "not listed"

    def __init__(self) -> None:
        with open("constants.toml", "rb") as f:
            self.config = tomllib.load(f)
        
        if not os.path.exists(self.config.get("data_folder")):
            os.mkdir(self.config.get("data_folder"))

    @property
    def is_downloaded(self) -> bool:
        return os.path.exists(self.config.get("ffc_db_file"))
    
    @property
    def is_cleaned(self) -> bool:
        return os.path.exists(self.config.get("cleaned_file"))

    def download_xlsx(self) -> None:
        headers = {"Content-Type": "application/json"}
        resp = requests.get(self.config.get("api_xl_url"), headers=headers)

        if not resp.status_code == 200:
            return

        logging.info(f"Writing data to file {self.config.get('ffc_db_file')}")
        with open(self.config.get("ffc_db_file"), "wb") as xl_file:
            xl_file.write(resp.content)

    def clean_data(self) -> None:
        if not self.is_downloaded:
            return
        
        warnings.simplefilter(action='ignore', category=pd.errors.PerformanceWarning)

        df = pd.read_excel(self.config.get("ffc_db_file"), engine="openpyxl", sheet_name=self.config.get("data_sheet_name") )

        cleaned_df = pd.DataFrame()

        self._clean_most_valuable_columns(df, cleaned_df)
        
        self._clean_sources(df, cleaned_df)
        self._clean_lists_columns(df, cleaned_df)

        cleaned_df.to_csv(self.config.get("cleaned_file"))

    def _clean_most_valuable_columns(self, df: pd.DataFrame, new_df: pd.DataFrame) -> None:
        new_df["CAS validity"] = df["CAS \nvalidity"].str.startswith("valid")
        new_df["CAS/CFSAN number"] = df["CAS \nnumber or CFSAN id"]
        new_df["Name"] = df["Name"]
        new_df["Synonyms"] = df["Synonyms, \nas used by other sources"]
        new_df["Hazardous auth"] = self._yes_no_column(df["Priority hazardous substance prioritized based on selected authoritative sources? + why"])
        new_df["Potential concern non-auth"] = self._yes_no_column(df["Substance of potential concern identified based on selected non-authoritative sources? + why"])
        new_df["ECHA: HH"] = pd.to_numeric(df["ECHA \nC&L: \nSUM HH"], errors="coerce")
        new_df["ECHA: ENVH"] = pd.to_numeric(df["ECHA \nC&L: SUM ENVH"], errors="coerce")
        new_df["ECHA: Signal Word"] = df["ECHA \nC&L: Signal Word"].where(df["ECHA \nC&L: Signal Word"] != self.NOT_LISTED)
        new_df["ECHA: Classification"] = df["ECHA \nC&L: \nClassification"].where(df["ECHA \nC&L: \nClassification"] != self.NOT_LISTED)
        new_df["GHS-J: HH"] = pd.to_numeric(df["GHS-J: \nSUM HH"], errors="coerce")
        new_df["GHS-J: ENVH"] = pd.to_numeric(df["GHS-J: \nSUM ENVH"], errors="coerce")
        new_df["GHS-J: Signal Word"] = df["GHS-J: \nSignal Word"].where(df["GHS-J: \nSignal Word"] != self.NOT_LISTED)
        new_df["GHS-J: Classification"] = df["GHS-J: \nClassification"].where(df["GHS-J: \nClassification"] != self.NOT_LISTED)

        new_df["GHS-aligned classifications"] = df["Danish \nEPA's predicted GHS-aligned classifications for HH or ENVH"].where(df["Danish \nEPA's predicted GHS-aligned classifications for HH or ENVH"] != self.NOT_LISTED)
        new_df["GHS-aligned HH priority"] = df["predicted priority HH: potential CMR substance based on the Danish EPA's predicted GHS-aligned classifications? + which classifications decisive"].where(df["predicted priority HH: potential CMR substance based on the Danish EPA's predicted GHS-aligned classifications? + which classifications decisive"] != self.NOT_LISTED)
        new_df["GHS-aligned ENVH priority"] = df["predicted priority ENVH: Class 1 Aq. Chronic with or without Aq. Acute 1 toxicant based on the Danish EPA's predicted GHS-aligned classifications? + which classifications decisive"].where(df["predicted priority ENVH: Class 1 Aq. Chronic with or without Aq. Acute 1 toxicant based on the Danish EPA's predicted GHS-aligned classifications? + which classifications decisive"] != self.NOT_LISTED)
        new_df["max_tonnage"] = [self._get_max_tonnage(val) for val in df["Registered under REACH? + tonnage"]]
        new_df["min_tonnage"] = [self._get_min_tonnage(val) for val in df["Registered under REACH? + tonnage"]]
        new_df["CPPdb food contact"] = [self._has_fc(x) for x in df["included in the CPPdb?\n + List A or B status and if considered fc (assessed for ListA only)"]]
        new_df["SIN food contact"] = df["SIN \nList's use groups"].str.contains("food", case=False)
        new_df["food_contact"] = new_df["SIN food contact"] or new_df["CPPdb food contact"]
        
        new_df["SIN groups"] = df["SIN \nList's use groups"]
        new_df["PMT/vPvM UBA"] = df["PMT/vPvM classification by UBA 2019 report + Assessment quality"]
        self._clean_material_info(df, new_df)



    def _clean_lists_columns(self, df: pd.DataFrame, new_df: pd.DataFrame):
        new_df["EDC REACH"] = self._yes_no_column(df["EDC,  REACH classification"])
        new_df["EDC EU"] = self._yes_no_column(df["Included on the EU Endocrine Disruptor Lists? + List type"])
        new_df["EDC ECHA"] = self._yes_no_column(df["Included on the ECHA's Endocrine disruptor assessment list? + Status + Outcome + Follow-up + Authority"])
        new_df["EDC UNEP"] = self._yes_no_column(df["EDC included in \n2018 UNEP report?"])
        new_df["EDC TEDX"] = self._yes_no_column(df["EDC \non TEDX list?"])
        new_df["EDC REACH/Biociedes requlations"] = self._yes_no_column(df["EDC recognized in the EU under REACH or Biocides regulation"])
        new_df["PBT/vPvB/POP EU US"] = self._yes_no_column(df["PBT \nor vPvB or POP? (EU, US)"])
        new_df["PBT ECHA"] = self._yes_no_column(df["On ECHA's PBT assessment list? + Status + Outcome + Follow-up + Assessment date + Authority"])
        new_df["SVHC REACH"] = self._yes_no_column(df["On EU \nREACH \nSVHC list (Candidate list for authorization)? + reasons for inclusion"])
        new_df["Authorization list REACH"] = self._yes_no_column(df["On EU \nREACH \nAuthorization list, Annex XIV? + reasons for inclusion"])
        new_df["Restriction list REACH"] = self._yes_no_column(df["On EU \nREACH Restriction list, Annex XVII? + entry number"])
        new_df["Cal Prop65"] = self._yes_no_column(df["on Cal \nProp65 List? + indicated toxicity"])
        new_df["CoRAP EU"] = self._yes_no_column(df["on EU CoRAP list? + Status + Initial grounds for concern + Year + Evaluating Member State"])
        new_df["OpenFoodToxDB EFSA"] = self._yes_no_column(df["In EFSA's Open Food Tox database?"])
        new_df["Genotoxicity OFTDB EFSA"] = df["Genotoxicity Calls from EFSA OpenFoodTox database"]
        new_df["SCI EPA"] = self._yes_no_column(df["on EPA's \nsafer \nchemical ingredients \nlist?"])
        new_df["Genotoxic concer by van Bossuyt"] = self._yes_no_column(df["Substances \nof genotoxic concern, prioritized by van Bossuyt et al. 2017, 2018"])
        new_df["SIN"] = self._yes_no_column(df["on \nSIN list?\n + reasons for inclusion"])
        new_df["ToxValDB"] = self._yes_no_column(df["In ToxVal\ndatabase? + N DataSources; N PubmedArticles; N PubchemDataSources; N CPDatCount"])
        new_df["Registerd REACH"] = self._yes_no_column(df["Registered under REACH? + tonnage"])
        new_df["Chemical Universe Mapping REACH"] = self._yes_no_column(df["on the REACH Chemical Universe Mapping list? + Tonnage + Registration Status + Position in the chemical universe"])
        new_df["Plastics additives ECHA"] = self._yes_no_column(df["on ECHA's \nplastics additives list? + main function indicated by ECHA"])
        new_df["CPPdb"] = self._yes_no_column(df["included in the CPPdb?\n + List A or B status and if considered fc (assessed for ListA only)"])
        new_df["TSCA"] = self._yes_no_column(df["on TSCA \ninventory? + status"])
        new_df["NZIOC"] = self._yes_no_column(df["on New \nZealand list of chemicals (NZIOC)? + conditions"])   

    def _clean_material_info(self, df: pd.DataFrame, new_df: pd.DataFrame) -> None:
        for col_name in df.columns:
            if match := re.match(r"^Global \nInventory: (.+)$", col_name):
                material = match.group(1)
                new_df[material] = df[col_name] != 0

        new_df["Usage count"] = df["N global \nFCM inventories where included"].astype(int)

    def _clean_sources(self, df: pd.DataFrame, new_df: pd.DataFrame) -> None:
        for col_name in df.columns:
            if match := re.match(r"^S(\d+)$", col_name):
                new_df[col_name] = df[col_name] != 0

        new_df["Ref count"] = df["N sources \nthat mention this chemical"].astype(int)


    def _get_max_tonnage(self, val: str) -> float:
        result = 0.0
        for value in val.split("; "):
            if match := re.match(r"(\d+)\s*-\s*(\d+)", value):
                result = max(result, float(match.group(2)))
            
            if match := re.match(r"(\d+)\+?", value):
                result = max(result, float(match.group(1)))

        return result
    
    def _get_min_tonnage(self, val: str) -> float:
        result = 0.0
        for value in val.split("; "):
            if match := re.match(r"(\d+)\s*-\s*(\d+)", value):
                result = max(result, float(match.group(1)))
            
            if match := re.match(r"(\d+)\+?", value):
                result = max(result, float(match.group(1)))

        return result

    def _has_fc(self, val: str) -> bool:
       if val.endswith(self.NO):
           return False
       
       fc_check = val.split(';')
       
       if len(fc_check) < 3:
           return False
       
       return True
       
 
    def _yes_no_column(self, series: pd.Series) -> pd.Series:
        return series.str.startswith(self.YES)

    def get_clean_data(self) -> pd.DataFrame:
        return pd.read_csv(self.config.get("cleaned_file"))
    
    def save_correlations(self, df: pd.DataFrame = None, method: str = "pearson"):
        correlation_matrix = df.select_dtypes(exclude='object').corr(method=method)
        correlation_matrix.to_csv(f"correlations_{method}.csv")

    def prepare_data_to_logistic_regression(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.select_dtypes(exclude="object")
        df = df.loc[:, MATERIALS + ['food_contact'] ]
        df.to_csv("temp.csv")
        return df

    def run_regression(self, df: pd.DataFrame, save_model: bool = False) -> None:
        data_to_regression = self.prepare_data_to_logistic_regression(df)
        X = data_to_regression.drop(columns=['food_contact'])
        y = data_to_regression['food_contact']
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
        
        clf = LogisticRegression(max_iter=1000)
        clf.fit(X_train, y_train)

        y_pred = clf.predict(X_test)

        accuracy = accuracy_score(y_test, y_pred)
        print(f"Accuracy of regression: {100 * accuracy:.2f}%")
        self.plot_regression_results(clf, X_test, y_test, y_pred, save_model)

        if save_model:
            joblib.dump(clf, "model.joblib")
        

    def plot_regression_results(self, clf: LogisticRegression, X_test: pd.DataFrame, y_test: pd.Series, y_pred: np.ndarray, save_model: bool = False) -> None:
        if save_model:
            self.plot_confiusion_matrix(y_test, y_pred, True)
            self.plot_ROC(clf, X_test, y_test, True)
            return

        self.plot_confiusion_matrix(y_test, y_pred)
        self.plot_ROC(clf, X_test, y_test)

    def plot_confiusion_matrix(self, y_test: pd.Series, y_pred: np.ndarray, save_model: bool = False) -> None:
        cm = confusion_matrix(y_test, y_pred)
        plt.figure(figsize=(8,6))
        sns.heatmap(cm, annot=True, fmt='g', cmap='Blues', cbar=False)
        plt.xlabel('Predicted labels')
        plt.ylabel('True labels')
        plt.title('Confusion Matrix')

        if save_model:
            plt.savefig("confiusion_matrix.png")
            return
        
        plt.show(block=False)
        plt.pause(0.2)

    def plot_ROC(self, clf: LogisticRegression, X_test: pd.DataFrame, y_test: pd.Series, save_model: bool = False):
        y_prob = clf.predict_proba(X_test)[:, 1]
        fpr, tpr, thresholds = roc_curve(y_test, y_prob)
        roc_auc = auc(fpr, tpr)

        plt.figure(figsize=(8,6))
        plt.plot(fpr, tpr, color='darkorange', label=f'ROC curve (area = {roc_auc:.2f})')
        plt.plot([0, 1], [0, 1], color='navy', linestyle='--')
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title('Receiver Operating Characteristic (ROC) Curve')
        plt.legend(loc='lower right')
        
        if save_model:
            plt.savefig("ROC.png")
            return
        
        plt.show(block=False)
        plt.pause(0.2)


