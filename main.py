import pandas as pd
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from cable_normalizer_fields import normalize_cable_fields

app = FastAPI()

# -----------------------------
# Загружаем Excel
# -----------------------------
df = pd.read_excel("Cables.xlsx", dtype=str).fillna("")
df["Cable"] = df["Cable"].astype(str)

# -----------------------------
# Создаём NormCable
# -----------------------------
def build_norm_key(name: str) -> str:
    parsed = normalize_cable_fields(str(name))
    base = parsed.get("base", "")
    mods = parsed.get("mods", [])
    return (base + "".join(mods)).lower()

df["NormCable"] = df["Cable"].apply(build_norm_key)

analog_columns = [col for col in df.columns if col.startswith("Analog")]

# -----------------------------
# Статика
# -----------------------------
app.mount("/static", StaticFiles(directory="static"), name="static")

# -----------------------------
# Главная страница
# -----------------------------
@app.get("/", response_class=HTMLResponse)
def read_root():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return f.read()

# -----------------------------
# API автоподсказок
# -----------------------------
@app.get("/api/suggest")
def suggest(query: str):
    parsed = normalize_cable_fields(query)
    base = parsed.get("base", "")
    mods = parsed.get("mods", [])
    key = (base + "".join(mods)).lower()

    matches = df[df["NormCable"].str.startswith(key)]
    suggestions = matches["Cable"].unique().tolist()

    return {"suggestions": suggestions}

# -----------------------------
# API поиска аналогов
# -----------------------------
@app.get("/api/analogs")
def get_analogs(name: str):
    parsed = normalize_cable_fields(name)
    base = parsed.get("base", "")
    mods = parsed.get("mods", [])
    key = (base + "".join(mods)).lower()

    # 1) Строгое совпадение
    matches = df[df["NormCable"] == key]

    # 2) Если нет — fallback по base
    if matches.empty:
        matches = df[df["NormCable"].str.startswith(base)]

    analogs = []
    for _, row in matches.iterrows():
        for col in analog_columns:
            val = row[col]
            if val and isinstance(val, str) and val.strip():
                analogs.append(val)

    analogs = list(dict.fromkeys(analogs))

    return {
        "input": name,
        "normalized": key,
        "analogs": analogs
    }
