# Loan Risk Analysis Project

## Overview
This project focuses on cleaning and preparing a real-world loan dataset from LendingClub. The goal was to take raw, inconsistent data and turn it into a structured dataset suitable for analysis and future modeling work.

The main focus was on building a solid data cleaning pipeline and creating meaningful features that could later be used for risk analysis or predictive modeling.

---

## Objective
The main objectives of this project were:
- Clean and standardize raw loan data
- Fix incorrect data types (numeric, categorical, and date fields)
- Handle missing values in a consistent way
- Create additional features for financial analysis
- Prepare the dataset for SQL analysis or modeling

---

## Dataset
The dataset contains loan-level information including borrower details, loan amounts, interest rates, and repayment history. It is commonly used for credit risk analysis.

Key types of information include:
- Loan amounts and funding details
- Borrower income and debt ratios
- Payment history
- Credit history variables

---

## Tools Used
- Python
- pandas
- NumPy

---

## Data Cleaning Process
Several steps were performed to clean and structure the dataset:

- Removed empty columns and constant-value columns
- Converted numeric fields that were stored as strings
- Cleaned percentage-based columns such as interest rate and utilization rate
- Converted date fields into proper datetime format
- Standardized categorical columns
- Addressed missing values in key fields

---

## Feature Engineering
To support analysis, additional variables were created:

- loan_to_income: ratio of loan amount to annual income
- installment_ratio: monthly installment relative to income
- credit_age_years: length of credit history
- loan_duration_days: duration between issue date and last payment
- high_dti_flag: indicator for high debt-to-income ratio
- high_interest_flag: indicator for high interest rate loans
- revol_util_missing: flag for missing credit utilization data

---

## Notes on Data Quality
Some columns contained missing or incomplete values, particularly in credit history and utilization fields. These were handled either through imputation or by creating missing-data indicators.

---

## Next Steps
- Export cleaned dataset for SQL analysis
- Build dashboards for loan performance insights
- Perform exploratory risk segmentation
- Potentially develop a predictive model for loan default risk
