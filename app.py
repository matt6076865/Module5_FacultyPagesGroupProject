from flask import Flask, render_template, request, jsonify, send_from_directory, session, redirect, url_for
from flask_cors import CORS
import mysql.connector
import os
import time
from dotenv import load_dotenv
from functools import wraps

load_dotenv()

app = Flask(__name__)
CORS(app)

# Secret key for session signing — must be set via FLASK_SECRET_KEY env var
app.secret_key = os.getenv('FLASK_SECRET_KEY', os.urandom(24))

# Database configuration — host falls back to Railway's private service domain
# so the app can reach MySQL even when MYSQL_HOST is not explicitly injected.
db_config = {
    'host': os.getenv('MYSQL_HOST', 'mysql.railway.internal'),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', ''),
    'database': os.getenv('MYSQL_DATABASE', 'railway'),
    'connection_timeout': 10,
    'connect_timeout': 10,
}

# Log the effective connection string at startup (password masked for safety)
_masked = '*' * len(db_config['password']) if db_config['password'] else '(empty)'
print(
    f"[db_config] host={db_config['host']}  user={db_config['user']}  "
    f"password={_masked}  database={db_config['database']}"
)

def get_db_connection():
    print(
        f"Connecting to MySQL at {db_config['host']} "
        f"(db={db_config['database']}) as {db_config['user']}..."
    )
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


# ---------------------------------------------------------------------------
# Authentication helpers
# ---------------------------------------------------------------------------

def is_authenticated():
    """Return True if the current session has a valid login."""
    return session.get('authenticated') is True


def login_required(f):
    """Decorator that returns 401 JSON for unauthenticated API requests."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not is_authenticated():
            return jsonify({'error': 'Unauthorized — please log in'}), 401
        return f(*args, **kwargs)
    return decorated


# ---------------------------------------------------------------------------
# Auth routes
# ---------------------------------------------------------------------------

@app.route('/login', methods=['GET'])
def login_page():
    if is_authenticated():
        return redirect(url_for('edit'))
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json(silent=True) or {}
    password = data.get('password', '')
    admin_password = os.getenv('ADMIN_PASSWORD', '')

    if not admin_password:
        return jsonify({'error': 'Server is not configured with an admin password'}), 500

    if password == admin_password:
        session['authenticated'] = True
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Invalid password'}), 401


@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True})


# ---------------------------------------------------------------------------
# Serve root-level images directory (legacy path support)
# ---------------------------------------------------------------------------

@app.route('/images/<path:filename>')
def serve_image(filename):
    return send_from_directory('images', filename)


# ---------------------------------------------------------------------------
# Page routes
# ---------------------------------------------------------------------------

@app.route('/')
def index():
    return render_template('index.html', authenticated=is_authenticated())


@app.route('/edit')
def edit():
    if not is_authenticated():
        return redirect(url_for('login_page'))
    return render_template('edit.html')

PII_FIELDS = ('office_location', 'email', 'phone', 'office_schedule')


def strip_pii(record):
    """Remove PII fields from a faculty record dict for unauthenticated responses."""
    return {k: v for k, v in record.items() if k not in PII_FIELDS}


@app.route('/api/faculty', methods=['GET'])
def get_faculty():
    try:
        faculty_id = request.args.get('id')
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        if faculty_id:
            print(f"GET /api/faculty - fetching record id={faculty_id}")
            cursor.execute('SELECT * FROM faculty WHERE id = %s', (faculty_id,))
        else:
            print("GET /api/faculty - fetching latest record...")
            cursor.execute('SELECT * FROM faculty ORDER BY id DESC LIMIT 1')

        faculty = cursor.fetchone()
        cursor.close()
        conn.close()

        if faculty:
            print(f"GET /api/faculty - returning record id={faculty.get('id')}")
            result = faculty if is_authenticated() else strip_pii(faculty)
            return jsonify(result)
        else:
            if faculty_id:
                return jsonify({'error': f'Faculty record {faculty_id} not found'}), 404
            print("GET /api/faculty - no records found, returning defaults")
            # Return default faculty data if none exists
            defaults = {
                'id': None,
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
            }
            return jsonify(defaults if is_authenticated() else strip_pii(defaults))
    except Exception as e:
        print(f"GET /api/faculty - error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/faculty/list', methods=['GET'])
def list_faculty():
    """Return a lightweight list of all faculty records (id + name) for selectors."""
    try:
        print("GET /api/faculty/list - fetching all faculty records...")
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT id, name FROM faculty ORDER BY id ASC')
        records = cursor.fetchall()
        cursor.close()
        conn.close()
        print(f"GET /api/faculty/list - returning {len(records)} records")
        return jsonify(records)
    except Exception as e:
        print(f"GET /api/faculty/list - error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/faculty', methods=['POST'])
@login_required
def create_faculty():
    """Insert a brand-new faculty record and return it with its generated ID."""
    try:
        data = request.json
        if not data:
            print("POST /api/faculty - error: no JSON body received")
            return jsonify({'error': 'Request body must be JSON'}), 400

        print(f"POST /api/faculty - creating record for: {data.get('name', '(unnamed)')}")
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            '''INSERT INTO faculty
               (name, title, campus_location, department, office_location,
                email, phone, office_schedule, about_me, education, research)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''',
            (
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
                data.get('research'),
            )
        )
        new_id = cursor.lastrowid
        conn.commit()

        # Fetch and return the newly created record
        cursor.execute('SELECT * FROM faculty WHERE id = %s', (new_id,))
        new_record = cursor.fetchone()
        cursor.close()
        conn.close()

        print(f"POST /api/faculty - created record id={new_id}")
        return jsonify(new_record), 201
    except Exception as e:
        print(f"POST /api/faculty - error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/faculty/<int:faculty_id>', methods=['PUT'])
@login_required
def update_faculty(faculty_id):
    """Update an existing faculty record by ID and return the updated record."""
    try:
        data = request.json
        if not data:
            print(f"PUT /api/faculty/{faculty_id} - error: no JSON body received")
            return jsonify({'error': 'Request body must be JSON'}), 400

        print(f"PUT /api/faculty/{faculty_id} - updating record for: {data.get('name', '(unnamed)')}")
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        params = (
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
            data.get('research'),
            faculty_id,
        )
        query = (
            'UPDATE faculty'
            ' SET name = %s, title = %s, campus_location = %s, department = %s,'
            '     office_location = %s, email = %s, phone = %s,'
            '     office_schedule = %s, about_me = %s, education = %s, research = %s'
            ' WHERE id = %s'
        )
        print(f"PUT /api/faculty/{faculty_id} - faculty_id={faculty_id!r} (type={type(faculty_id).__name__})")
        print(f"PUT /api/faculty/{faculty_id} - executing: {query}")
        print(f"PUT /api/faculty/{faculty_id} - params: {params}")
        cursor.execute(query, params)

        # IMPORTANT: read rowcount BEFORE commit — mysql.connector resets it to 0 after commit
        rowcount = cursor.rowcount
        print(f"PUT /api/faculty/{faculty_id} - cursor.rowcount={rowcount}")

        if rowcount == 0:
            conn.rollback()
            cursor.close()
            conn.close()
            print(f"PUT /api/faculty/{faculty_id} - no rows matched, returning 404")
            return jsonify({'error': f'Faculty record {faculty_id} not found'}), 404

        conn.commit()

        # Fetch and return the updated record
        cursor.execute('SELECT * FROM faculty WHERE id = %s', (faculty_id,))
        updated = cursor.fetchone()
        cursor.close()
        conn.close()

        print(f"PUT /api/faculty/{faculty_id} - record updated successfully")
        return jsonify(updated)
    except Exception as e:
        print(f"PUT /api/faculty/{faculty_id} - error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/faculty/<int:faculty_id>', methods=['DELETE'])
@login_required
def delete_faculty(faculty_id):
    """Delete a faculty record by ID."""
    try:
        print(f"DELETE /api/faculty/{faculty_id} - deleting record...")
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM faculty WHERE id = %s', (faculty_id,))

        # Read rowcount BEFORE commit — mysql.connector resets it to 0 after commit
        rowcount = cursor.rowcount
        if rowcount == 0:
            conn.rollback()
            cursor.close()
            conn.close()
            return jsonify({'error': f'Faculty record {faculty_id} not found'}), 404

        conn.commit()

        cursor.close()
        conn.close()
        print(f"DELETE /api/faculty/{faculty_id} - record deleted successfully")
        return jsonify({'success': True, 'message': f'Faculty record {faculty_id} deleted'})
    except Exception as e:
        print(f"DELETE /api/faculty/{faculty_id} - error: {e}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print(f"Starting Faculty Portal on port {port}...")
    print(f"MySQL host: {db_config['host']}, database: {db_config['database']}")
    init_db()
    app.run(host='0.0.0.0', port=port, debug=False)
