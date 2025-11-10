let curPage = 1;
let perPage = 15;
let totalCount = 0;
let prevPage = 1;
let nextPage = 1;

document.getElementById('perPage').value = '15';

async function load(page = 1) {
    perPage = parseInt(document.getElementById('perPage').value);
    curPage = page || 1;
    
    try {
        const res = await fetch(`/api/recipes?page=${curPage}&limit=${perPage}`);
        const data = await res.json();
        const recipes = data.data;
        totalCount = data.total;
        
        prevPage = Math.max(1, curPage - 1);
        nextPage = curPage + 1;
        
        displayRecipes(recipes, data);
    } catch (error) {
        console.error('Error loading recipes:', error);
    }
}

function displayRecipes(recipes, data) {
    const tbody = document.getElementById('tbody');
    const noResults = document.getElementById('noResults');
    
    tbody.innerHTML = '';
    
    if (!recipes.length) {
        noResults.style.display = 'block';
        document.getElementById('pageInfo').textContent = '';
        return;
    }
    
    noResults.style.display = 'none';
    
    recipes.forEach(recipe => {
        const tr = document.createElement('tr');
        tr.style.cursor = 'pointer';
        tr.innerHTML = `
            <td class="recipe-title" title="${recipe.title}">${recipe.title}</td>
            <td>${recipe.cuisine}</td>
            <td>${renderStars(recipe.rating)}</td>
            <td>${formatTime(recipe.total_time)}</td>
            <td>${recipe.serves}</td>
        `;
        tr.onclick = () => openDrawer(recipe);
        tbody.appendChild(tr);
    });
    
    document.getElementById('pageInfo').textContent = `Page ${curPage} of ${Math.ceil(data.total / perPage)} • ${data.total} total recipes`;
}

function formatTime(time) {
    if (!time && time !== 0) return 'N/A';
    if (typeof time === 'string') return time;
    return `${time} min`;
}

function renderStars(rating) {
    if (!rating && rating !== 0) return '<span class="text-muted">N/A</span>';
    if (typeof rating === 'string') return `<span class="text-muted">${rating}</span>`;
    
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 >= 0.5;
    const emptyStars = 5 - fullStars - (hasHalfStar ? 1 : 0);
    
    let stars = '';
    for (let i = 0; i < fullStars; i++) {
        stars += '<i class="fas fa-star star-rating"></i>';
    }
    if (hasHalfStar) {
        stars += '<i class="fas fa-star-half-alt star-rating"></i>';
    }
    for (let i = 0; i < emptyStars; i++) {
        stars += '<i class="far fa-star star-rating"></i>';
    }
    
    return stars + ` <small class="text-muted">(${rating.toFixed(1)})</small>`;
}

function openDrawer(recipe) {
    document.getElementById('drawerTitle').textContent = `${recipe.title} - ${recipe.cuisine}`;
    
    const nutrients = recipe.nutrients || {};
    const ingredients = recipe.ingredients || [];
    const instructions = recipe.instructions || [];
    
    document.getElementById('drawerBody').innerHTML = `
        <div class="mb-4">
            <h6 class="text-primary">Description</h6>
            <p class="mb-0">${recipe.description}</p>
        </div>
        
        <div class="mb-4">
            <h6 class="text-primary">Location</h6>
            <p class="mb-0">${recipe.continent}, ${recipe.country_state}</p>
        </div>
        
        <div class="mb-4">
            <h6 class="text-primary">Time Information</h6>
            <p class="mb-1"><strong>Total Time:</strong> ${formatTime(recipe.total_time)}</p>
            <button class="btn btn-sm btn-outline-secondary" onclick="toggleTimeDetails(this)">
                <i class="fas fa-chevron-down me-1"></i>Show Details
            </button>
            <div class="time-details mt-2" style="display: none;">
                <p class="mb-1"><strong>Prep Time:</strong> ${formatTime(recipe.prep_time)}</p>
                <p class="mb-0"><strong>Cook Time:</strong> ${formatTime(recipe.cook_time)}</p>
            </div>
        </div>
        
        <div class="mb-4">
            <h6 class="text-primary">Serving Information</h6>
            <p class="mb-0">${recipe.serves}</p>
        </div>
        
        <div class="mb-4">
            <h6 class="text-primary">Ingredients</h6>
            <ul class="list-unstyled">
                ${ingredients.map(ing => `<li class="mb-1">• ${ing}</li>`).join('') || '<li>No ingredients listed</li>'}
            </ul>
        </div>
        
        <div class="mb-4">
            <h6 class="text-primary">Instructions</h6>
            <ol>
                ${instructions.map(inst => `<li class="mb-2">${inst}</li>`).join('') || '<li>No instructions available</li>'}
            </ol>
        </div>
        
        <div>
            <h6 class="text-primary">Nutrition Information</h6>
            <table class="table table-sm nutrition-table">
                <tbody>
                    <tr><td><strong>Calories</strong></td><td>${nutrients.calories || recipe.calories_int || 'N/A'}</td></tr>
                    <tr><td>Carbohydrates</td><td>${nutrients.carbohydrateContent || 'N/A'}</td></tr>
                    <tr><td>Cholesterol</td><td>${nutrients.cholesterolContent || 'N/A'}</td></tr>
                    <tr><td>Fiber</td><td>${nutrients.fiberContent || 'N/A'}</td></tr>
                    <tr><td>Protein</td><td>${nutrients.proteinContent || 'N/A'}</td></tr>
                    <tr><td>Saturated Fat</td><td>${nutrients.saturatedFatContent || 'N/A'}</td></tr>
                    <tr><td>Sodium</td><td>${nutrients.sodiumContent || 'N/A'}</td></tr>
                    <tr><td>Sugar</td><td>${nutrients.sugarContent || 'N/A'}</td></tr>
                    <tr><td>Fat</td><td>${nutrients.fatContent || 'N/A'}</td></tr>
                </tbody>
            </table>
        </div>
        
        ${recipe.url ? `<div class="mt-4"><a href="${recipe.url}" target="_blank" class="btn btn-outline-primary btn-sm">View Original Recipe</a></div>` : ''}
    `;
    
    const offcanvas = new bootstrap.Offcanvas(document.getElementById('drawer'));
    offcanvas.show();
}

function toggleTimeDetails(button) {
    const timeDetails = button.nextElementSibling;
    const icon = button.querySelector('i');
    
    if (timeDetails.style.display === 'none') {
        timeDetails.style.display = 'block';
        icon.className = 'fas fa-chevron-up me-1';
        button.innerHTML = '<i class="fas fa-chevron-up me-1"></i>Hide Details';
    } else {
        timeDetails.style.display = 'none';
        icon.className = 'fas fa-chevron-down me-1';
        button.innerHTML = '<i class="fas fa-chevron-down me-1"></i>Show Details';
    }
}

async function search() {
    const title = document.getElementById('f_title').value;
    const cuisine = document.getElementById('f_cuisine').value;
    const rating = document.getElementById('f_rating').value;
    const calories = document.getElementById('f_cal').value;
    const limit = document.getElementById('perPage').value;
    
    const params = new URLSearchParams();
    if (title) params.append('title', title);
    if (cuisine) params.append('cuisine', cuisine);
    if (rating) params.append('rating', rating);
    if (calories) params.append('calories', calories);
    params.append('limit', limit);
    params.append('page', '1');
    
    try {
        const res = await fetch(`/api/recipes/search?${params.toString()}`);
        const data = await res.json();
        const recipes = data.data;
        
        displaySearchResults(recipes);
    } catch (error) {
        console.error('Error searching recipes:', error);
    }
}

function displaySearchResults(recipes) {
    const tbody = document.getElementById('tbody');
    const noResults = document.getElementById('noResults');
    
    tbody.innerHTML = '';
    
    if (!recipes.length) {
        noResults.style.display = 'block';
        document.getElementById('pageInfo').textContent = 'No results found';
        return;
    }
    
    noResults.style.display = 'none';
    
    recipes.forEach(recipe => {
        const tr = document.createElement('tr');
        tr.style.cursor = 'pointer';
        tr.innerHTML = `
            <td class="recipe-title" title="${recipe.title}">${recipe.title}</td>
            <td>${recipe.cuisine}</td>
            <td>${renderStars(recipe.rating)}</td>
            <td>${formatTime(recipe.total_time)}</td>
            <td>${recipe.serves}</td>
        `;
        tr.onclick = () => openDrawer(recipe);
        tbody.appendChild(tr);
    });
    
    document.getElementById('pageInfo').textContent = `Found ${recipes.length} recipes`;
}

document.addEventListener('DOMContentLoaded', function() {
    load(1);
    
    document.getElementById('f_title').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') search();
    });
    
    document.getElementById('f_cuisine').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') search();
    });
    
    document.getElementById('f_rating').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') search();
    });
    
    document.getElementById('f_cal').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') search();
    });
});