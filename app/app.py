from flask import Flask, jsonify, request, render_template
from app.db_loader import seed_from_json, create_table
from app.db_manager import get_recipes, search_recipes
import os

app = Flask(__name__, template_folder='../templates', static_folder='../static')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/init')
def init():
    create_table() 
    seed_from_json(force=True) 
    return jsonify({"message": "Database seeded successfully"})

@app.route('/api/recipes')
def api_recipes():
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)
    return jsonify(get_recipes(page=page, limit=limit))

@app.route('/api/recipes/search')
def api_search():
    params = {
        "calories": request.args.get('calories'),
        "title": request.args.get('title'),
        "cuisine": request.args.get('cuisine'),
        "total_time": request.args.get('total_time'),
        "rating": request.args.get('rating'),
        "limit": request.args.get('limit', 15, type=int),
        "page": request.args.get('page', 1, type=int)
    }
    return jsonify({"data": search_recipes(params)})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    create_table()
    seed_from_json(force=False)
    app.run(host='0.0.0.0', port=port, debug=True)