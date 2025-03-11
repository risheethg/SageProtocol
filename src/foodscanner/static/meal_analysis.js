// Function to initialize the page with meal analysis data
async function initializeMealAnalysis() {
    console.log('Initializing meal analysis page...');
    try {
        // Check for initial data
        const initialDataElement = document.getElementById('initialData');
        if (initialDataElement) {
            console.log('Found initial data element');
            try {
                const initialData = JSON.parse(initialDataElement.dataset.mealAnalysis);
                if (initialData) {
                    console.log('Successfully parsed initial data:', initialData);
                    displayData(initialData);
                    return;
                }
            } catch (parseError) {
                console.error('Error parsing initial data:', parseError);
            }
        } else {
            console.log('No initial data found, will fetch from API');
        }

        // Show loading state
        console.log('Showing loading state...');
        document.getElementById('loadingState').style.display = 'flex';
        document.getElementById('contentSections').style.display = 'none';
        document.getElementById('errorState').style.display = 'none';

        // Fetch data from API
        console.log('Fetching data from API...');
        const response = await fetch('/api/meal-analysis');
        const data = await response.json();
        console.log('API response:', data);
        
        if (data.success) {
            console.log('Successfully received data from API');
            displayData(data);
        } else {
            console.warn('API returned error:', data.message);
            showError(data.message || 'Failed to load meal analysis data');
        }
    } catch (error) {
        console.error('Error in meal analysis:', error);
        showError('An error occurred while loading the analysis');
    }
}

// Display all data
function displayData(data) {
    console.log('Displaying data:', data);
    try {
        // Hide loading, show content
        document.getElementById('loadingState').style.display = 'none';
        document.getElementById('contentSections').style.display = 'block';
        document.getElementById('errorState').style.display = 'none';

        // Display each section
        console.log('Displaying food items:', data.foods);
        displayFoodItems(data.foods);
        
        console.log('Updating nutritional summary:', data.nutrition_summary);
        updateNutritionalSummary(data.nutrition_summary);
        
        console.log('Displaying detailed nutrients:', data.detailed_nutrients);
        displayDetailedNutrients(data.detailed_nutrients);
        
        console.log('Displaying recommendations:', data.recommendations);
        displayRecommendations(data.recommendations);
        
        console.log('All data displayed successfully');
    } catch (error) {
        console.error('Error displaying data:', error);
        showError('Error displaying meal analysis data');
    }
}

// Display detected food items
function displayFoodItems(foods = []) {
    console.log('Displaying food items, count:', foods.length);
    const foodItemsList = document.getElementById('foodItemsList');
    foodItemsList.innerHTML = '';

    if (foods.length === 0) {
        console.log('No food items to display');
        foodItemsList.innerHTML = '<p class="no-data">No food items detected</p>';
        return;
    }

    foods.forEach(food => {
        console.log('Creating food item element for:', food.name);
        const foodItem = document.createElement('div');
        foodItem.className = 'food-item';
        foodItem.innerHTML = `
            <img src="${food.image || '/static/images/placeholder-food.png'}" alt="${food.name}">
            <h3>${food.name}</h3>
            <p>${food.portion_size || 'Standard Portion'}</p>
            <p>${food.calories} kcal</p>
        `;
        foodItemsList.appendChild(foodItem);
    });
}

// Update nutritional summary
function updateNutritionalSummary(summary = {}) {
    console.log('Updating nutritional summary with:', summary);
    document.getElementById('totalCalories').textContent = `${summary.calories || 0} kcal`;
    document.getElementById('totalProtein').textContent = `${summary.protein || 0}g`;
    document.getElementById('totalCarbs').textContent = `${summary.carbohydrates || 0}g`;
    document.getElementById('totalFat').textContent = `${summary.fat || 0}g`;
}

// Display detailed nutrients with progress bars
function displayDetailedNutrients(nutrients = {}) {
    console.log('Displaying detailed nutrients, count:', Object.keys(nutrients).length);
    const nutrientsGrid = document.getElementById('detailedNutrients');
    nutrientsGrid.innerHTML = '';

    if (Object.keys(nutrients).length === 0) {
        console.log('No detailed nutrients to display');
        nutrientsGrid.innerHTML = '<p class="no-data">No detailed nutrient information available</p>';
        return;
    }

    Object.entries(nutrients).forEach(([nutrient, data]) => {
        console.log(`Creating nutrient element for ${nutrient}:`, data);
        const percentage = (data.amount / data.daily_value) * 100;
        const nutrientItem = document.createElement('div');
        nutrientItem.className = 'nutrient-item';
        nutrientItem.innerHTML = `
            <h4>${nutrient}</h4>
            <div class="progress-bar">
                <div class="progress-fill" style="width: ${Math.min(percentage, 100)}%"></div>
            </div>
            <p>${data.amount}${data.unit} (${percentage.toFixed(1)}% DV)</p>
        `;
        nutrientsGrid.appendChild(nutrientItem);
    });
}

// Display recommendations
function displayRecommendations(recommendations = []) {
    console.log('Displaying recommendations, count:', recommendations.length);
    const recommendationsList = document.getElementById('recommendationsList');
    recommendationsList.innerHTML = '';

    if (recommendations.length === 0) {
        console.log('No recommendations to display');
        recommendationsList.innerHTML = '<p class="no-data">No recommendations available</p>';
        return;
    }

    recommendations.forEach(rec => {
        console.log('Creating recommendation element:', rec.title);
        const recItem = document.createElement('div');
        recItem.className = 'recommendation-item';
        recItem.innerHTML = `
            <i class="fas fa-lightbulb"></i>
            <div>
                <h4>${rec.title}</h4>
                <p>${rec.description}</p>
            </div>
        `;
        recommendationsList.appendChild(recItem);
    });
}

// Show error message
function showError(message) {
    console.error('Showing error message:', message);
    document.getElementById('loadingState').style.display = 'none';
    document.getElementById('contentSections').style.display = 'none';
    
    const errorState = document.getElementById('errorState');
    errorState.style.display = 'flex';
    errorState.querySelector('p').textContent = message;
}

// Initialize the page when DOM is loaded
console.log('Setting up meal analysis page...');
document.addEventListener('DOMContentLoaded', initializeMealAnalysis); 