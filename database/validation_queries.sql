-- CareerIQ Milestone 2 validation queries
-- Run these after loading data into data/processed/careeriq_dev.sqlite.

-- 1. Confirm core row counts.
SELECT 'job_postings' AS table_name, COUNT(*) AS row_count FROM job_postings
UNION ALL
SELECT 'skills', COUNT(*) FROM skills
UNION ALL
SELECT 'job_posting_skills', COUNT(*) FROM job_posting_skills;

-- 2. Most in-demand skills.
SELECT
    s.skill_name,
    s.skill_category,
    COUNT(*) AS posting_count
FROM job_posting_skills AS jps
JOIN skills AS s
    ON s.skill_id = jps.skill_id
GROUP BY s.skill_id, s.skill_name, s.skill_category
ORDER BY posting_count DESC, s.skill_name
LIMIT 10;

-- 3. Top hiring cities.
SELECT
    city,
    province,
    COUNT(*) AS posting_count
FROM job_postings
GROUP BY city, province
ORDER BY posting_count DESC, city;

-- 4. Experience demand by level.
SELECT
    experience_level,
    COUNT(*) AS posting_count,
    ROUND(AVG(min_years_experience), 1) AS avg_min_years
FROM job_postings
GROUP BY experience_level
ORDER BY posting_count DESC;

-- 5. Role category demand using simple title grouping.
SELECT
    CASE
        WHEN LOWER(job_title) LIKE '%data%' OR LOWER(job_title) LIKE '%bi%' OR LOWER(job_title) LIKE '%report%' THEN 'Data and BI'
        WHEN LOWER(job_title) LIKE '%business%' OR LOWER(job_title) LIKE '%process%' THEN 'Business Analysis'
        WHEN LOWER(job_title) LIKE '%support%' OR LOWER(job_title) LIKE '%desk%' OR LOWER(job_title) LIKE '%technician%' OR LOWER(job_title) LIKE '%it analyst%' THEN 'IT and User Support'
        ELSE 'Other'
    END AS role_category,
    COUNT(*) AS posting_count
FROM job_postings
GROUP BY role_category
ORDER BY posting_count DESC;

