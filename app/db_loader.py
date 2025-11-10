import json
import sqlite3
import re
import pandas as pd
import numpy as np
from .config import RAW_JSON_PATH, DB_PATH

def clean_numeric_data(df):
    numeric_cols = ['rating', 'prep_time', 'cook_time', 'total_time']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            df[col] = df[col].replace([np.inf, -np.inf], np.nan)
    return df

def validate_and_fix_times(df):
    def _fix_row_times(row):
        prep = row.get('prep_time')
        cook = row.get('cook_time')
        total = row.get('total_time')
        
        prep_num = pd.to_numeric(prep, errors='coerce') if prep is not None else np.nan
        cook_num = pd.to_numeric(cook, errors='coerce') if cook is not None else np.nan
        total_num = pd.to_numeric(total, errors='coerce') if total is not None else np.nan
        
        calculated_total = prep_num + cook_num
        
        if pd.isna(total_num) and not pd.isna(calculated_total):
            return prep_num, cook_num, calculated_total
        elif not pd.isna(total_num) and (pd.isna(prep_num) or pd.isna(cook_num)):
            return prep_num, cook_num, total_num
        elif not pd.isna(total_num) and not pd.isna(calculated_total):
            difference = abs(total_num - calculated_total)
            tolerance = max(30, calculated_total * 0.2)
            if difference > tolerance:
                return prep_num, cook_num, calculated_total
            else:
                return prep_num, cook_num, total_num
        else:
            return prep_num, cook_num, total_num
    
    fixed_times = df.apply(_fix_row_times, axis=1, result_type='expand')
    df[['prep_time', 'cook_time', 'total_time']] = fixed_times
    return df

def extract_calories(nutrients_series):
    def _extract(nutrients):
        if not nutrients or not isinstance(nutrients, dict):
            return None
        calories_str = nutrients.get('calories', '')
        if not calories_str:
            return None
        match = re.search(r'(\d+)', str(calories_str))
        return int(match.group(1)) if match else None
    
    return nutrients_series.apply(_extract)

def create_table():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS recipes(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            continent TEXT,
            country_state TEXT,
            cuisine TEXT,
            title TEXT,
            url TEXT,
            rating REAL,
            prep_time INTEGER,
            cook_time INTEGER,
            total_time INTEGER,
            description TEXT,
            ingredients TEXT,
            instructions TEXT,
            nutrients TEXT,
            calories_int INTEGER,
            serves TEXT
        )
    """)
    conn.commit()
    conn.close()
    print("Table 'recipes' created successfully")
    
    
def seed_from_json(force=False):
    create_table()
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT count(1) FROM recipes")
    exists = c.fetchone()[0] > 0
    
    if exists and not force:
        conn.close()
        return
    
    with open(RAW_JSON_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    recipes_list = []
    for recipe_id, recipe_data in data.items():
        recipe_data['id'] = recipe_id
        recipes_list.append(recipe_data)
    
    df = pd.DataFrame(recipes_list)
    
    df = clean_numeric_data(df)
    df = validate_and_fix_times(df)
    
    if 'nutrients' in df.columns:
        df['calories_int'] = extract_calories(df['nutrients'])
    
    df['nutrients_text'] = df['nutrients'].apply(
        lambda x: json.dumps(x, ensure_ascii=False) if x and isinstance(x, dict) else '{}'
    )
    
    df['ingredients_text'] = df['ingredients'].apply(
        lambda x: json.dumps(x, ensure_ascii=False) if x and isinstance(x, list) else '[]'
    )
    
    df['instructions_text'] = df['instructions'].apply(
        lambda x: json.dumps(x, ensure_ascii=False) if x and isinstance(x, list) else '[]'
    )
    
    text_columns = ['continent', 'country_state', 'cuisine', 'title', 'url', 'description', 'serves']
    for col in text_columns:
        if col in df.columns:
            df[col] = df[col].fillna('')
    
    c.execute("DELETE FROM recipes")
    
    for _, row in df.iterrows():
        c.execute("""
            INSERT INTO recipes(continent, country_state, cuisine, title, url, rating, prep_time, cook_time, total_time, description, ingredients, instructions, nutrients, calories_int, serves)
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            row.get('Continent') or row.get('continent') or '',
            row.get('Country_State') or row.get('country_state') or '',
            row.get('cuisine') or '',
            row.get('title') or '',
            row.get('URL') or row.get('url') or '',
            row.get('rating'),
            row.get('prep_time'),
            row.get('cook_time'),
            row.get('total_time'),
            row.get('description') or '',
            row.get('ingredients_text') or '[]',
            row.get('instructions_text') or '[]',
            row.get('nutrients_text') or '{}',
            row.get('calories_int'),
            row.get('serves') or ''
        ))
    
    conn.commit()
    conn.close()