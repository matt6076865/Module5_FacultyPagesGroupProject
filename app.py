from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# Database configuration from environment variables
db_config = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', ''),
    'database': os.getenv('MYSQL_DATABASE', 'faculty_portal')
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

# Initialize database tables
def init_db():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS faculty (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                title VARCHAR(255),
                campus_location VARCHAR(255),
                department VARCHAR(255),
                office_location VARCHAR(255),
                email VARCHAR(255),
                phone VARCHAR(20),
                office_schedule VARCHAR(255),
                about_me TEXT,
                education TEXT,
                research TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Database initialization error: {e}")

# Serve root-level images directory (legacy path support)
@app.route('/images/<path:filename>')
def serve_image(filename):
    return send_from_directory('images', filename)

# API Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/edit')
def edit():
    return render_template('edit.html')

@app.route('/api/faculty', methods=['GET'])
def get_faculty():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM faculty ORDER BY id DESC LIMIT 1')
        faculty = cursor.fetchone()
        cursor.close()
        conn.close()

        if faculty:
            return jsonify(faculty)
        else:
            # Return default faculty data if none exists
            return jsonify({
                'id': 1,
                'name': 'Matt Watkins',
                'title': 'Professor',
                'campus_location': 'Clearwater Campus',
                'department': 'Computer and Information Technology',
                'office_location': 'Building A, Room 210',
                'email': 'faculty@school.edu',
                'phone': '(555) 123-4567',
                'office_schedule': 'Mon/Wed 2:00 PM to 4:00 PM',
                'about_me': 'Assists with all technical support for CAS faculty and staff.',
                'education': 'He began as an adjunct instructor with St. Petersburg College in 1999...',
                'research': 'He has earned many industry certifications...'
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/faculty', methods=['POST'])
def update_faculty():
    try:
        data = request.json
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO faculty (name, title, campus_location, department, office_location, email, phone, office_schedule, about_me, education, research)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            name = VALUES(name),
            title = VALUES(title),
            campus_location = VALUES(campus_location),
            department = VALUES(department),
            office_location = VALUES(office_location),
            email = VALUES(email),
            phone = VALUES(phone),
            office_schedule = VALUES(office_schedule),
            about_me = VALUES(about_me),
            education = VALUES(education),
            research = VALUES(research)
        ''', (
            data.get('name'),
            data.get('title'),
            data.get('campus_location'),
            data.get('department'),
            data.get('office_location'),
            data.get('email'),
            data.get('phone'),
            data.get('office_schedule'),
            data.get('about_me'),
            data.get('education'),
            data.get('research')
        ))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({'success': True, 'message': 'Faculty information updated'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)), debug=False)
