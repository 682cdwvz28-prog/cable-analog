from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import pandas as pd

app = FastAPI()

# Загружаем Excel при старте
df = pd.read_excel("cables.xlsx")


@app.get("/api/analogs")
def get_analogs(name: str):
    row = df[df["Cable"].str.lower() == name.lower()]

    if row.empty:
        return {"cable": name, "analogs": []}

    analogs = row.iloc[0].drop("Cable").dropna().tolist()

    return {"cable": name, "analogs": analogs}


# Раздаём статические файлы ПОСЛЕ API
app.mount("/", StaticFiles(directory="static", html=True), name="static")
