# -----------------------------------------------------------
# PROBLEM STATEMENT
# -----------------------------------------------------------
# We want to predict whether a borrower will default on their loan
# given information available at the time the loan was issued.
# This is a binary classification problem:
# 1 = defaulted (Charged Off), 0 = paid back (Fully Paid / Current)
#
# We only use pre-loan columns — columns like recoveries, total_pymnt,
# and collection_recovery_fee only exist after a default has already happened,
# so including them would be cheating (data leakage).




import pandas as pd
import numpy as np
from pathlib import Path
 
# -----------------------------------------------------------
# LOAD DATA
# -----------------------------------------------------------
# Path.home() makes this work on any machine, not just mine
path = Path.home() / "Downloads" / "loan (1).csv"
 
df = pd.read_csv(
    path,
    encoding="latin1",  # handles special characters in the CSV
    dtype=str,          # read everything as string first, we cast manually below
    engine="python"
)
 
# drop columns that are completely empty or have only one unique value (no information)
df = df.dropna(axis=1, how="all")
df = df.loc[:, df.nunique(dropna=False) > 1]
 
# drop columns we will never use — identifiers and free text fields
df = df.drop(columns=[c for c in ["id", "member_id", "url", "title", "desc"] if c in df.columns])
 
 
# -----------------------------------------------------------
# SCHEMA DEFINITION
# based on the LendingClub data dictionary
# -----------------------------------------------------------
 
# only keeping pre-loan columns — post-loan columns like recoveries or total_pymnt
# would leak information about the outcome we are trying to predict
numeric_cols = [
    "loan_amnt", "funded_amnt",
    "installment", "annual_inc", "dti",
    "delinq_2yrs", "inq_last_6mths",
    "open_acc", "pub_rec", "revol_bal",
    "total_acc", "pub_rec_bankruptcies",
    "tax_liens", "mths_since_last_delinq",
    "mths_since_last_record"
]
 
# stored as strings with a % sign, need to strip that before converting
percent_cols = [
    "int_rate",
    "revol_util"
]
 
# stored as "Jan-14" format, need to parse correctly
date_cols = [
    "issue_d",
    "earliest_cr_line",
    "last_pymnt_d",
    "last_credit_pull_d"
]
 
categorical_cols = [
    "term", "grade", "sub_grade",
    "home_ownership", "verification_status", "loan_status",
    "purpose", "zip_code", "addr_state",
    "initial_list_status", "application_type",
    "emp_title", "emp_length"
]
 
 
# -----------------------------------------------------------
# SCHEMA VALIDATION
# check if any columns were missed or don't exist in the data
# -----------------------------------------------------------
schema_cols = set(numeric_cols + percent_cols + date_cols + categorical_cols)
df_cols = set(df.columns)
 
missing_in_df = schema_cols - df_cols
missing_in_schema = df_cols - schema_cols
 
if missing_in_df:
    print("In schema but not in data:", missing_in_df)
if missing_in_schema:
    print("In data but not classified:", missing_in_schema)
 
# filter each list to only columns that actually exist in the dataframe
# prevents crashes if a column is missing
numeric_cols = [col for col in numeric_cols if col in df.columns]
percent_cols = [col for col in percent_cols if col in df.columns]
date_cols = [col for col in date_cols if col in df.columns]
categorical_cols = [col for col in categorical_cols if col in df.columns]
 
 
# -----------------------------------------------------------
# TYPE CASTING
# -----------------------------------------------------------
 
# convert to numbers — any value that can't be converted becomes NaN
df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors="coerce")
 
# strip the % sign then convert to number
for col in percent_cols:
    df[col] = df[col].str.replace("%", "", regex=False)
    df[col] = pd.to_numeric(df[col], errors="coerce")
 
# dates are stored as "Jan-14" so we specify the format explicitly
for col in date_cols:
    df[col] = pd.to_datetime(df[col], format="%b-%y", errors="coerce")
 
# category dtype is more memory efficient than storing repeated strings
for col in categorical_cols:
    df[col] = df[col].astype("category")
 
 
# -----------------------------------------------------------
# MISSING VALUES
# -----------------------------------------------------------
print("\nMissing values before cleaning:")
print(df.isnull().sum()[df.isnull().sum() > 0])
 
# next_pymnt_d is 97% empty so not worth keeping
df = df.drop(columns=["next_pymnt_d"], errors="ignore")
 
# for these columns, missing means the event never happened so 0 makes sense
for col in ["collections_12_mths_ex_med", "chargeoff_within_12_mths", "tax_liens", "pub_rec_bankruptcies"]:
    df[col] = df[col].fillna(0)
 
# same logic — no delinquency or public record on file means 0 months since last one
df["mths_since_last_delinq"] = df["mths_since_last_delinq"].fillna(0)
df["mths_since_last_record"] = df["mths_since_last_record"].fillna(0)
 
# flag rows where revol_util was missing before we fill it
# useful to keep this information rather than just losing it
df["revol_util_missing"] = df["revol_util"].isna().astype(int)
df["revol_util"] = df["revol_util"].fillna(df["revol_util"].median())
 
# emp_title and emp_length are categorical so we fill with "Unknown"
# need to convert back to object first because category dtype only allows existing categories
df["emp_title"] = df["emp_title"].astype("object").fillna("Unknown")
df["emp_length"] = df["emp_length"].astype("object").fillna("Unknown")
 
 
# -----------------------------------------------------------
# FEATURE ENGINEERING
# -----------------------------------------------------------
 
# replace 0 income with NaN to avoid division by zero in the ratios below
df["annual_inc"] = df["annual_inc"].replace(0, np.nan)
 
# how large is the loan relative to the borrower's income
df["loan_to_income"] = df["loan_amnt"] / df["annual_inc"]
 
# how much of monthly income goes toward this loan payment
df["installment_ratio"] = df["installment"] / df["annual_inc"]
 
# how many years of credit history the borrower had when they took the loan
df["credit_age_years"] = (df["issue_d"] - df["earliest_cr_line"]).dt.days / 365
 
# how many days between loan issue and last payment
df["loan_duration_days"] = (df["last_pymnt_d"] - df["issue_d"]).dt.days
 
# binary flags for high risk indicators
df["high_dti_flag"] = (df["dti"] > 20).astype(int)
df["high_interest_flag"] = (df["int_rate"] > 15).astype(int)
 
 
# -----------------------------------------------------------
# TARGET VARIABLE
# -----------------------------------------------------------
# 1 = loan was charged off (defaulted), 0 = fully paid or current
df["target_default"] = (df["loan_status"] == "Charged Off").astype(int)
 
 
# -----------------------------------------------------------
# SUMMARY
# -----------------------------------------------------------
print(f"\nShape: {df.shape}")
print(f"Default rate: {df['target_default'].mean():.1%}")
print("\nRemaining missing values:")
missing = df.isnull().sum()[df.isnull().sum() > 0]
print(missing if not missing.empty else "None")
 