CREATE TABLE students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password_hash TEXT,
    role TEXT DEFAULT 'student'
);

CREATE TABLE problems (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    description TEXT,
    language TEXT
);

CREATE TABLE test_cases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    problem_id INTEGER,
    input TEXT,
    expected_output TEXT
);

CREATE TABLE submissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER,
    problem_id INTEGER,
    code TEXT,
    language TEXT,
    score INTEGER,
    penalty INTEGER,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE testcases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    problem_id INTEGER,
    input TEXT,
    output TEXT
);