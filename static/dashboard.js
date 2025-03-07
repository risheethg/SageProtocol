// Fetch user data from the server
async function fetchUserData() {
    try {
        const response = await fetch('/api/user-data');
        const data = await response.json();
        updateDashboard(data);
    } catch (error) {
        console.error('Error fetching user data:', error);
    }
}

// Update dashboard with user data
function updateDashboard(data) {
    // Update user name
    document.getElementById('user-name').textContent = data.name;

    // Update trimester information
    const trimesterProgress = document.getElementById('trimester-progress');
    const trimesterText = document.getElementById('trimester-text');
    const trimesterPercentage = (data.trimester / 3) * 100;
    trimesterProgress.style.width = `${trimesterPercentage}%`;
    trimesterText.textContent = `${data.trimester}${getOrdinalSuffix(data.trimester)} Trimester`;

    // Update countdown
    updateCountdown(data.dueDate);

    // Update stats
    updateStats(data);
}

// Update countdown timer
function updateCountdown(dueDate) {
    const due = new Date(dueDate);
    
    function updateTimer() {
        const now = new Date();
        const diff = due - now;

        const days = Math.floor(diff / (1000 * 60 * 60 * 24));
        const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));

        document.getElementById('days').textContent = String(days).padStart(2, '0');
        document.getElementById('hours').textContent = String(hours).padStart(2, '0');
        document.getElementById('minutes').textContent = String(minutes).padStart(2, '0');
    }

    updateTimer();
    setInterval(updateTimer, 60000); // Update every minute
}

// Update stats with user data
function updateStats(data) {
    // Update calories
    const caloriesProgress = document.getElementById('calories-progress');
    const caloriesPercentage = (data.caloriesConsumed / data.caloriesTarget) * 100;
    caloriesProgress.style.width = `${caloriesPercentage}%`;
    document.getElementById('calories-consumed').textContent = data.caloriesConsumed;

    // Update water intake
    const waterProgress = document.getElementById('water-progress');
    const waterPercentage = (data.waterConsumed / data.waterTarget) * 100;
    waterProgress.style.width = `${waterPercentage}%`;
    document.getElementById('water-consumed').textContent = data.waterConsumed;

    // Update weight
    document.getElementById('current-weight').textContent = data.currentWeight;
    const weightChange = data.currentWeight - data.prePregnancyWeight;
    const weightChangeElement = document.getElementById('weight-change');
    weightChangeElement.textContent = `${weightChange > 0 ? '+' : ''}${weightChange.toFixed(1)} kg`;
    weightChangeElement.style.color = weightChange > 0 ? '#4CAF50' : '#ff4444';

    // Update meals logged
    document.getElementById('meals-logged').textContent = data.mealsLogged;

    // Update nutrients
    updateNutrients(data.nutrients);
}

// Update nutrient progress bars
function updateNutrients(nutrients) {
    // Protein
    const proteinProgress = document.getElementById('protein-progress');
    const proteinPercentage = (nutrients.protein / 75) * 100;
    proteinProgress.style.width = `${proteinPercentage}%`;
    document.getElementById('protein-consumed').textContent = nutrients.protein;

    // Carbs
    const carbsProgress = document.getElementById('carbs-progress');
    const carbsPercentage = (nutrients.carbs / 275) * 100;
    carbsProgress.style.width = `${carbsPercentage}%`;
    document.getElementById('carbs-consumed').textContent = nutrients.carbs;

    // Fat
    const fatProgress = document.getElementById('fat-progress');
    const fatPercentage = (nutrients.fat / 73) * 100;
    fatProgress.style.width = `${fatPercentage}%`;
    document.getElementById('fat-consumed').textContent = nutrients.fat;

    // Folic Acid
    const folicProgress = document.getElementById('folic-progress');
    const folicPercentage = (nutrients.folic / 600) * 100;
    folicProgress.style.width = `${folicPercentage}%`;
    document.getElementById('folic-consumed').textContent = nutrients.folic;
}

// Helper function to get ordinal suffix
function getOrdinalSuffix(n) {
    const j = n % 10;
    const k = n % 100;
    if (j == 1 && k != 11) return 'st';
    if (j == 2 && k != 12) return 'nd';
    if (j == 3 && k != 13) return 'rd';
    return 'th';
}

// Handle Log Food button click
document.querySelector('.btn-log-food').addEventListener('click', () => {
    // TODO: Implement food logging functionality
    alert('Food logging feature coming soon!');
});

// Initialize dashboard
document.addEventListener('DOMContentLoaded', fetchUserData); 