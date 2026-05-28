import pandas as pd
import numpy as np
from pathlib import Path


path = Path.home() / "Downloads" / "loan (1).csv"

df = pd.read_csv(
    path,
    encoding="latin1",
    dtype=str,
    engine="python",
    
    
)

df = df.dropna(axis=1, how="all")  #remove empty columns
df=df.loc[:,df.nunique(dropna=False)>1]  #remove constant columns with 1 unique value (including NaN)
df = df.drop(columns=[c for c in ["id", "member_id", "url", "title", "desc"] if c in df.columns])

#Schema definition based on LendingClub data dictionary

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
    "zip_code",
    "addr_state",
    "initial_list_status",
    "application_type",
    "emp_title",
    "emp_length"
]

# combine all schema columns
schema_cols = set(
    numeric_cols +
    percent_cols +
    date_cols +
    categorical_cols
)

# actual dataframe columns
df_cols = set(df.columns)

# 1. columns in schema but NOT in df (invalid / extra)
missing_in_df = schema_cols - df_cols

# 2. columns in df but NOT in schema 
missing_in_schema = df_cols - schema_cols

if missing_in_schema:
    print("Unclassified columns:", missing_in_schema)


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

df["target_default"] = (df["loan_status"] == "Charged Off").astype(int)
# 1 = defaulted, 0 = fully paid or current

print(df["target_default"] .value_counts())   

print(f"Shape: {df.shape}")
print(f"Default rate: {df['target_default'].mean():.1%}")