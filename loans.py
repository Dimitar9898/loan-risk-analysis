import pandas as pd
import numpy as np
from pathlib import Path
import gdown
import os
import mysql.connector
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

 
 
# -----------------------------------------------------------
# PROBLEM STATEMENT
# -----------------------------------------------------------
# Goal: predict whether a borrower will default on their loan
# using only information available at the time the loan was issued.
#
# Target variable: 1 = defaulted (Charged Off), 0 = paid back
#
# Post-loan columns like recoveries and total_pymnt are excluded
# because they only exist after a default has already happened.
# Using them would mean training on the answer, not the inputs.
 
 
# -----------------------------------------------------------
# LOAD DATA
# -----------------------------------------------------------
 
# pulls the file from Google Drive if it's not already downloaded
file_path = Path.home() / "Downloads" / "loan (1).csv"
if not file_path.exists():
    print("Downloading dataset from Google Drive...")
    gdown.download("https://drive.google.com/uc?id=1DtdOEFL9l5LCCUjXZBeHlrDJ7YmIgvQR", str(file_path), quiet=False)
 
# everything is read as a string first so type conversion can be done manually and controlled
df = pd.read_csv(
    file_path,
    encoding="latin1",  # latin1 handles special characters that break the default utf-8 reader
    dtype=str,
    engine="python"
)
 
# columns that are entirely empty or have only one value carry no information
df = df.dropna(axis=1, how="all")
df = df.loc[:, df.nunique(dropna=False) > 1]
 
# identifiers and free text fields are useless for analysis
df = df.drop(columns=[c for c in ["id", "member_id", "url", "title", "desc"] if c in df.columns])
 
# these columns only exist after a loan has defaulted — keeping them would leak the outcome
post_loan_cols = [
    "funded_amnt_inv", "out_prncp", "out_prncp_inv",
    "total_pymnt", "total_pymnt_inv", "total_rec_prncp",
    "total_rec_int", "total_rec_late_fee", "recoveries",
    "collection_recovery_fee", "last_pymnt_amnt",
    "last_pymnt_d", "last_credit_pull_d", "next_pymnt_d"  # added: post-origination dates, moved here for consistency
]
df = df.drop(columns=[c for c in post_loan_cols if c in df.columns])
 
 
# -----------------------------------------------------------
# SCHEMA DEFINITION
# based on the LendingClub data dictionary
# every column must belong to one of these lists
# -----------------------------------------------------------
 
numeric_cols = [
    "loan_amnt", "funded_amnt",
    "installment", "annual_inc", "dti",
    "delinq_2yrs", "inq_last_6mths",
    "open_acc", "pub_rec", "revol_bal",
    "total_acc", "pub_rec_bankruptcies",
    "tax_liens", "mths_since_last_delinq",
    "mths_since_last_record", "collections_12_mths_ex_med",
    "chargeoff_within_12_mths"
]
 
# these come in as strings like "13.5%" so the % needs stripping before conversion
percent_cols = [
    "int_rate",
    "revol_util"
]
 
# stored as "Jan-14" — not a standard format so the pattern needs to be specified explicitly
date_cols = [
    "issue_d",
    "earliest_cr_line",
]
 
categorical_cols = [
    "term", "grade", "sub_grade",
    "home_ownership", "verification_status", "loan_status",
    "purpose", "zip_code", "addr_state",
    "emp_title", "emp_length"
]
 
 
# -----------------------------------------------------------
# SCHEMA VALIDATION
# catches columns that were missed or don't exist in this dataset
# -----------------------------------------------------------
schema_cols = set(numeric_cols + percent_cols + date_cols + categorical_cols)
df_cols = set(df.columns)
 
missing_in_df = schema_cols - df_cols
missing_in_schema = df_cols - schema_cols
 
if missing_in_df:
    print("In schema but not in data:", missing_in_df)
if missing_in_schema:
    print("In data but not classified:", missing_in_schema)
 
# safety filter — avoids crashes if a column from the schema is missing in this particular file
numeric_cols     = [col for col in numeric_cols     if col in df.columns]
percent_cols     = [col for col in percent_cols     if col in df.columns]
date_cols        = [col for col in date_cols        if col in df.columns]
categorical_cols = [col for col in categorical_cols if col in df.columns]
 
 
# -----------------------------------------------------------
# TYPE CASTING
# -----------------------------------------------------------
 
# errors="coerce" turns anything unparseable into NaN instead of crashing
df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors="coerce")
 
# strip the % sign first, otherwise the conversion fails entirely
for col in percent_cols:
    df[col] = df[col].str.replace("%", "", regex=False)
    df[col] = pd.to_numeric(df[col], errors="coerce")
 
for col in date_cols:
    df[col] = pd.to_datetime(df[col], format="%b-%y", errors="coerce")
 
# category dtype stores repeated strings much more efficiently than plain object
for col in categorical_cols:
    df[col] = df[col].astype("category")
 
 
# -----------------------------------------------------------
# MISSING VALUES
# -----------------------------------------------------------
print("\nMissing values before cleaning:")
print(df.isnull().sum()[df.isnull().sum() > 0])
 
 
# missing here means the event never happened, so 0 is the right assumption
for col in ["collections_12_mths_ex_med", "chargeoff_within_12_mths",
            "tax_liens", "pub_rec_bankruptcies",
            "mths_since_last_delinq", "mths_since_last_record"]:
    df[col] = df[col].fillna(0)
 
# record which rows had missing revol_util before filling — that missingness might carry signal
df["revol_util_missing"] = df["revol_util"].isna().astype(int)
df["revol_util"] = df["revol_util"].fillna(df["revol_util"].median())
 
# categories that are missing are treated as a separate category called "Unknown"
df["emp_title"] = df["emp_title"].cat.add_categories("Unknown").fillna("Unknown")
df["emp_length"] = df["emp_length"].cat.add_categories("Unknown").fillna("Unknown")
 
# -----------------------------------------------------------
# FEATURE ENGINEERING
# -----------------------------------------------------------
 
# 0 income would cause division by zero in the ratios below
df["annual_inc"] = df["annual_inc"].replace(0, np.nan)
 
# measures how stretched the borrower is relative to their income
df["loan_to_income"] = df["loan_amnt"] / df["annual_inc"]
df["installment_ratio"] = df["installment"] / df["annual_inc"]
 
# longer credit history generally signals a more reliable borrower
df["credit_age_years"] = (df["issue_d"] - df["earliest_cr_line"]).dt.days / 365
 

 
# quick binary flags for borrowers who are already in a high risk zone
df["high_dti_flag"] = (df["dti"] > 20).astype(int)
df["high_interest_flag"] = (df["int_rate"] > 15).astype(int)
 
 
# -----------------------------------------------------------
# TARGET VARIABLE
# -----------------------------------------------------------
# 1 = defaulted, 0 = fully paid or still current
df["target_default"] = (df["loan_status"] == "Charged Off").astype(int)
 
 
# -----------------------------------------------------------
# EXPORT TO MYSQL AND CSV
# -----------------------------------------------------------
output_path = Path(__file__).parent
 
DB_PASSWORD = os.environ.get("DB_PASSWORD")
if not DB_PASSWORD:
    raise ValueError("DB_PASSWORD environment variable not set. Run: export DB_PASSWORD=your_password")
 
# create the database if it doesn't exist yet
conn = mysql.connector.connect(host="localhost", user="root", password=DB_PASSWORD)
cursor = conn.cursor()
cursor.execute("CREATE DATABASE IF NOT EXISTS loan_db")
cursor.close()
conn.close()
 
# load the cleaned dataframe into MySQL
engine = create_engine(f"mysql+mysqlconnector://root:{DB_PASSWORD}@localhost/loan_db")
df.to_sql("loans", engine, if_exists="replace", index=False)
print("Data saved to MySQL — loan_db.loans")
 
# CSV export for Tableau and other tools
df.to_csv(output_path / "loans_clean.csv", index=False)
print("Data saved to loans_clean.csv")
 
 
# -----------------------------------------------------------
# SUMMARY
# -----------------------------------------------------------
print(f"\nShape: {df.shape}")
print(f"Default rate: {df['target_default'].mean():.1%}")
print("\nRemaining missing values:")
missing = df.isnull().sum()[df.isnull().sum() > 0]
print(missing if not missing.empty else "None")
 