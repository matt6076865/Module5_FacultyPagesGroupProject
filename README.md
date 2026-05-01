Module5_FacultyPagesGroupProject - SPC - COP 4504 - DEV TEAM 2 - 2026
This is a Dev Team 2 Group project that was based on a prior forked one.
This project adds a Python/Flask backend with MySQL database support for dynamic faculty data management.
Contributors: Matthew W., Dannielle M., Jacob G., and LeEric R.

## Project Structure
```
/
├── app.py                  - Flask application and API routes
├── requirements.txt        - Python dependencies
├── templates/
│   ├── index.html          - Faculty profile page (dynamic, API-driven)
│   └── edit.html           - Faculty edit form (loads/saves via API)
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
- REST API (`/api/faculty`) for reading and updating faculty information
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
3. Create a `.env` file with your database credentials:
   ```
   MYSQL_HOST=localhost
   MYSQL_USER=root
   MYSQL_PASSWORD=yourpassword
   MYSQL_DATABASE=faculty_portal
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

The database table is created automatically on first run.

## API Endpoints
| Method | Path          | Description                        |
|--------|---------------|------------------------------------|
| GET    | `/`           | Faculty profile page               |
| GET    | `/edit`       | Faculty edit page                  |
| GET    | `/api/faculty`| Fetch current faculty data (JSON)  |
| POST   | `/api/faculty`| Save updated faculty data (JSON)   |

## Notes
- If no faculty record exists in the database, the API returns default placeholder data
- Static assets are served from the `static/` folder
- Place profile images in `static/images/` for Flask to serve them correctly
