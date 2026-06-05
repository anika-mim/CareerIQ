PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS job_postings (
    job_id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_title TEXT NOT NULL,
    company TEXT,
    city TEXT,
    province TEXT,
    country TEXT NOT NULL DEFAULT 'Canada',
    employment_type TEXT,
    experience_level TEXT,
    min_years_experience REAL,
    max_years_experience REAL,
    salary_min REAL,
    salary_max REAL,
    posting_date TEXT,
    source TEXT,
    source_url TEXT,
    description TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS skills (
    skill_id INTEGER PRIMARY KEY AUTOINCREMENT,
    skill_name TEXT NOT NULL UNIQUE,
    skill_category TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS job_posting_skills (
    job_id INTEGER NOT NULL,
    skill_id INTEGER NOT NULL,
    is_required INTEGER NOT NULL DEFAULT 1,
    PRIMARY KEY (job_id, skill_id),
    FOREIGN KEY (job_id) REFERENCES job_postings (job_id) ON DELETE CASCADE,
    FOREIGN KEY (skill_id) REFERENCES skills (skill_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS candidate_profiles (
    candidate_id INTEGER PRIMARY KEY AUTOINCREMENT,
    resume_file_name TEXT,
    raw_resume_text TEXT,
    target_role TEXT,
    total_years_experience REAL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS candidate_skills (
    candidate_id INTEGER NOT NULL,
    skill_id INTEGER NOT NULL,
    confidence_score REAL NOT NULL DEFAULT 1.0,
    extraction_method TEXT NOT NULL DEFAULT 'rule_based',
    PRIMARY KEY (candidate_id, skill_id),
    FOREIGN KEY (candidate_id) REFERENCES candidate_profiles (candidate_id) ON DELETE CASCADE,
    FOREIGN KEY (skill_id) REFERENCES skills (skill_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS candidate_education (
    education_id INTEGER PRIMARY KEY AUTOINCREMENT,
    candidate_id INTEGER NOT NULL,
    institution TEXT,
    program TEXT,
    credential TEXT,
    graduation_year INTEGER,
    FOREIGN KEY (candidate_id) REFERENCES candidate_profiles (candidate_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS candidate_certifications (
    certification_id INTEGER PRIMARY KEY AUTOINCREMENT,
    candidate_id INTEGER NOT NULL,
    certification_name TEXT NOT NULL,
    issuer TEXT,
    issue_year INTEGER,
    FOREIGN KEY (candidate_id) REFERENCES candidate_profiles (candidate_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS candidate_experience (
    experience_id INTEGER PRIMARY KEY AUTOINCREMENT,
    candidate_id INTEGER NOT NULL,
    job_title TEXT,
    company TEXT,
    start_date TEXT,
    end_date TEXT,
    description TEXT,
    FOREIGN KEY (candidate_id) REFERENCES candidate_profiles (candidate_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS candidate_projects (
    project_id INTEGER PRIMARY KEY AUTOINCREMENT,
    candidate_id INTEGER NOT NULL,
    project_name TEXT,
    description TEXT,
    project_url TEXT,
    FOREIGN KEY (candidate_id) REFERENCES candidate_profiles (candidate_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS analysis_runs (
    analysis_id INTEGER PRIMARY KEY AUTOINCREMENT,
    candidate_id INTEGER NOT NULL,
    target_role TEXT,
    market_competitiveness_score REAL,
    employability_score REAL,
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (candidate_id) REFERENCES candidate_profiles (candidate_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS job_match_results (
    match_id INTEGER PRIMARY KEY AUTOINCREMENT,
    analysis_id INTEGER NOT NULL,
    job_id INTEGER,
    role_title TEXT,
    job_match_score REAL NOT NULL,
    matched_skill_count INTEGER NOT NULL DEFAULT 0,
    missing_skill_count INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (analysis_id) REFERENCES analysis_runs (analysis_id) ON DELETE CASCADE,
    FOREIGN KEY (job_id) REFERENCES job_postings (job_id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS skill_gap_results (
    gap_id INTEGER PRIMARY KEY AUTOINCREMENT,
    analysis_id INTEGER NOT NULL,
    skill_id INTEGER NOT NULL,
    demand_count INTEGER NOT NULL DEFAULT 0,
    demand_percentage REAL NOT NULL DEFAULT 0,
    priority_level TEXT NOT NULL DEFAULT 'medium',
    recommendation_reason TEXT,
    FOREIGN KEY (analysis_id) REFERENCES analysis_runs (analysis_id) ON DELETE CASCADE,
    FOREIGN KEY (skill_id) REFERENCES skills (skill_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_job_postings_title ON job_postings (job_title);
CREATE INDEX IF NOT EXISTS idx_job_postings_city ON job_postings (city);
CREATE INDEX IF NOT EXISTS idx_job_postings_experience ON job_postings (experience_level);
CREATE INDEX IF NOT EXISTS idx_skills_name ON skills (skill_name);
CREATE INDEX IF NOT EXISTS idx_analysis_candidate ON analysis_runs (candidate_id);

