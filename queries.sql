SELECT COUNT (*) as total_loans, 
		SUM (target_default) as total_defaults, 
		ROUND (AVG(target_default) * 100,2) as default_rate_pct
FROM loans;


SELECT grade,
       COUNT(*) as total_loans,
       SUM(target_default) as defaults,
       ROUND(AVG(target_default) * 100, 2) as default_rate_pct
FROM loans
GROUP BY grade
ORDER BY grade;

# we can see as the grade gets worse, so the does the default rate 


SELECT purpose,
       COUNT(*) as total_loans,
       ROUND(AVG(target_default) * 100, 2) as default_rate_pct
FROM loans
GROUP BY purpose
ORDER BY default_rate_pct DESC;


SELECT home_ownership,
       COUNT(*) as total_loans,
       ROUND(AVG(target_default) * 100, 2) as default_rate_pct
FROM loans
GROUP BY home_ownership
ORDER BY default_rate_pct DESC;

#small_business have the highest default_rate at 26% , credit card card and car loans are safest around 10%



SELECT grade, 
       ROUND(AVG(dti), 2) as avg_dti,
       COUNT(*) as total_loans,
       ROUND(AVG(target_default) * 100, 2) as default_rate_pct
FROM loans
WHERE dti > 20
GROUP BY grade
ORDER BY default_rate_pct DESC;

# among high dti above 20, the pattern still holds, grade f still has the highest default rate and higher dti


SELECT grade,
       COUNT(*) as total_loans,
       ROUND(AVG(target_default) * 100, 2) as default_rate_pct
FROM loans
GROUP BY grade
HAVING AVG(target_default) > 0.20
ORDER BY default_rate_pct DESC;

# which grades should we reduce lending to or charge higher interest rates, as they have the highest default rates


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

# as risk increases so does default rate, so better to avoid high risk as much as possible



SELECT grade,
       ROUND(AVG(loan_amnt), 2) as avg_loan,
       ROUND(AVG(target_default) * 100, 2) as default_rate_pct
FROM loans
WHERE loan_amnt > (SELECT AVG(loan_amnt) FROM loans)
GROUP BY grade
ORDER BY default_rate_pct DESC;

# so loan amounts higher than average also have higher default rate the higher the grade is with f being 31.52 default rate



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

