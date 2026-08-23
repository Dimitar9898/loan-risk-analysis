# Loan Risk Analysis

## What This Project Does

This project takes raw LendingClub loan data and turns it into something useful. 
The data comes in messy, with wrong types, missing values, and columns that need to be dropped or transformed. 
The pipeline cleans all of that, loads it into a database, and runs SQL analysis to answer one core question: which borrower characteristics predict loan default?


---

## The Business Problem

LendingClub needs to know which borrowers are likely to default before approving a loan. 
This project builds a profile of high risk borrowers using historical loan data. 
The findings can help lenders decide who to approve, what interest rate to charge, and which combinations of risk factors to watch out for.
---
Dashboard
The Tableau dashboard shows the key findings visually. It covers default rate by grade, loan purpose, employment length, and state, plus average loan amount by grade.

[View the live dashboard here] (https://public.tableau.com/views/LendingClub_17806833936180/Dashboard2)

## Dataset
The dataset comes from LendingClub and contains 39,717 loans with information on borrower income, credit history, loan purpose, grade, and repayment status. 14.2% of loans in the dataset ended in default.
  
## Tools

Python, pandas, NumPy, SQLite, DBeaver, Tableau


## What the Pipeline Does

The pipeline in loans.py drops empty and useless columns, 
removes post loan outcome columns to prevent data leakage, 
converts all fields to the correct types, 
fills missing values based on business logic,
creates new features like loan to income ratio and risk flags, 
and defines the target variable where 1 means default and 0 means fully paid.


---## SQL Analysis

The queries in queries.sql cover default rates by grade, purpose, and home ownership, filtering with WHERE and HAVING, CASE WHEN risk buckets, subqueries, CTEs, and window functions with PARTITION BY.

The key finding is that borrowers with 3 or more risk flags default at 3 times the rate of clean borrowers. 


---

## Dashboard

The Tableau dashboard shows the key findings visually. It covers default rate by grade, loan purpose, employment length, and state, plus average loan amount by grade.

[View the live dashboard here]
(https://public.tableau.com/views/LendingClub_17806833936180/Dashboard2)


## Project Structure

loans.py runs the full cleaning pipeline and exports the data to SQLite and CSV. 
queries.sql contains all SQL analysis organized by concept. loans.db is the SQLite database. 
loans_clean.csv is the cleaned dataset used by Tableau.



## How to Run It
The LendingClub loan dataset used in this project is available for download here:

[Download LendingClub Dataset](https://drive.google.com/file/d/1DtdOEFL9l5LCCUjXZBeHlrDJ7YmIgvQR/view)

The dataset was originally obtained from Kaggle and contains historical loan records used for credit risk analysis.

Place the downloaded CSV file in your `Downloads` folder and run `loans.py` to execute the ETL pipeline.

After the pipeline completes:
- Run SQL queries from `queries.sql` to analyze loan risk factors
- Open the Tableau dashboard to explore borrower risk trends
