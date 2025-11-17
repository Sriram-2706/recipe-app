# Recipe Explorer Application

This is a Flask-based web application built as part of an assessment.  
The main idea is to load a large recipe dataset, clean the data, store it in an SQLite database, and expose the data through a set of API endpoints.  
A simple frontend is also included to make it easier to browse, search, and view recipe details.

---

## 1. Features

- Loads raw recipe data from a JSON file  
- Cleans and prepares the data using Pandas  
- Stores the processed data in an SQLite database  
- REST APIs for:
  - Pagination
  - Searching recipes using multiple filters
  - Viewing detailed recipe information
- Frontend built with HTML, CSS, and JavaScript
- Off-canvas drawer UI for recipe details
- Pagination controls on the frontend

---

## 2. Project Structure

```
RECIPE-APP/
│
├── app/
│   ├── __init__.py
│   ├── app.py              # Flask routes and API endpoints
│   ├── config.py           # Path configuration
│   ├── db_loader.py        # Loads and cleans data, inserts into DB
│   ├── db_manager.py       # Database querying functions
│
├── data/
│   ├── recipes.json        # Raw dataset
│   ├── recipes.db          # SQLite database (auto-created)
│
├── static/
│   ├── script.js           # Frontend logic
│   ├── style.css           # Basic styling
│
├── templates/
│   ├── index.html          # Main UI
│
├── requirements.txt
└── .gitignore
```



---

## 3. How the Application Works

### Data Processing  
The file `db_loader.py` reads the raw JSON file and performs several cleaning steps:
- Converts numeric fields properly  
- Handles missing values  
- Fixes inconsistent time fields  
- Extracts calorie information  
- Converts lists (like ingredients and instructions) into JSON strings for database storage

After cleaning, the data is inserted into an SQLite database (`recipes.db`).

### Backend  
The backend is written in Flask.  
`db_manager.py` contains the database helper functions for pagination and filtering.  
`app.py` exposes these through API routes.

### Frontend  
The UI is a basic HTML page (`index.html`) that uses Bootstrap and vanilla JavaScript.  
`script.js` handles fetching data from the API, updating the DOM, and displaying recipe details inside an off-canvas drawer.

---

## 4. API Endpoints

### `GET /init`
Loads the JSON data, cleans it, and creates the database.

### `GET /api/recipes?page=X&limit=Y`
Returns a paginated list of recipes.

### `GET /api/recipes/search`
Supports filtering by:
- title  
- cuisine  
- rating  
- calories  
- total_time  

Example:
/api/recipes/search?cuisine=Indian&rating>=4

---

## 5. Running the Project Locally

### 1. Create a virtual environment
python -m venv venv

### 2. Activate it  
Windows:
venv\Scripts\activate

### 3. Install packages  
pip install -r requirements.txt

### 4. Run the app  
python -m flask run

### 5. Initialize the database  
Open the browser and go to:
http://127.0.0.1:5000/init

### 6. Use the UI  
http://127.0.0.1:5000/

---

## 6. Notes

- The database file is created automatically when `/init` is called.  
- If you run into missing data, simply rerun the `/init` endpoint.  
- This project focuses on the backend logic, data processing, and clean API design rather than UI design.

---

## 7. Future Improvements

- Add filters for ingredients  
- Add user accounts and saved recipes  
- Add charts for nutritional analysis  
- Improve the UI with better layouts  
- Move to FastAPI for faster backend responses

