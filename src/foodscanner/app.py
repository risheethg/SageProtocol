from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import User
from config import Config
import sqlite3
from datetime import datetime, timedelta
import traceback
import os
import requests

from werkzeug.utils import secure_filename
from calorie import process_image

# Define allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app = Flask(__name__)
app.config.from_object(Config)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth'

# Add upload folder configuration
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

def allowed_file(filename):
    """Check if the file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_meal_image(file):
    """
    Save the uploaded meal image with proper validation
    Returns: (success, message, filename)
    """
    if not file:
        return False, "No file uploaded", None
        
    if not allowed_file(file.filename):
        return False, "Invalid file type. Only PNG, JPG, and JPEG files are allowed.", None
        
    try:
        # Generate unique filename using timestamp and user ID
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        original_filename = secure_filename(file.filename)
        filename = f"meal_{current_user.id}_{timestamp}_{original_filename}"
        
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(file_path)
        
        return True, "File uploaded successfully", filename
    except Exception as e:
        return False, f"Error saving file: {str(e)}", None

def init_db():
    conn = sqlite3.connect('nutrilogic.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            name TEXT,
            height REAL,
            weight REAL,
            pre_pregnancy_weight REAL,
            age INTEGER,
            trimester INTEGER,
            multiple_pregnancies BOOLEAN,
            medical_conditions TEXT,
            diet_type TEXT,
            allergies TEXT
        )
    ''')
    
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
    """
    Load a user from the database by their user ID.

    Args:
        user_id (int): The ID of the user to be loaded.

    Returns:
        User: An instance of the User class if found, otherwise None.
    """

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

@app.route("/process_image", methods=["POST"])
def process_image_request():
    try:
        print("Received request at /process_image")  # Debugging

        data = request.get_json()
        print("Received JSON:", data)  # Debugging

        if not data or "filename" not in data:
            return jsonify({"error": "No filename provided"}), 400

        image_filename = data["filename"]
        print("Processing image:", image_filename)  # Debugging

        image_path = os.path.join(app.config["UPLOAD_FOLDER"], image_filename)

        if not os.path.exists(image_path):
            print(f"File not found: {image_path}")
            return jsonify({"error": "File not found"}), 404

        with open(image_path, "rb") as image_file:
            image_bytes = image_file.read()

        print("Image successfully read.")  # Debugging

        response_data = process_image(image_bytes)

        print("Final JSON output:", response_data)  # Debugging

        return jsonify(response_data)

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/upload", methods=["POST"])

def upload():
    """Handle meal image upload and nutrition analysis"""
    try:
        print("Received upload request.")  # Debugging

        # Get text description (optional)
        text_data = request.form.get("mealText", "")

        # Check if file is present in request
        file = request.files.get("mealImage")
        if not file or file.filename == '':
            print("No image file received.")  # Debugging
            return jsonify({"error": "No image file provided"}), 400

        # Secure and save the image
        uploaded_filename = secure_filename(file.filename)
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], uploaded_filename)
        file.save(file_path)

        print(f"File saved at: {file_path}")  # Debugging

        # 🟢 Call /process_image to analyze nutrition
        print("About to call /process_image with filename:", uploaded_filename)

        try:
            response = requests.post(
                "http://127.0.0.1:5000/process_image", 
                json={"filename": uploaded_filename}
            )

            print("Response from /process_image:", response.status_code, response.text[:500])  # Debugging

            # Ensure JSON response
            if "application/json" not in response.headers.get("Content-Type", ""):
                print("Error: Expected JSON, received non-JSON response.")
                return jsonify({"error": "Invalid response from server"}), 500

            nutrition_data = response.json()
            print("Received nutrition data:", nutrition_data)  # Debugging

        except requests.RequestException as e:
            print("Error calling /process_image:", e)  # Debugging
            return jsonify({"error": "Failed to process image"}), 500

        # 🟢 Save meal data to the database
        conn = sqlite3.connect('nutrilogic.db')
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO meals (
                user_id, image_path, description, calories, protein, 
                folic_acid, iron, vitamin_d, calcium
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            current_user.id,
            uploaded_filename,
            text_data,
            nutrition_data.get('calories', 0),
            nutrition_data.get('protein', 0),
            nutrition_data.get('folic_acid', 0),
            nutrition_data.get('iron', 0),
            nutrition_data.get('vitamin_d', 0),
            nutrition_data.get('calcium', 0)
        ))

        conn.commit()
        conn.close()

        print("Meal logged successfully in database.")  # Debugging

        return jsonify({
            "success": True,
            "message": "Meal logged successfully",
            "nutrition_data": nutrition_data
        })

    except Exception as e:
        print(f"Error in upload: {str(e)}")
        return jsonify({"error": "An unexpected error occurred"}), 500


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
    
    # Get today's nutritional totals
    today = datetime.now().date()
    cursor.execute('''
        SELECT 
            COALESCE(SUM(calories), 0) as total_calories,
            COALESCE(SUM(protein), 0) as total_protein,
            COALESCE(SUM(folic_acid), 0) as total_folic_acid,
            COALESCE(SUM(iron), 0) as total_iron,
            COALESCE(SUM(vitamin_d), 0) as total_vitamin_d,
            COALESCE(SUM(calcium), 0) as total_calcium
        FROM meals 
        WHERE user_id = ? AND date(created_at) = date(?)
    ''', (current_user.id, today))
    
    totals = cursor.fetchone()
    conn.close()
    
    data = {
        'name': current_user.name,
        'trimester': current_user.trimester,
        'dueDate': due_date.isoformat(),
        'caloriesConsumed': totals[0],
        'caloriesTarget': 2200,
        'waterConsumed': 1.5,
        'waterTarget': 2.5,
        'currentWeight': current_user.weight,
        'prePregnancyWeight': current_user.pre_pregnancy_weight,
        'mealsLogged': meals_logged,
        'nutrients': {
            'protein': totals[1],
            'folic_acid': totals[2],
            'iron': totals[3],
            'vitamin_d': totals[4],
            'calcium': totals[5]
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
