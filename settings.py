import os


DATA_DIR = "data"
DATA_FILES = {
    "profile": os.path.join(DATA_DIR, "profile.json"),
    "tasks": os.path.join(DATA_DIR, "tasks.json"),
    "rewards": os.path.join(DATA_DIR, "rewards.json"),
    "history": os.path.join(DATA_DIR, "history.json"),
    "settings": os.path.join(DATA_DIR, "settings.json"),
}
DATA_FILE = DATA_FILES["tasks"]

PRIORITY_POINTS = {
    "Baixa": 5,
    "Media": 10,
    "Alta": 20,
}

PRIORITY_ORDER = {
    "Alta": 0,
    "Media": 1,
    "Baixa": 2,
}

CATEGORIES = (
    "Estudos",
    "Trabalho",
    "Saude",
    "Casa",
    "Lazer",
    "Outros",
)

FILTERS = (
    "Todas",
    "Pendentes",
    "Concluidas",
)

XP_PER_LEVEL = 100
DEFAULT_DAILY_GOAL_POINTS = 30
MIN_DAILY_GOAL_POINTS = 5
MAX_DAILY_GOAL_POINTS = 500
