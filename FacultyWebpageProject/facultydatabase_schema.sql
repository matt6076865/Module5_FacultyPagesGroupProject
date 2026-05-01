-- Dev Team 2: Matt W, LeEric R., Danneille M., and Jacob G. 
-- Create the Database
CREATE DATABASE IF NOT EXISTS FacultyDatabase;
USE FacultyDatabase;

-- Create Departments Table (3NF)
CREATE TABLE departments (
    dept_id INT AUTO_INCREMENT PRIMARY KEY,
    dept_name VARCHAR(100) NOT NULL UNIQUE
);

-- Create Faculty Table
CREATE TABLE faculty (
    faculty_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(50) NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    campus_location VARCHAR(50) NOT NULL,
    office_location VARCHAR(100),
    email_address VARCHAR(100) UNIQUE NOT NULL,
    phone_number VARCHAR(20),
    about_me TEXT,
    education TEXT,
    research_publications TEXT,
    office_hours VARCHAR(255),
    dept_id INT,
    CONSTRAINT chk_email_format
        CHECK (email_address like '%@%'),
    CONSTRAINT fk_faculty_dept
        FOREIGN KEY (dept_id) REFERENCES departments(dept_id)
        ON DELETE SET NULL
);

-- Create Courses Table (Simulating ERP/PeopleSoft data)
CREATE TABLE courses (
    course_id VARCHAR(20) PRIMARY KEY,
    course_name VARCHAR(150) NOT NULL,
    credits INT DEFAULT 3,
    CONSTRAINT chk_credits
		CHECK (credits BETWEEN 1 AND 5)
);

-- Create Faculty_Courses Junction Table (Many-to-Many)
CREATE TABLE faculty_courses (
    faculty_id INT,
    course_id VARCHAR(20),
    semester_code VARCHAR(10),
    PRIMARY KEY (faculty_id, course_id, semester_code),
    CONSTRAINT fk_junction_faculty
        FOREIGN KEY (faculty_id) REFERENCES faculty(faculty_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_junction_course
        FOREIGN KEY (course_id) REFERENCES courses(course_id)
        ON DELETE CASCADE
);

-- Inserting Courses for testing
INSERT INTO courses (course_id, course_name, credits)
VALUES
	('COP1000', 'Introduction to Programming', 3),
	('COP1044', 'Python Programming', 3),
	('COP3505', 'Advanced Programming', 3),
	('COP4504', 'Advanced Software Programming', 3),
	('ISM3212', 'Database Management', 3),
	('ISM3232', 'Applied Systems Analysis', 3),
	('ISM4914', 'Project Management', 3),
	('ISM4915', 'Capstone Project', 3
);

USE SchoolDatabase;
SHOW TABLES;

DESCRIBE faculty;
DESCRIBE departments;
DESCRIBE courses;
DESCRIBE faculty_courses;
