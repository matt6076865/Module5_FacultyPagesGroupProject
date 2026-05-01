from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import mysql.connector
import os
import time
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# Database configuration from environment variables (no defaults — must be injected)
db_config = {
    'host': os.getenv('MYSQL_HOST'),
    'user': os.getenv('MYSQL_USER'),
    'password': os.getenv('MYSQL_PASSWORD'),
    'database': os.getenv('MYSQL_DATABASE'),
    'connection_timeout': 10,
    'connect_timeout': 10,
}

def get_db_connection():
    print(f"Connecting to MySQL at {db_config['host']} as {db_config['user']}...")
    conn = mysql.connector.connect(**db_config)
    print("MySQL connection established.")
    return conn

# Initialize database tables with retry logic
def init_db(retries=5, delay=2):
    for attempt in range(1, retries + 1):
        try:
            print(f"Database init attempt {attempt}/{retries}...")
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
            print("Database initialized successfully.")
            return
        except Exception as e:
            print(f"Database initialization error (attempt {attempt}/{retries}): {e}")
            if attempt < retries:
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                print("All database initialization attempts failed. The app will start, but DB operations may fail.")


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
        print("GET /api/faculty - fetching faculty record...")
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM faculty ORDER BY id DESC LIMIT 1')
        faculty = cursor.fetchone()
        cursor.close()
        conn.close()

        if faculty:
            print(f"GET /api/faculty - returning record id={faculty.get('id')}")
            return jsonify(faculty)
        else:
            print("GET /api/faculty - no records found, returning defaults")
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
        print(f"GET /api/faculty - error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/faculty', methods=['POST'])
def update_faculty():
    try:
        data = request.json
        if not data:
            print("POST /api/faculty - error: no JSON body received")
            return jsonify({'error': 'Request body must be JSON'}), 400

        print(f"POST /api/faculty - saving data for: {data.get('name', '(unnamed)')}")
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

        print("POST /api/faculty - faculty record saved successfully")
        return jsonify({'success': True, 'message': 'Faculty information updated'})
    except Exception as e:
        print(f"POST /api/faculty - error: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print(f"Starting Faculty Portal on port {port}...")

    # Validate that all required MySQL environment variables are present
    required_vars = ['MYSQL_HOST', 'MYSQL_USER', 'MYSQL_PASSWORD', 'MYSQL_DATABASE']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        print(f"ERROR: Missing required environment variables: {', '.join(missing_vars)}")
        print("The app cannot connect to MySQL without these variables. Exiting.")
        raise SystemExit(1)

    print(f"MySQL host: {db_config['host']}, user: {db_config['user']}, "
          f"password: {'*' * len(db_config['password'])}, database: {db_config['database']}")

    init_db()
    app.run(host='0.0.0.0', port=port, debug=False)
