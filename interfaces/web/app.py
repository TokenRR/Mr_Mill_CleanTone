import os
import json
from flask import Flask, render_template, request, flash, redirect, url_for, session
from werkzeug.utils import secure_filename
from io import BytesIO
import website_config

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Allowed extensions for video upload
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mkv'}

# Global variables
uploaded_file = None
USERS_FILE = 'users.json'  # Path to the JSON file for user data

# Function to check allowed extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Load users from the JSON file
def load_users():
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'w') as file:
            json.dump({"users": []}, file)
    with open(USERS_FILE, 'r') as file:
        return json.load(file)

# Save users to the JSON file
def save_users(users):
    with open(USERS_FILE, 'w') as file:
        json.dump(users, file)

# Home page route
@app.route('/', methods=['GET', 'POST'])
def index():
    global uploaded_file

    # Set default language if not set
    if 'language' not in session:
        session['language'] = 'en'  # Default language

    # Handle POST requests
    if request.method == 'POST':

        # Handle language switching
        if 'switch_language' in request.form:
            session['language'] = 'uk' if session['language'] == 'en' else 'en'

        # Handle file uploads (drag-and-drop or browse)
        if 'file' in request.files:
            file = request.files['file']
            if file and allowed_file(file.filename):
                uploaded_file = file.read()
                flash(website_config.TRANSLATIONS[session['language']]['file_uploaded'], 'success')
            else:
                flash(website_config.TRANSLATIONS[session['language']]['invalid_file'], 'danger')

        # Handle processing (Enhance buttons)
        if 'enhance' in request.form:
            if uploaded_file:
                return send_file(BytesIO(uploaded_file), as_attachment=True, download_name="processed_video.mp4")
            else:
                flash(website_config.TRANSLATIONS[session['language']]['no_file_selected'], 'danger')

    return render_template(
        'index.html',
        language=session['language'],
        translations=website_config.TRANSLATIONS[session['language']]
    )

# Registration route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Load existing users
        users = load_users()

        # Check if user already exists
        if any(user['username'] == username for user in users['users']):
            flash(website_config.TRANSLATIONS[session['language']]['user_exists'], 'danger')
        else:
            # Add new user
            users['users'].append({'username': username, 'password': password})
            save_users(users)
            flash(website_config.TRANSLATIONS[session['language']]['registration_successful'], 'success')
            return redirect(url_for('index'))  # Redirect to main page after registration

    return render_template('register.html', translations=website_config.TRANSLATIONS[session['language']])


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Load existing users
        users = load_users()

        # Check if credentials are correct
        if any(user['username'] == username and user['password'] == password for user in users['users']):
            # Store user details in session
            session['username'] = username
            session['password'] = password
            flash(website_config.TRANSLATIONS[session['language']]['login_successful'], 'success')
            return redirect(url_for('index'))  # Redirect to main page after successful login
        else:
            flash(website_config.TRANSLATIONS[session['language']]['invalid_credentials'], 'danger')

    return render_template('login.html', translations=website_config.TRANSLATIONS[session['language']])


@app.route('/logout', methods=['GET'])
def logout():
    # Clear the session to log out the user
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for('index'))


@app.route('/my_account', methods=['GET'])
def my_account():
    # Check if the user is logged in
    if 'username' not in session:
        flash("You need to log in to access this page.", "danger")
        return redirect(url_for('login'))

    # Get user details from the session
    username = session['username']
    password = session['password']
    selected_plan = "NULL"  # Default plan

    return render_template(
        'my_account.html',
        username=username,
        password=password,
        selected_plan=selected_plan,
        translations=website_config.TRANSLATIONS[session['language']]
    )


if __name__ == '__main__':
    app.run(debug=True)
