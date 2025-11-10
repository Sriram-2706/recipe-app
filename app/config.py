import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR,"..",'data')
RAW_JSON_PATH = os.path.join(DATA_DIR, 'recipes.json')
DB_PATH = os.path.join(DATA_DIR, 'recipes.db')
