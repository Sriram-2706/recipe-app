import sqlite3
import json
from .config import DB_PATH

def _row_to_dict(r):
    nutrients = {}
    ingredients = []
    instructions = []
    
    try:
        if r[13] and r[13] != '{}':
            nutrients = json.loads(r[13])
    except:
        nutrients = {}
    
    try:
        if r[11] and r[11] != '[]':
            ingredients = json.loads(r[11])
    except:
        ingredients = []
    
    try:
        if r[12] and r[12] != '[]':
            instructions = json.loads(r[12])
    except:
        instructions = []
    
    return {
        "id": r[0],
        "continent": r[1] if r[1] else "Not Available",
        "country_state": r[2] if r[2] else "Not Available",
        "cuisine": r[3] if r[3] else "Not Available",
        "title": r[4] if r[4] else "Untitled Recipe",
        "url": r[5] if r[5] else "",
        "rating": r[6],
        "prep_time": r[7],
        "cook_time": r[8],
        "total_time": r[9],
        "description": r[10] if r[10] else "No description available",
        "ingredients": ingredients,
        "instructions": instructions,
        "nutrients": nutrients,
        "calories_int": r[14],
        "serves": r[15] if r[15] else "Not specified"
    }

def get_recipes(page=1, limit=10):
    offset = (page - 1) * limit
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT COUNT(1) FROM recipes")
    total = c.fetchone()[0]
    q = """SELECT id, continent, country_state, cuisine, title, url, rating, prep_time, cook_time, total_time, 
                  description, ingredients, instructions, nutrients, calories_int, serves 
           FROM recipes 
           ORDER BY CASE WHEN rating IS NULL THEN 1 ELSE 0 END, rating DESC 
           LIMIT ? OFFSET ?"""
    c.execute(q, (limit, offset))
    rows = c.fetchall()
    conn.close()
    data = [_row_to_dict(r) for r in rows]
    return {"page": page, "limit": limit, "total": total, "data": data}

def _parse_op_val(s):
    if not s: return None
    s = str(s).strip()
    ops = {">=", "<=", "!=", "=", "<", ">"}
    for op in ops:
        if s.startswith(op):
            try:
                return op, float(s[len(op):])
            except:
                return None
    if s[0] in "<>=":
        op = s[0]
        val = s[1:]
        try:
            return op, float(val)
        except:
            return None
    try:
        return "=", float(s)
    except:
        return None

def search_recipes(params):
    clauses = []
    args = []
    
    if params.get("title"):
        t = params["title"].strip()
        clauses.append("(title LIKE ? OR title IS NULL)")
        args.append(f"%{t}%")
    
    if params.get("cuisine"):
        c = params["cuisine"].strip()
        clauses.append("(cuisine LIKE ? OR cuisine IS NULL)")
        args.append(f"%{c}%")
    
    if params.get("total_time"):
        pv = _parse_op_val(params["total_time"])
        if pv:
            op, val = pv
            clauses.append(f"(total_time {op} ? OR total_time IS NULL)")
            args.append(int(val))
    
    if params.get("rating"):
        pv = _parse_op_val(params["rating"])
        if pv:
            op, val = pv
            clauses.append(f"(rating {op} ? OR rating IS NULL)")
            args.append(float(val))
    
    if params.get("calories"):
        pv = _parse_op_val(params["calories"])
        if pv:
            op, val = pv
            clauses.append(f"(calories_int {op} ? OR calories_int IS NULL)")
            args.append(int(val))
    
    where = (" WHERE " + " AND ".join(clauses)) if clauses else ""
    limit = int(params.get("limit", 50))
    page = int(params.get("page", 1))
    offset = (page - 1) * limit
    
    q = f"""SELECT id, continent, country_state, cuisine, title, url, rating, prep_time, cook_time, total_time, 
                   description, ingredients, instructions, nutrients, calories_int, serves 
            FROM recipes {where} 
            ORDER BY CASE WHEN rating IS NULL THEN 1 ELSE 0 END, rating DESC 
            LIMIT ? OFFSET ?"""
    
    args.extend([limit, offset])
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(q, tuple(args))
    rows = c.fetchall()
    conn.close()
    return [_row_to_dict(r) for r in rows]