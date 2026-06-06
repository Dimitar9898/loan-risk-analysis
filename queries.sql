-- ============================================================
-- LOAN DEFAULT RISK ANALYSIS
-- Dataset: LendingClub loan data
-- Goal: Identify which borrower characteristics predict default
-- ============================================================
 
 
-- ============================================================
-- SECTION 1: BASIC AGGREGATIONS
-- ============================================================
 
-- overall default rate across all loans
SELECT COUNT(*) as total_loans,
       SUM(target_default) as total_defaults,
       ROUND(AVG(target_default) * 100, 2) as default_rate_pct
FROM loans;
 
 
-- default rate by grade, as grade gets worse, default rate increases consistently
SELECT grade,
       COUNT(*) as total_loans,
       SUM(target_default) as defaults,
       ROUND(AVG(target_default) * 100, 2) as default_rate_pct
FROM loans
GROUP BY grade
ORDER BY grade;
 
 
-- default rate by loan purpose, small business is riskiest at 26%, credit card safest at 10%
SELECT purpose,
       COUNT(*) as total_loans,
       ROUND(AVG(target_default) * 100, 2) as default_rate_pct
FROM loans
GROUP BY purpose
ORDER BY default_rate_pct DESC;
 
 
-- default rate by home ownership, mortgage holders are most reliable, renters slightly riskier
SELECT home_ownership,
       COUNT(*) as total_loans,
       ROUND(AVG(target_default) * 100, 2) as default_rate_pct
FROM loans
GROUP BY home_ownership
ORDER BY default_rate_pct DESC;
 
 
-- ============================================================
-- SECTION 2: WHERE AND HAVING
-- ============================================================
 
-- among high DTI borrowers (above 20), grade still predicts default rate well
-- the grading system holds up even for already risky borrowers
SELECT grade,
       ROUND(AVG(dti), 2) as avg_dti,
       COUNT(*) as total_loans,
       ROUND(AVG(target_default) * 100, 2) as default_rate_pct
FROM loans
WHERE dti > 20
GROUP BY grade
ORDER BY default_rate_pct DESC;
 
 
-- grades with default rate above 20% — these are candidates for stricter lending or higher rates
SELECT grade,
       COUNT(*) as total_loans,
       ROUND(AVG(target_default) * 100, 2) as default_rate_pct
FROM loans
GROUP BY grade
HAVING AVG(target_default) > 0.20
ORDER BY default_rate_pct DESC;
 
 
-- ============================================================
-- SECTION 3: CASE WHEN
-- ============================================================
 
-- group grades into risk buckets — high risk borrowers default at nearly 3x the rate of low risk
SELECT
    CASE
        WHEN grade IN ('A', 'B') THEN 'Low Risk'
        WHEN grade IN ('C', 'D') THEN 'Medium Risk'
        WHEN grade IN ('E', 'F', 'G') THEN 'High Risk'
    END as risk_category,
    COUNT(*) as total_loans,
    ROUND(AVG(target_default) * 100, 2) as default_rate_pct
FROM loans
GROUP BY risk_category
ORDER BY default_rate_pct DESC;
 
 
-- ============================================================
-- SECTION 4: SUBQUERIES
-- ============================================================
 
-- borrowers with above average loan amounts — do they default more?
-- grade F has the highest default rate at 31.5% among above-average loan amounts
SELECT grade,
       ROUND(AVG(loan_amnt), 2) as avg_loan,
       ROUND(AVG(target_default) * 100, 2) as default_rate_pct
FROM loans
WHERE loan_amnt > (SELECT AVG(loan_amnt) FROM loans)
GROUP BY grade
ORDER BY default_rate_pct DESC;
 
 
-- ============================================================
-- SECTION 5: CTEs
-- ============================================================
 
-- calculate default rate per grade then rank them in the same query
-- G is rank 1 meaning highest default rate, A is rank 7 meaning lowest
WITH default_by_grade AS (
    SELECT grade,
           COUNT(*) as total_loans,
           ROUND(AVG(target_default) * 100, 2) as default_rate_pct
    FROM loans
    GROUP BY grade
)
SELECT grade,
       total_loans,
       default_rate_pct,
       RANK() OVER (ORDER BY default_rate_pct DESC) as risk_rank
FROM default_by_grade;
 
 
-- ============================================================
-- SECTION 6: WINDOW FUNCTIONS
-- ============================================================
 
-- rank states by default rate — shows the 10 riskiest states
SELECT
    addr_state,
    COUNT(*) as total_loans,
    ROUND(AVG(target_default) * 100, 2) as default_rate_pct,
    RANK() OVER (ORDER BY AVG(target_default) DESC) as risk_rank
FROM loans
GROUP BY addr_state
ORDER BY risk_rank
LIMIT 10;
 
 
-- rank loans by amount within each grade using PARTITION BY
-- each grade gets its own ranking starting from 1
-- also shows the average loan amount for that grade on every row
SELECT
    grade,
    loan_amnt,
    ROUND(AVG(loan_amnt) OVER (PARTITION BY grade), 2) as grade_avg_loan,
    RANK() OVER (PARTITION BY grade ORDER BY loan_amnt DESC) as rank_within_grade
FROM loans
LIMIT 20;


-- multi factor risk profile
-- borrowers who combine bad grade + high dti + renting + small business
WITH risk_profile AS (
    SELECT *,
        CASE
            WHEN grade IN ('E','F','G') THEN 1 ELSE 0 END +
        CASE WHEN dti > 20 THEN 1 ELSE 0 END +
        CASE WHEN home_ownership = 'RENT' THEN 1 ELSE 0 END +
        CASE WHEN purpose = 'small_business' THEN 1 ELSE 0 END
        as risk_score
    FROM loans
)
SELECT risk_score,
       COUNT(*) as total_loans,
       ROUND(AVG(target_default) * 100, 2) as default_rate_pct
FROM risk_profile
GROUP BY risk_score
ORDER BY risk_score DESC;

-- multi-factor risk scoring: each additional risk flag compounds default probability
-- borrowers with 3+ flags default at 3x the rate of clean borrowers
-- recommendation: use risk score alongside grade for better lending decisions
-- note: risk score 4 has only 19 loans so the result is not statistically reliable due to small sample size
