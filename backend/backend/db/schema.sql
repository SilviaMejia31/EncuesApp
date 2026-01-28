-- Database schema (SQLite)

CREATE TABLE countries (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL
);

CREATE TABLE companies (
  id INTEGER PRIMARY KEY,
  country_id INTEGER,
  name TEXT NOT NULL
);

CREATE TABLE branches (
  id INTEGER PRIMARY KEY,
  company_id INTEGER,
  name TEXT NOT NULL
);

CREATE TABLE questions (
  id INTEGER PRIMARY KEY,
  text TEXT NOT NULL
);

CREATE TABLE survey_responses (
  id INTEGER PRIMARY KEY,
  branch_id INTEGER,
  created_at TEXT
);

CREATE TABLE answers (
  id INTEGER PRIMARY KEY,
  survey_response_id INTEGER,
  question_id INTEGER,
  value TEXT
);
