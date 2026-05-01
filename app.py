from flask import Flask, render_template, request, redirect, url_for, flash
import os
from dotenv import load_dotenv
import mysql.connector

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )
def split_name(full_name):
    parts = full_name.strip().split(" ", 1)
    first_name = parts[0]
    last_name = parts[1] if len(parts) > 1 else ""
    return first_name, last_name


def format_phone(phone):
    digits = ''.join(filter(str.isdigit, phone))

    if len(digits) == 10:
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    
    return phone  # fallback if not valid    

def get_or_create_department(cursor, dept_name):
    if not dept_name:
        return None

    cursor.execute(
        "select dept_id from departments where dept_name = %s",
        (dept_name,)
    )
    department = cursor.fetchone()

    if department:
        return department[0]

    cursor.execute(
        "insert into departments (dept_name) values (%s)",
        (dept_name,)
    )

    return cursor.lastrowid

@app.route("/")
def home():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        select f.*, d.dept_name
        from faculty f
        left join departments d on f.dept_id = d.dept_id
        order by f.faculty_id desc
        limit 1
    """)

    faculty = cursor.fetchone()

    courses = []
    if faculty:
        cursor.execute("""
            select c.course_id
            from faculty_courses fc
            join courses c on fc.course_id = c.course_id
            where fc.faculty_id = %s
        """, (faculty["faculty_id"],))
        courses = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("index.html", faculty=faculty, courses=courses)


@app.route("/edit")
def edit():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        select f.*, d.dept_name
        from faculty f
        left join departments d on f.dept_id = d.dept_id
        order by f.faculty_id desc
        limit 1
    """)

    faculty = cursor.fetchone()

    selected_courses = []
    if faculty:
        cursor.execute("""
            select course_id
            from faculty_courses
            where faculty_id = %s
        """, (faculty["faculty_id"],))
        selected_courses = [row["course_id"] for row in cursor.fetchall()]

    cursor.close()
    conn.close()

    return render_template(
        "edit.html",
        faculty=faculty,
        selected_courses=selected_courses
    )


@app.route("/save", methods=["POST"])
def save():
    faculty_id = request.form.get("faculty_id")
    name = request.form.get("name")
    title = request.form.get("title")
    campus = request.form.get("campus")
    department = request.form.get("department")
    office_location = request.form.get("office_location")
    email = request.form.get("email")
    office_phone = format_phone(request.form.get("office_phone"))
    office_hours = request.form.get("office_hours")
    about_me = request.form.get("about_me")
    education = request.form.get("education")
    research_publications = request.form.get("research_publications")
    courses = request.form.getlist("courses")

    if not name or not email:
        flash("Name and email are required.")
        return redirect(url_for("edit"))

    first_name, last_name = split_name(name)

    conn = get_db_connection()
    cursor = conn.cursor()

    dept_id = get_or_create_department(cursor, department)

    if faculty_id:
        cursor.execute("""
            update faculty
            set title = %s,
                first_name = %s,
                last_name = %s,
                campus_location = %s,
                office_location = %s,
                email_address = %s,
                phone_number = %s,
                about_me = %s,
                education = %s,
                research_publications = %s,
                office_hours = %s,
                dept_id = %s
            where faculty_id = %s
        """, (
            title,
            first_name,
            last_name,
            campus,
            office_location,
            email,
            office_phone,
            about_me,
            education,
            research_publications,
            office_hours,
            dept_id,
            faculty_id
        ))
    else:
        cursor.execute("""
            insert into faculty
            (
                title,
                first_name,
                last_name,
                campus_location,
                office_location,
                email_address,
                phone_number,
                about_me,
                education,
                research_publications,
                office_hours,
                dept_id
            )
            values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            title,
            first_name,
            last_name,
            campus,
            office_location,
            email,
            office_phone,
            about_me,
            education,
            research_publications,
            office_hours,
            dept_id
        ))

        faculty_id = cursor.lastrowid

    cursor.execute(
        "delete from faculty_courses where faculty_id = %s",
        (faculty_id,)
    )

    for course_id in courses:
        cursor.execute("""
            insert into faculty_courses (faculty_id, course_id, semester_code)
            values (%s, %s, %s)
        """, (faculty_id, course_id, "SPR26"))

    conn.commit()
    cursor.close()
    conn.close()

    flash("Faculty profile saved successfully.")
    return redirect(url_for("home"))

@app.route("/delete-course/<int:faculty_id>/<course_id>", methods=["POST"])
def delete_course(faculty_id, course_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        delete from faculty_courses
        where faculty_id = %s and course_id = %s
    """, (faculty_id, course_id))

    conn.commit()
    cursor.close()
    conn.close()

    flash("Course deleted successfully.")
    return redirect(url_for("edit"))


@app.route("/db-test")
def db_test():
    try:
        conn = get_db_connection()
        conn.close()
        return "Database connection successful."
    except mysql.connector.Error as error:
        return f"Database connection failed: {error}"


if __name__ == "__main__":
    app.run(debug=True)