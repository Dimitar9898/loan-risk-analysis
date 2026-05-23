import pandas as pd
import os
import numpy as np

path = r"C:\Users\dimit\Downloads\loan (1).csv"

df = pd.read_csv(
    path,
    encoding="latin1",
    dtype=str,
    engine="python",
    
    
)

df = df.dropna(axis=1, how="all")  #remove empty columns
df=df.loc[:,df.nunique(dropna=False)>1]  #remove constant columns with 1 unique value (including NaN)


#Schema definition based on LendingClub data dictionary

id_cols = ["id", "member_id", "url"]   #these are identifiers, we will keep as strings but not use for modeling
numeric_cols = [
    "loan_amnt", "funded_amnt", "funded_amnt_inv",
    "installment", "annual_inc", "dti",
    "delinq_2yrs", "inq_last_6mths",
    "open_acc", "pub_rec", "revol_bal",
    "total_acc",
    "out_prncp", "out_prncp_inv",  
    "total_pymnt", "total_pymnt_inv",
    "total_rec_prncp", "total_rec_int",
    "total_rec_late_fee", "recoveries",
    "collection_recovery_fee", "last_pymnt_amnt",
    "collections_12_mths_ex_med",
    "chargeoff_within_12_mths",
    "pub_rec_bankruptcies",
    "tax_liens",
    "mths_since_last_delinq",
    "mths_since_last_record"
]

percent_cols = [   #these are percentages stored as strings with a % sign, we will clean and convert to numeric 
    "int_rate",
    "revol_util"
]

date_cols = [  #these are dates stored as strings, we will convert to datetime
    "issue_d",
    "earliest_cr_line",
    "last_pymnt_d",
    "next_pymnt_d",
    "last_credit_pull_d"
]

categorical_cols = [  #these are categorical variables, we will convert to category dtype
    "term",
    "grade",
    "sub_grade",
    "home_ownership",
    "verification_status",
    "loan_status",
    "purpose",
    "title",
    "zip_code",
    "addr_state",
    "initial_list_status",
    "application_type",
    "emp_title",
    "emp_length",
    "desc"
]

# combine all schema columns
schema_cols = set(
    id_cols +
    numeric_cols +
    percent_cols +
    date_cols +
    categorical_cols
)

# actual dataframe columns
df_cols = set(df.columns)

# 1. columns in schema but NOT in df (invalid / extra)
missing_in_df = schema_cols - df_cols

# 2. columns in df but NOT in schema (you forgot to classify)
missing_in_schema = df_cols - schema_cols



#print("Columns in df but NOT in schema:", missing_in_schema)
categorical_cols = [
    col for col in categorical_cols
    if col in df.columns
]




# -------------------------
# 1. NUMERIC
# -------------------------
df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors="coerce")

# -------------------------
# 2. PERCENTAGE
# -------------------------
for col in percent_cols:
    df[col] = df[col].str.replace("%", "", regex=False)
    df[col] = pd.to_numeric(df[col], errors="coerce")

# -------------------------
# 3. DATES
# -------------------------
for col in date_cols:
    df[col] = pd.to_datetime(df[col], format="%b-%y", errors="coerce")

# -------------------------
# 4. CATEGORICAL
# -------------------------
for col in categorical_cols:
    df[col] = df[col].astype("category")

# -------------------------
# 5. IDS (keep as string)
# -------------------------

# Convert ID columns to string (if they exist in the dataframe)
df[id_cols] = df[id_cols].astype(str)

# FINAL CLEANUP - drop columns we won't use for modeling (IDs, text fields)
df = df.drop(columns=["id", "member_id", "url","title", "desc"])

df["revol_util_missing"] = df["revol_util"].isna().astype(int)   #making a new column to see if missing values in revol_util 
df["revol_util"] = df["revol_util"].fillna(df["revol_util"].median())  #fill missing values in revol_util with median (could also use mean or a model-based imputation)


df["mths_since_last_delinq"] = df["mths_since_last_delinq"].fillna(0) #assuming missing means no delinquencies, so we fill with 0
df["mths_since_last_record"] = df["mths_since_last_record"].fillna(0) #assuming missing means no records, so we fill with 0


#ADDING NEW FEATURES
df["emp_title"] = df["emp_title"].astype("object").fillna("Unknown") #
df["emp_length"] = df["emp_length"].astype("object").fillna("Unknown")

df["annual_inc"] = df["annual_inc"].replace(0, np.nan) #replace 0 with NaN in annual_inc to avoid division by zero in new features
df["loan_to_income"] = df["loan_amnt"] / df["annual_inc"]
df["installment_ratio"] = df["installment"] / df["annual_inc"]

df["credit_age_years"] = (df["issue_d"] - df["earliest_cr_line"]).dt.days / 365
df["loan_duration_days"] = (df["last_pymnt_d"] - df["issue_d"]).dt.days

df["high_dti_flag"] = (df["dti"] > 20).astype(int)
df["high_interest_flag"] = (df["int_rate"] > 15).astype(int)


df["target_default"] = df["loan_status"].isin(["Charged Off"]).astype(int)  #checks for bad loans with 1 being charged off and 0 being good loans (fully paid or current)

df["loan_to_income"] = (
    df["loan_amnt"] / df["annual_inc"]
)

df["installment_ratio"] = (
    df["installment"] / df["annual_inc"]
)

df["credit_age_years"] = (
    (df["issue_d"] - df["earliest_cr_line"]).dt.days / 365
)

df["high_dti_flag"] = (
    (df["dti"] > 20).astype(int)
)

