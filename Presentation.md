---
marp: true
theme: gaia
class: invert
---

# Analiza danych FFCdb

Wykonana przez: 
Jakuba Melzackiego i Bartosza Jakubowskiego

---

## 1. Środowisko programistyczne
* Zdecydowaliśmy się na użycie VisualStudioCode + domyślne wirtualne środowisko Python 3.11
* Za pomocą środowiska testowego zainstalowaliśmy potrzebne nam paczki:
    - `requests` - Pobranie danych
    - `pandas` (w tym `numpy`) - Analiza i przygotowanie danych
    - `matplotlib`- Wizualizacja
    - Resztę paczek można znaleźć w pliku `requirements.txt`
    
---

## 2. Pobieranie danych

Do pobierania danych wykorzystaliśmy bibliotekę `requests` i wystawione API przez `zenodo`
```python
def download_xlsx(self) -> None:
        headers = {"Content-Type": "application/json"}
        resp = requests.get(self.config.get("api_xl_url"), headers=headers)

        if not resp.status_code == 200:
            return

        with open(self.config.get("ffc_db_file"), "wb") as xl_file:
            xl_file.write(resp.content)
```

---

## 3. Praca z danymi

Punkt 3. składa się z 6 podpunktów przez, które przejdziemy na kolejnych slajdach

---

### 3.a Wczytanie FCCdb_FINAL_LIST do odpowiedniej struktury danych.




---