import pandas as pd

def get_data_overview(df):
    overview = {
        "rows": df.shape[0],
        "columns": df.shape[1],
        "column_info": df.dtypes,
        "missing_values": df.isnull().sum(),
        "statistics": df.describe(include="all")
    }

    return overview

def validate_required_columns(df, required_columns):
    missing_columns = []

    for column in required_columns:
        if column not in df.columns:
            missing_columns.append(column)

    return missing_columns

def validate_data_types(df):
    errors = []

    # Check numeric columns
    numeric_columns = ["Sales", "Profit", "Quantity"]

    for column in numeric_columns:
        if column in df.columns:
            converted = pd.to_numeric(df[column], errors="coerce")

            if converted.isnull().any():
                errors.append(f"{column} contains non-numeric values.")

    # Check date column
    if "OrderDate" in df.columns:
        converted_dates = pd.to_datetime(df["OrderDate"], errors="coerce")

        if converted_dates.isnull().any():
            errors.append("OrderDate contains invalid date values.")

    return errors


def clean_data(df):
    df = df.copy()

    numeric_columns = ["Sales", "Profit", "Quantity"]

    for column in numeric_columns:
        if column in df.columns:
            df[column] = pd.to_numeric(df[column])

    if "OrderDate" in df.columns:
        df["OrderDate"] = pd.to_datetime(df["OrderDate"])

    return df