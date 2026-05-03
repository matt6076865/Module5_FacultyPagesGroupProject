-- =============================================================================
-- Faculty Portal — Database Schema
-- =============================================================================
-- This file documents the MySQL table structure used by the Faculty Portal
-- application (app.py).  It can be run directly against a MySQL instance to
-- create the schema from scratch, or used as a reference when restoring the
-- database.
--
-- Usage:
--   mysql -u <user> -p <database> < facultydatabase_schema.sql
--
-- The IF NOT EXISTS guard makes it safe to run multiple times without
-- destroying existing data.
-- =============================================================================

-- -----------------------------------------------------------------------------
-- Table: faculty
--
-- Stores the profile information for a single faculty member that is displayed
-- on the Faculty Portal website.  The application reads the most-recently
-- inserted row (ORDER BY id DESC LIMIT 1) and allows it to be updated via the
-- /edit page.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS faculty (
    -- Surrogate primary key, auto-incremented by MySQL.
    id               INT           AUTO_INCREMENT PRIMARY KEY,

    -- Full display name of the faculty member (e.g. "Dr. Jane Smith").
    name             VARCHAR(255)  NOT NULL,

    -- Academic or professional title (e.g. "Associate Professor").
    title            VARCHAR(255),

    -- Campus where the faculty member is primarily located
    -- (e.g. "Clearwater Campus").
    campus_location  VARCHAR(255),

    -- Academic department the faculty member belongs to
    -- (e.g. "Computer and Information Technology").
    department       VARCHAR(255),

    -- Physical office location on campus (e.g. "Building A, Room 210").
    office_location  VARCHAR(255),

    -- Institutional e-mail address (e.g. "jsmith@school.edu").
    email            VARCHAR(255),

    -- Office phone number, including area code (e.g. "(555) 123-4567").
    phone            VARCHAR(20),

    -- Days and times the faculty member holds office hours
    -- (e.g. "Mon/Wed 2:00 PM to 4:00 PM").
    office_schedule  VARCHAR(255),

    -- Free-form biographical text displayed in the "About Me" section.
    about_me         TEXT,

    -- Free-form text describing the faculty member's educational background.
    education        TEXT,

    -- Free-form text describing research interests and publications.
    research         TEXT,

    -- Timestamp set automatically when the row is first inserted.
    created_at       TIMESTAMP     DEFAULT CURRENT_TIMESTAMP,

    -- Timestamp updated automatically whenever the row is modified.
    updated_at       TIMESTAMP     DEFAULT CURRENT_TIMESTAMP
                                   ON UPDATE CURRENT_TIMESTAMP
);
