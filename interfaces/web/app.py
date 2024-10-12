import os
from flask import Flask, render_template, request, flash, send_file, session
from werkzeug.utils import secure_filename
from io import BytesIO
import website_config  # Import translations and settings

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Allowed extensions for video upload
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mkv'}

# Dictionary to store uploaded files temporarily
uploaded_file = None

# Function to check allowed extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
                # Store the file temporarily in memory (or disk if needed)
                uploaded_file = file.read()
                flash(website_config.TRANSLATIONS[session['language']]['file_uploaded'], 'success')
            else:
                flash(website_config.TRANSLATIONS[session['language']]['invalid_file'], 'danger')

        # Handle processing (Enhance buttons)
        if 'enhance' in request.form:
            if uploaded_file:
                # Use the stored file for processing
                return send_file(BytesIO(uploaded_file), as_attachment=True, download_name="processed_video.mp4")
            else:
                flash(website_config.TRANSLATIONS[session['language']]['no_file_selected'], 'danger')

    return render_template(
        'index.html',
        language=session['language'],
        translations=website_config.TRANSLATIONS[session['language']]
    )

if __name__ == '__main__':
    app.run(debug=True)
