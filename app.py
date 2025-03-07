from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import User
from config import Config
import sqlite3
from datetime import datetime, timedelta
import traceback
import os

app = Flask(__name__)
app.config.from_object(Config)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth'

def init_db():
    conn = sqlite3.connect('nutrilogic.db')
    cursor = conn.cursor()
    
    # Create meals table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS meals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            image_path TEXT NOT NULL,
            description TEXT,
            calories INTEGER DEFAULT 0,
            protein REAL DEFAULT 0,
            folic_acid REAL DEFAULT 0,
            iron REAL DEFAULT 0,
            vitamin_d REAL DEFAULT 0,
            calcium REAL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()

@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect('nutrilogic.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, username, email, name, height, weight, pre_pregnancy_weight, 
               age, trimester, multiple_pregnancies, medical_conditions, diet_type, allergies
        FROM users WHERE id = ?
    ''', (user_id,))
    user_data = cursor.fetchone()
    conn.close()
    
    if user_data:
        return User(*user_data)
    return None

@app.route('/')
def index():
    return render_template('Sample.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/log-meal')
@login_required
def log_meal():
    return render_template('log_meal.html')

@app.route('/api/upload-meal', methods=['POST'])
@login_required
def upload_meal():
    try:
        if 'mealImage' not in request.files:
            return jsonify({'success': False, 'message': 'No image file provided'}), 400

        file = request.files['mealImage']
        if file.filename == '':
            return jsonify({'success': False, 'message': 'No selected file'}), 400

        if not file or not file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
            return jsonify({'success': False, 'message': 'Invalid file type. Please upload an image.'}), 400

        # Create uploads directory if it doesn't exist
        upload_dir = os.path.join(app.root_path, 'static', 'uploads')
        os.makedirs(upload_dir, exist_ok=True)

        # Save the file
        filename = f"{current_user.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
        file_path = os.path.join(upload_dir, filename)
        file.save(file_path)

        # Get meal description
        description = request.form.get('mealText', '')

        # Save meal data to database with initial nutritional values set to 0
        conn = sqlite3.connect('nutrilogic.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO meals (
                user_id, image_path, description, calories, protein, 
                folic_acid, iron, vitamin_d, calcium
            )
            VALUES (?, ?, ?, 0, 0, 0, 0, 0, 0)
        ''', (current_user.id, filename, description))
        
        meal_id = cursor.lastrowid
        conn.commit()
        conn.close()

        # TODO: Process the image with AI model to get nutritional information
        # For now, we'll use mock data
        nutritional_info = {
            'calories': 0,
            'protein': 0,
            'folic_acid': 0,
            'iron': 0,
            'vitamin_d': 0,
            'calcium': 0
        }

        return jsonify({
            'success': True,
            'message': 'Meal logged successfully',
            'filename': filename,
            'nutritional_info': nutritional_info
        })

    except Exception as e:
        print(f"Upload error: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/meals')
@login_required
def get_meals():
    try:
        conn = sqlite3.connect('nutrilogic.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, image_path, description, calories, protein, 
                   folic_acid, iron, vitamin_d, calcium, created_at
            FROM meals
            WHERE user_id = ?
            ORDER BY created_at DESC
        ''', (current_user.id,))
        
        meals = cursor.fetchall()
        conn.close()
        
        return jsonify({
            'success': True,
            'meals': [{
                'id': meal[0],
                'image_path': meal[1],
                'description': meal[2],
                'calories': meal[3],
                'protein': meal[4],
                'folic_acid': meal[5],
                'iron': meal[6],
                'vitamin_d': meal[7],
                'calcium': meal[8],
                'created_at': meal[9]
            } for meal in meals]
        })
        
    except Exception as e:
        print(f"Error fetching meals: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/user-data')
@login_required
def get_user_data():
    # Calculate due date (40 weeks from conception)
    conception_date = datetime.now() - timedelta(weeks=current_user.trimester * 13)
    due_date = conception_date + timedelta(weeks=40)
    
    # Get total meals logged
    conn = sqlite3.connect('nutrilogic.db')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM meals WHERE user_id = ?', (current_user.id,))
    meals_logged = cursor.fetchone()[0]
    conn.close()
    
    # Mock data for demonstration
    data = {
        'name': current_user.name,
        'trimester': current_user.trimester,
        'dueDate': due_date.isoformat(),
        'caloriesConsumed': 1500,
        'caloriesTarget': 2200,
        'waterConsumed': 1.5,
        'waterTarget': 2.5,
        'currentWeight': current_user.weight,
        'prePregnancyWeight': current_user.pre_pregnancy_weight,
        'mealsLogged': meals_logged,
        'nutrients': {
            'protein': 45,
            'carbs': 180,
            'fat': 55,
            'folic': 400
        }
    }
    
    return jsonify(data)

@app.route('/auth')
def auth():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('auth.html')

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'No data provided'}), 400
            
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({'success': False, 'message': 'Username and password are required'}), 400

        user = User.get_by_username(username)
        if user and user.check_password(password):
            login_user(user)
            return jsonify({'success': True, 'message': 'Login successful'})
        
        return jsonify({'success': False, 'message': 'Invalid username or password'}), 401
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/signup', methods=['POST'])
def signup():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'No data provided'}), 400

        # Validate required fields
        required_fields = ['email', 'password', 'name', 'height', 'weight', 'pre_pregnancy_weight', 
                         'age', 'trimester', 'multiple_pregnancies', 'diet_type']
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            return jsonify({'success': False, 'message': f'Missing required fields: {", ".join(missing_fields)}'}), 400

        # Check if username or email already exists
        username = data.get('email').split('@')[0]
        if User.get_by_username(username):
            return jsonify({'success': False, 'message': 'Username already exists'}), 400
        
        if User.get_by_email(data.get('email')):
            return jsonify({'success': False, 'message': 'Email already exists'}), 400

        # Create user
        user = User.create_user(data)
        if user:
            login_user(user)
            return jsonify({'success': True, 'message': 'Signup successful'})
        else:
            return jsonify({'success': False, 'message': 'Failed to create user'}), 500

    except Exception as e:
        print(f"Signup error: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

@app.route('/api/update-profile', methods=['POST'])
@login_required
def update_profile():
    try:
        data = request.get_json()
        
        # Update user information in the database
        conn = sqlite3.connect('nutrilogic.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE users 
            SET name = ?, age = ?, height = ?, trimester = ?, 
                multiple_pregnancies = ?, medical_conditions = ?,
                weight = ?, pre_pregnancy_weight = ?, diet_type = ?, allergies = ?
            WHERE id = ?
        ''', (
            data['name'], data['age'], data['height'], data['trimester'],
            data['multiple_pregnancies'], data['medical_conditions'],
            data['weight'], data['pre_pregnancy_weight'], data['diet_type'],
            data['allergies'], current_user.id
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'Profile updated successfully'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/recommendations')
@login_required
def recommendations():
    return render_template('recommendations.html')

@app.route('/api/profile-data')
@login_required
def get_profile_data():
    try:
        # Calculate due date (40 weeks from conception)
        conception_date = datetime.now() - timedelta(weeks=current_user.trimester * 13)
        due_date = conception_date + timedelta(weeks=40)
        
        data = {
            'name': current_user.name,
            'email': current_user.email,
            'age': current_user.age,
            'height': current_user.height,
            'trimester': current_user.trimester,
            'due_date': due_date.isoformat(),
            'multiple_pregnancies': current_user.multiple_pregnancies,
            'medical_conditions': current_user.medical_conditions.split(',') if current_user.medical_conditions else [],
            'weight': current_user.weight,
            'pre_pregnancy_weight': current_user.pre_pregnancy_weight,
            'diet_type': current_user.diet_type,
            'allergies': current_user.allergies
        }
        
        return jsonify(data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    init_db()  # Initialize database tables
    app.run(debug=True)
