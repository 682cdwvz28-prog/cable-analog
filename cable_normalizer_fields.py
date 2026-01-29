# cable_normalizer_fields.py
import re

# -----------------------------
# Универсальный нормализатор кабельных наименований с разбором на поля
# -----------------------------

# Канонический порядок модификаторов (составные модификаторы идут раньше)
MODS_ORDER = ['нг', 'frls', 'fr', 'lsltx', 'ls', 'hf']

# Латиница → кириллица (только визуально похожие буквы)
LAT2CYR = str.maketrans({
    'a': 'а',
    'b': 'в',
    'c': 'с',
    'e': 'е',
    'h': 'н',
    'k': 'к',
    'm': 'м',
    'o': 'о',
    'p': 'р',
    't': 'т',
    'x': 'х',
    'v': 'в',
})

def normalize_cable_fields(name: str) -> dict:
    """
    Универсальный нормализатор кабельных наименований.
    Разбивает на два поля:
    - base — тип кабеля (ввг, кввг, ппг …)
    - mods — список модификаторов (нг, frls, ls …)
    
    Работает с:
    - латиницей/кириллицей
    - составными модификаторами frls, lsltx
    - скобками (А)
    - лишними пробелами и дефисами
    - точечным схлопыванием ББшв
    """

    if not name:
        return {'base': '', 'mods': []}

    # приведение к нижнему регистру
    name = name.lower()

    # латиница → кириллица
    name = name.translate(LAT2CYR)

    # убрать скобки (А), (B)
    name = re.sub(r'\(.*?\)', '', name)

    # убрать все пробелы
    name = re.sub(r'\s+', '', name)

    # убрать дефисы
    name = name.replace('-', '')

    # нормализация составных модификаторов
    replacements = {
        'fr-ls': 'frls',
        'fr ls': 'frls',
        'ls-ltx': 'lsltx',
        'ls ltx': 'lsltx',
    }
    for k, v in replacements.items():
        name = name.replace(k, v)

    # точечное схлопывание "ББшв" → "БШВ"
    name = re.sub(r'бб(?=шв)', 'б', name)

    # оставить только кириллицу и цифры
    name = re.sub(r'[^а-я0-9]', '', name)

    # выделяем модификаторы
    mods_found = []
    base = name
    for mod in MODS_ORDER:
        if mod in base:
            mods_found.append(mod)
            base = base.replace(mod, '')

    return {'base': base, 'mods': mods_found}


# -----------------------------
# Пример теста при запуске
# -----------------------------
if __name__ == "__main__":
    tests = [
        "ВВГнг-LS",
        "ВВГ нг (А) FR LS",
        "ВВГFRLS",
        "ВББшвнг-fr ls",
        "VbBShv NG-FR-LS",
        "КВВГнг-lsltx",
        "KVVG NG LS-LTX",
        "АББГ",
        "В В Г  н г",
        "В  ВГ   нг   -   LS",
        "V V G  NG -  L S",
    ]

    for t in tests:
        result = normalize_cable_fields(t)
        print(f"{t:35} → {result}")