Module5_FacultyPagesGroupProject - SPC - COP 4504 - DEV TEAM 2 - 2026
This is a Dev Team 2 Group project that was based on a prior forked one.
This project adds a Python/Flask backend with MySQL database support for dynamic faculty data management.
Contributors: Matthew W., Dannielle M., Jacob G., and LeEric R.

## Project Status
✅ Full CRUD implemented — CREATE, READ, UPDATE, DELETE all working
✅ Password-based authentication added
✅ PII protection for unauthenticated users

## Project Structure
```
/
├── app.py                  - Flask application and API routes
├── requirements.txt        - Python dependencies
├── templates/
│   ├── index.html          - Faculty profile page (dynamic, API-driven)
│   ├── edit.html           - Faculty edit form (requires login)
│   └── login.html          - Admin login page
├── static/
│   ├── style.css           - Shared styles
│   ├── spc.css             - SPC brand styles
│   └── images/             - Profile pictures and image assets
├── images/                 - Legacy image assets (root-level)
└── Faculty Info Pages Wireframes.pdf - Design mockups
```

## Project Purpose
This application demonstrates:
- Full-stack Flask + MySQL architecture
- Dynamic faculty data loaded from a MySQL database
- Full REST API for creating, reading, updating, and deleting faculty records
- Password-based authentication with server-side session management
- PII protection — sensitive fields are hidden from unauthenticated users
- Interactive edit form that persists changes to the database
- Separation of frontend templates and backend API concerns

## How to Run Locally

### Prerequisites
- Python 3.8+
- MySQL database

### Setup
1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file with your database credentials and secrets:
   ```
   MYSQL_HOST=localhost
   MYSQL_USER=root
   MYSQL_PASSWORD=yourpassword
   MYSQL_DATABASE=faculty_portal
   ADMIN_PASSWORD=1234
   FLASK_SECRET_KEY=your-secret-key
   ```
4. Run the application:
   ```bash
   python app.py
   ```
5. Open `http://localhost:5000` in your browser

## Deployment (Railway)
The app auto-detects Python via Railpack. Connect a MySQL database service and Railway will automatically inject the following environment variables:
- `MYSQL_HOST`
- `MYSQL_USER`
- `MYSQL_PASSWORD`
- `MYSQL_DATABASE`

Set `ADMIN_PASSWORD` and `FLASK_SECRET_KEY` manually in the Railway service variables panel.

The database table is created automatically on first run.

## Environment Variables

| Variable           | Description                                              | Default                  |
|--------------------|----------------------------------------------------------|--------------------------|
| `MYSQL_HOST`       | Hostname of your MySQL server                            | `mysql.railway.internal` |
| `MYSQL_USER`       | MySQL username                                           | `root`                   |
| `MYSQL_PASSWORD`   | MySQL password                                           | *(empty)*                |
| `MYSQL_DATABASE`   | Name of the database to connect to                       | `railway`                |
| `ADMIN_PASSWORD`   | Password required to log in and access protected routes  | *(none — must be set)*   |
| `FLASK_SECRET_KEY` | Secret key used to sign session cookies                  | *(auto-generated)*       |

> **Note:** If `FLASK_SECRET_KEY` is not set, a random key is generated at startup. This means all sessions are invalidated on every restart. Set a stable value in production.

## API Endpoints

| Method   | Path                    | Auth Required | Description                                              |
|----------|-------------------------|---------------|----------------------------------------------------------|
| GET      | `/`                     | No            | Faculty profile page (PII hidden if not logged in)       |
| GET      | `/edit`                 | Yes           | Faculty edit page (redirects to `/login` if not logged in) |
| GET      | `/login`                | No            | Admin login page                                         |
| POST     | `/login`                | No            | Authenticate with password, creates session              |
| POST     | `/logout`               | No            | Clears session and logs out                              |
| GET      | `/api/faculty`          | No*           | Fetch faculty record (PII stripped if not logged in)     |
| GET      | `/api/faculty/list`     | No            | Fetch all faculty as `[{id, name}]` for selectors        |
| POST     | `/api/faculty`          | **Yes**       | Create a new faculty record                              |
| PUT      | `/api/faculty/<id>`     | **Yes**       | Update an existing faculty record by ID                  |
| DELETE   | `/api/faculty/<id>`     | **Yes**       | Delete a faculty record by ID                            |

\* `GET /api/faculty` is publicly accessible but returns a reduced payload — PII fields (`email`, `phone`, `office_location`, `office_schedule`) are omitted unless the request comes from an authenticated session.

## Authentication

The portal uses a simple password-based login system backed by server-side sessions.

- Visit `/login` and enter the admin password (default: `1234`, configured via `ADMIN_PASSWORD`)
- On success, a signed session cookie is set — no credentials are stored client-side
- Protected API endpoints (`POST`, `PUT`, `DELETE`) return `401 Unauthorized` if the session is not authenticated
- The `/edit` page redirects unauthenticated visitors to `/login`
- Call `POST /logout` (or click the Logout button) to clear the session

**Login flow:**
```http
POST /login
Content-Type: application/json

{ "password": "1234" }
```
Returns `{ "success": true }` on success, or `{ "error": "Invalid password" }` with HTTP 401 on failure.

## Security Features

- **PII protection** — `email`, `phone`, `office_location`, and `office_schedule` are stripped from all API responses for unauthenticated users
- **Parameterized SQL queries** — all database operations use `%s` placeholders via `mysql-connector-python`, preventing SQL injection
- **Environment variables for secrets** — `ADMIN_PASSWORD` and `FLASK_SECRET_KEY` are never hardcoded
- **Server-side sessions** — authentication state is stored in a signed, server-side session cookie; the password is never persisted in the browser

## How to Test CRUD Functionality

### Login First
1. Navigate to `http://localhost:5000/login`
2. Enter the admin password: `1234`
3. You will be redirected to `/edit` upon success

### CREATE — Add a Faculty Record
1. On the `/edit` page, leave the faculty selector blank (or choose "New Faculty")
2. Fill out all fields in the form
3. Click **"Save Changes"**
4. The new record is inserted and its ID is returned

**API equivalent:**
```http
POST /api/faculty
Content-Type: application/json

{
  "name": "Dr. Jane Smith",
  "title": "Professor",
  "department": "Computer Science",
  "campus_location": "Clearwater Campus",
  "office_location": "Building A, Room 210",
  "email": "jsmith@school.edu",
  "phone": "(555) 123-4567",
  "office_schedule": "Mon/Wed 2:00 PM – 4:00 PM",
  "about_me": "...",
  "education": "...",
  "research": "..."
}
```
Returns the created record with HTTP 201.

### READ — View Faculty Data
1. Visit the home page at `http://localhost:5000`
2. Faculty data is dynamically loaded from the MySQL database via the API
3. PII fields are visible only when logged in; unauthenticated visitors see a redacted profile

**API equivalent:**
```http
GET /api/faculty
GET /api/faculty?id=3
```
Returns the faculty record as a JSON object. PII fields are included only for authenticated sessions.

### UPDATE — Modify an Existing Record
1. Navigate to `http://localhost:5000/edit`
2. Select the faculty member from the dropdown
3. Modify any fields as needed
4. Click **"Save Changes"**

**API equivalent:**
```http
PUT /api/faculty/3
Content-Type: application/json

{
  "name": "Dr. Jane Smith",
  "title": "Associate Professor",
  ...
}
```
Returns the updated record on success, or `404` if the ID does not exist.

### DELETE — Remove a Faculty Record
1. Navigate to `http://localhost:5000/edit`
2. Select the faculty member from the dropdown
3. Click **"Delete"** and confirm the prompt

**API equivalent:**
```http
DELETE /api/faculty/3
```
Returns `{ "success": true, "message": "Faculty record 3 deleted" }` on success, or `404` if the ID does not exist.

### Logout
- Click the **Logout** button on the edit page, or send `POST /logout`
- The session is cleared and you are returned to the public view

---

## Technologies Used

| Technology                    | Version  | Purpose                                      |
|-------------------------------|----------|----------------------------------------------|
| Python                        | 3.8+     | Backend runtime                              |
| Flask                         | 2.3.3    | Web framework and API routing                |
| Flask-CORS                    | 4.0.0    | Cross-origin resource sharing support        |
| Werkzeug                      | 2.3.7    | WSGI utilities and session handling          |
| MySQL                         | 8.0      | Relational database for faculty data storage |
| mysql-connector-python        | 8.0.33   | Python driver for MySQL connectivity         |
| python-dotenv                 | 1.0.0    | Load environment variables from `.env`       |
| HTML5 / CSS3                  | —        | Frontend markup and styling                  |
| JavaScript (Fetch API)        | —        | Async API calls from the browser             |
| Bootstrap                     | 5.3.8    | Responsive UI components and layout          |